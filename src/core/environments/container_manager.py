import docker
import uuid
import logging
import time
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
import json
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil
import signal
import os
import websockets
from prometheus_client import Counter, Gauge, Histogram
import threading
import queue
import select
import networkx as nx
from dataclasses import dataclass
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
container_creation_counter = Counter('container_creation_total', 'Total number of containers created')
container_execution_counter = Counter('container_execution_total', 'Total number of code executions')
container_error_counter = Counter('container_error_total', 'Total number of container errors')
container_memory_usage = Gauge('container_memory_usage_bytes', 'Container memory usage in bytes')
container_cpu_usage = Gauge('container_cpu_usage_percent', 'Container CPU usage percentage')
container_execution_time = Histogram('container_execution_seconds', 'Container execution time in seconds')

@dataclass
class ContainerDependency:
    """Container dependency configuration."""
    name: str
    image: str
    environment: Dict[str, str] = None
    ports: Dict[str, str] = None
    volumes: Dict[str, str] = None
    health_check: Dict[str, Any] = None
    depends_on: List[str] = None

class ContainerNetwork:
    """Manages container networking and dependencies."""
    def __init__(self):
        self.network = nx.DiGraph()
        self.containers: Dict[str, ContainerDependency] = {}
        self.docker_network = None

    def add_container(self, container: ContainerDependency):
        """Add a container to the network."""
        self.containers[container.name] = container
        self.network.add_node(container.name)
        
        if container.depends_on:
            for dep in container.depends_on:
                self.network.add_edge(dep, container.name)

    def get_start_order(self) -> List[str]:
        """Get the order in which containers should be started."""
        try:
            return list(nx.topological_sort(self.network))
        except nx.NetworkXUnfeasible:
            raise ValueError("Circular dependency detected")

    async def create_network(self, client: docker.DockerClient):
        """Create a Docker network for the containers."""
        self.docker_network = client.networks.create(
            name=f"execution-network-{uuid.uuid4()}",
            driver="bridge"
        )

    async def remove_network(self):
        """Remove the Docker network."""
        if self.docker_network:
            self.docker_network.remove()

class ContainerConfig:
    """Configuration for container creation and execution."""
    def __init__(
        self,
        language: str,
        memory_limit: str = "512m",
        cpu_period: int = 100000,
        cpu_quota: int = 50000,  # 0.5 CPU
        network_disabled: bool = True,
        timeout: int = 30,
        max_output_size: int = 1024 * 1024,  # 1MB
        max_log_size: int = 10 * 1024 * 1024,  # 10MB
        log_retention_days: int = 7,
        read_only: bool = True,  # Mount filesystem as read-only
        no_new_privileges: bool = True,  # Prevent privilege escalation
        security_opt: List[str] = None,  # Additional security options
        ulimits: Dict[str, int] = None,  # Resource limits
        cap_drop: List[str] = None,  # Drop capabilities
        sysctls: Dict[str, str] = None  # System controls
    ):
        self.language = language
        self.memory_limit = memory_limit
        self.cpu_period = cpu_period
        self.cpu_quota = cpu_quota
        self.network_disabled = network_disabled
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.max_log_size = max_log_size
        self.log_retention_days = log_retention_days
        self.read_only = read_only
        self.no_new_privileges = no_new_privileges
        self.security_opt = security_opt or [
            "no-new-privileges",
            "no-sysrq",
            "no-ptrace",
            "no-exec",
            "no-ipc",
            "no-uts",
            "no-mount",
            "no-pid",
            "no-net",
            "no-cgroup"
        ]
        self.ulimits = ulimits or {
            "nofile": 100,  # Limit open files
            "nproc": 50,    # Limit processes
            "core": 0       # Disable core dumps
        }
        self.cap_drop = cap_drop or [
            "ALL",  # Drop all capabilities
            "CHOWN",
            "DAC_OVERRIDE",
            "FOWNER",
            "MKNOD",
            "NET_RAW",
            "SETGID",
            "SETUID",
            "SETFCAP",
            "SETPCAP",
            "NET_BIND_SERVICE",
            "SYS_CHROOT",
            "SYS_MODULE",
            "SYS_RAWIO",
            "SYS_RESOURCE",
            "SYS_TIME",
            "SYS_TTY_CONFIG",
            "SYSLOG",
            "WAKE_ALARM"
        ]
        self.sysctls = sysctls or {
            "net.ipv4.ip_forward": "0",
            "net.ipv4.conf.all.send_redirects": "0",
            "net.ipv4.conf.default.send_redirects": "0",
            "net.ipv4.conf.all.accept_source_route": "0",
            "net.ipv4.conf.default.accept_source_route": "0",
            "net.ipv4.conf.all.accept_redirects": "0",
            "net.ipv4.conf.default.accept_redirects": "0",
            "net.ipv4.conf.all.secure_redirects": "0",
            "net.ipv4.conf.default.secure_redirects": "0",
            "net.ipv4.conf.all.log_martians": "1",
            "net.ipv4.conf.default.log_martians": "1",
            "net.ipv4.icmp_echo_ignore_broadcasts": "1",
            "net.ipv4.icmp_ignore_bogus_error_responses": "1",
            "net.ipv4.conf.all.rp_filter": "1",
            "net.ipv4.conf.default.rp_filter": "1",
            "net.ipv4.tcp_syncookies": "1",
            "net.ipv4.tcp_rfc1337": "1",
            "net.ipv4.conf.all.accept_redirects": "0",
            "net.ipv4.conf.default.accept_redirects": "0",
            "net.ipv4.conf.all.secure_redirects": "0",
            "net.ipv4.conf.default.secure_redirects": "0",
            "net.ipv4.conf.all.send_redirects": "0",
            "net.ipv4.conf.default.send_redirects": "0",
            "net.ipv4.conf.all.accept_source_route": "0",
            "net.ipv4.conf.default.accept_source_route": "0",
            "net.ipv4.conf.all.log_martians": "1",
            "net.ipv4.conf.default.log_martians": "1",
            "net.ipv4.icmp_echo_ignore_broadcasts": "1",
            "net.ipv4.icmp_ignore_bogus_error_responses": "1",
            "net.ipv4.conf.all.rp_filter": "1",
            "net.ipv4.conf.default.rp_filter": "1",
            "net.ipv4.tcp_syncookies": "1",
            "net.ipv4.tcp_rfc1337": "1"
        }

class ExecutionResult:
    """Result of code execution in a container."""
    def __init__(
        self,
        execution_id: str,
        status: str,
        output: str,
        error: Optional[str] = None,
        exit_code: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        resource_usage: Optional[Dict[str, Any]] = None
    ):
        self.execution_id = execution_id
        self.status = status
        self.output = output
        self.error = error
        self.exit_code = exit_code
        self.start_time = start_time or datetime.utcnow()
        self.end_time = end_time
        self.resource_usage = resource_usage or {}

class InteractiveSession:
    """Manages an interactive code execution session."""
    def __init__(self, container_id: str, websocket: websockets.WebSocketServerProtocol):
        self.container_id = container_id
        self.websocket = websocket
        self.stdin_queue = queue.Queue()
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.running = True
        self.threads = []

    async def start(self):
        """Start the interactive session."""
        try:
            # Start input/output threads
            self.threads = [
                threading.Thread(target=self._handle_stdin),
                threading.Thread(target=self._handle_stdout),
                threading.Thread(target=self._handle_stderr)
            ]
            for thread in self.threads:
                thread.daemon = True
                thread.start()

            # Start WebSocket message handler
            await self._handle_websocket_messages()
        except Exception as e:
            logger.error(f"Error in interactive session: {str(e)}")
            await self.stop()

    def _handle_stdin(self):
        """Handle stdin from WebSocket to container."""
        while self.running:
            try:
                data = self.stdin_queue.get(timeout=1)
                if data is None:
                    break
                # Send data to container stdin
                container = self.client.containers.get(self.container_id)
                container.exec_run(f"echo '{data}'", stdin=True)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error handling stdin: {str(e)}")
                break

    def _handle_stdout(self):
        """Handle stdout from container to WebSocket."""
        while self.running:
            try:
                container = self.client.containers.get(self.container_id)
                for log in container.logs(stream=True, stdout=True, stderr=False):
                    if not self.running:
                        break
                    self.stdout_queue.put(log.decode())
            except Exception as e:
                logger.error(f"Error handling stdout: {str(e)}")
                break

    def _handle_stderr(self):
        """Handle stderr from container to WebSocket."""
        while self.running:
            try:
                container = self.client.containers.get(self.container_id)
                for log in container.logs(stream=True, stdout=False, stderr=True):
                    if not self.running:
                        break
                    self.stderr_queue.put(log.decode())
            except Exception as e:
                logger.error(f"Error handling stderr: {str(e)}")
                break

    async def _handle_websocket_messages(self):
        """Handle WebSocket messages."""
        try:
            while self.running:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if data["type"] == "input":
                    self.stdin_queue.put(data["content"])
                elif data["type"] == "stop":
                    await self.stop()
                    break
        except websockets.exceptions.ConnectionClosed:
            await self.stop()
        except Exception as e:
            logger.error(f"Error handling WebSocket messages: {str(e)}")
            await self.stop()

    async def stop(self):
        """Stop the interactive session."""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=1)
        await self.websocket.close()

class ContainerManager:
    """Manages container creation, execution, and cleanup."""
    
    def __init__(self, base_path: str = "/tmp/containers"):
        self.client = docker.from_env()
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.executions: Dict[str, ExecutionResult] = {}
        self.interactive_sessions: Dict[str, InteractiveSession] = {}
        self.cleanup_task = None
        self.monitoring_task = None
        self.network = ContainerNetwork()
        self._start_cleanup_task()
        self._start_monitoring_task()

    def _start_cleanup_task(self):
        """Start the background cleanup task."""
        async def cleanup_loop():
            while True:
                await self.cleanup_old_executions()
                await asyncio.sleep(3600)  # Run every hour

        self.cleanup_task = asyncio.create_task(cleanup_loop())

    def _start_monitoring_task(self):
        """Start the container monitoring task."""
        async def monitoring_loop():
            while True:
                await self._monitor_containers()
                await asyncio.sleep(5)  # Check every 5 seconds

        self.monitoring_task = asyncio.create_task(monitoring_loop())

    async def cleanup_old_executions(self):
        """Clean up old execution results and containers."""
        try:
            current_time = datetime.utcnow()
            for execution_id, result in list(self.executions.items()):
                if (current_time - result.start_time).days > result.log_retention_days:
                    await self.cleanup_execution(execution_id)
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def cleanup_execution(self, execution_id: str):
        """Clean up a specific execution and its dependencies."""
        try:
            # Stop and remove all containers in the network
            for container_name in self.network.containers:
                try:
                    container = self.client.containers.get(container_name)
                    container.stop()
                    container.remove()
                except docker.errors.NotFound:
                    pass
                except Exception as e:
                    logger.error(f"Error cleaning up container {container_name}: {str(e)}")
            
            # Remove the network
            await self.network.remove_network()
            
            # Remove execution directory
            execution_dir = self.base_path / execution_id
            if execution_dir.exists():
                shutil.rmtree(execution_dir)
            
            # Remove from executions dict
            self.executions.pop(execution_id, None)
            
        except Exception as e:
            logger.error(f"Error cleaning up execution {execution_id}: {str(e)}")
            raise

    def _get_language_template(self, language: str) -> str:
        """Get language-specific Dockerfile template."""
        templates = {
            "python": """
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER nobody
CMD ["python", "main.py"]
""",
            "javascript": """
FROM node:16-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
USER node
CMD ["node", "index.js"]
""",
            "java": """
FROM openjdk:11-slim
WORKDIR /app
COPY pom.xml .
RUN apt-get update && apt-get install -y maven \
    && rm -rf /var/lib/apt/lists/*
COPY src ./src
RUN mvn package -DskipTests
USER nobody
CMD ["java", "-jar", "target/app.jar"]
""",
            "go": """
FROM golang:1.16-alpine
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o main .
USER nobody
CMD ["./main"]
""",
            "ruby": """
FROM ruby:2.7-slim
WORKDIR /app
COPY Gemfile* ./
RUN bundle install
COPY . .
USER nobody
CMD ["ruby", "main.rb"]
""",
            "rust": """
FROM rust:1.54-slim
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
RUN cargo build --release
COPY src ./src
USER nobody
CMD ["./target/release/app"]
""",
            "csharp": """
FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build
WORKDIR /app
COPY *.csproj ./
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o out
FROM mcr.microsoft.com/dotnet/runtime:5.0
WORKDIR /app
COPY --from=build /app/out ./
USER nobody
CMD ["dotnet", "app.dll"]
""",
            "php": """
FROM php:7.4-cli
WORKDIR /app
COPY composer.json composer.lock ./
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer install --no-dev --no-scripts
COPY . .
USER nobody
CMD ["php", "main.php"]
""",
            "swift": """
FROM swift:5.5
WORKDIR /app
COPY Package.swift ./
RUN swift package resolve
COPY Sources ./Sources
USER nobody
CMD ["swift", "run"]
""",
            "kotlin": """
FROM openjdk:11-slim
WORKDIR /app
COPY build.gradle.kts settings.gradle.kts ./
RUN apt-get update && apt-get install -y gradle \
    && rm -rf /var/lib/apt/lists/*
COPY src ./src
RUN gradle build --no-daemon
USER nobody
CMD ["java", "-jar", "build/libs/app.jar"]
""",
            "scala": """
FROM openjdk:11-slim
WORKDIR /app
COPY build.sbt project/ ./
RUN apt-get update && apt-get install -y sbt \
    && rm -rf /var/lib/apt/lists/*
COPY src ./src
RUN sbt assembly
USER nobody
CMD ["java", "-jar", "target/scala-2.13/app-assembly-0.1.0.jar"]
""",
            "haskell": """
FROM haskell:8
WORKDIR /app
COPY *.cabal ./
RUN cabal update
COPY . .
RUN cabal build
USER nobody
CMD ["./dist/build/app/app"]
""",
            "lua": """
FROM lua:5.4
WORKDIR /app
COPY rockspec ./
RUN luarocks install --local --server https://luarocks.org/dev app-0.1.0-1.rockspec
COPY . .
USER nobody
CMD ["lua", "main.lua"]
""",
            "perl": """
FROM perl:5.32
WORKDIR /app
COPY cpanfile ./
RUN cpanm --installdeps .
COPY . .
USER nobody
CMD ["perl", "main.pl"]
""",
            "shell": """
FROM ubuntu:20.04
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY . .
USER nobody
CMD ["bash", "main.sh"]
""",
            "typescript": """
FROM node:16-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY tsconfig.json ./
COPY src ./src
RUN npm run build
USER node
CMD ["node", "dist/main.js"]
""",
            "dart": """
FROM dart:2.19
WORKDIR /app
COPY pubspec.yaml ./
RUN dart pub get
COPY . .
USER nobody
CMD ["dart", "bin/main.dart"]
""",
            "julia": """
FROM julia:1.8
WORKDIR /app
COPY Project.toml ./
RUN julia -e 'using Pkg; Pkg.instantiate()'
COPY . .
USER nobody
CMD ["julia", "src/main.jl"]
""",
            "r": """
FROM r-base:latest
WORKDIR /app
COPY install.R ./
RUN Rscript install.R
COPY . .
USER nobody
CMD ["Rscript", "main.R"]
""",
            "matlab": """
FROM mathworks/matlab:r2021b
WORKDIR /app
COPY . .
USER nobody
CMD ["matlab", "-batch", "main"]
""",
            "fortran": """
FROM gcc:latest
WORKDIR /app
COPY . .
RUN gfortran -o main main.f90
USER nobody
CMD ["./main"]
""",
            "cobol": """
FROM opencobol/gnucobol:latest
WORKDIR /app
COPY . .
RUN cobc -x main.cbl
USER nobody
CMD ["./main"]
""",
            "pascal": """
FROM fpc/compiler:latest
WORKDIR /app
COPY . .
RUN fpc main.pas
USER nobody
CMD ["./main"]
""",
            "ada": """
FROM gnat:latest
WORKDIR /app
COPY . .
RUN gnatmake main.adb
USER nobody
CMD ["./main"]
""",
            "prolog": """
FROM swipl:latest
WORKDIR /app
COPY . .
USER nobody
CMD ["swipl", "main.pl"]
""",
            "erlang": """
FROM erlang:latest
WORKDIR /app
COPY rebar.config ./
RUN rebar3 get-deps
COPY . .
RUN rebar3 compile
USER nobody
CMD ["erl", "-noshell", "-s", "main", "start"]
""",
            "elixir": """
FROM elixir:latest
WORKDIR /app
COPY mix.exs mix.lock ./
RUN mix deps.get
COPY . .
RUN mix compile
USER nobody
CMD ["mix", "run"]
""",
            "clojure": """
FROM clojure:latest
WORKDIR /app
COPY project.clj ./
RUN lein deps
COPY . .
RUN lein uberjar
USER nobody
CMD ["java", "-jar", "target/uberjar/app.jar"]
""",
            "fsharp": """
FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build
WORKDIR /app
COPY *.fsproj ./
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o out
FROM mcr.microsoft.com/dotnet/runtime:5.0
WORKDIR /app
COPY --from=build /app/out ./
USER nobody
CMD ["dotnet", "app.dll"]
""",
            "ocaml": """
FROM ocaml/opam:latest
WORKDIR /app
COPY *.opam ./
RUN opam install . --deps-only
COPY . .
RUN opam exec -- dune build
USER nobody
CMD ["./_build/default/bin/main.exe"]
""",
            "racket": """
FROM racket/racket:latest
WORKDIR /app
COPY info.rkt ./
RUN raco pkg install --deps search-auto
COPY . .
USER nobody
CMD ["racket", "main.rkt"]
""",
            "smalltalk": """
FROM pharo/smalltalk:latest
WORKDIR /app
COPY . .
USER nobody
CMD ["pharo", "main.st"]
""",
            "lisp": """
FROM sbcl:latest
WORKDIR /app
COPY . .
RUN sbcl --load main.lisp --eval "(sb-ext:save-lisp-and-die \"main\" :executable t)"
USER nobody
CMD ["./main"]
""",
            "scheme": """
FROM guile:latest
WORKDIR /app
COPY . .
USER nobody
CMD ["guile", "main.scm"]
""",
            "haxe": """
FROM haxe:latest
WORKDIR /app
COPY . .
RUN haxe --main Main --interp
USER nobody
CMD ["haxe", "--main", "Main", "--interp"]
""",
            "nim": """
FROM nimlang/nim:latest
WORKDIR /app
COPY . .
RUN nim c main.nim
USER nobody
CMD ["./main"]
""",
            "crystal": """
FROM crystallang/crystal:latest
WORKDIR /app
COPY shard.yml ./
RUN shards install
COPY . .
RUN crystal build main.cr
USER nobody
CMD ["./main"]
""",
            "v": """
FROM vlang/v:latest
WORKDIR /app
COPY . .
RUN v main.v
USER nobody
CMD ["./main"]
""",
            "zig": """
FROM zig:latest
WORKDIR /app
COPY . .
RUN zig build-exe main.zig
USER nobody
CMD ["./main"]
""",
            "odin": """
FROM odin:latest
WORKDIR /app
COPY . .
RUN odin build main.odin
USER nobody
CMD ["./main"]
""",
            "cuda": """
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY . .
RUN nvcc -o main main.cu
USER nobody
CMD ["./main"]
""",
            "opencl": """
FROM opencl:latest
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    opencl-headers \
    ocl-icd-opencl-dev \
    && rm -rf /var/lib/apt/lists/*
COPY . .
RUN gcc -o main main.c -lOpenCL
USER nobody
CMD ["./main"]
""",
            "webassembly": """
FROM emscripten/emsdk:latest
WORKDIR /app
COPY . .
RUN emcc main.c -o main.js
USER nobody
CMD ["node", "main.js"]
""",
            "solidity": """
FROM ethereum/solc:latest
WORKDIR /app
COPY . .
RUN solc --bin main.sol
USER nobody
CMD ["solc", "--bin", "main.sol"]
""",
            "move": """
FROM move-language/move-cli:latest
WORKDIR /app
COPY . .
RUN move build
USER nobody
CMD ["move", "run"]
""",
            "vyper": """
FROM vyperlang/vyper:latest
WORKDIR /app
COPY . .
RUN vyper main.vy
USER nobody
CMD ["vyper", "main.vy"]
""",
            "teal": """
FROM algorand/teal:latest
WORKDIR /app
COPY . .
RUN teal main.teal
USER nobody
CMD ["teal", "main.teal"]
"""
        }
        return templates.get(language.lower(), templates["python"])

    def _create_dockerfile(self, execution_id: str, config: ContainerConfig) -> str:
        """Create a Dockerfile for the container."""
        template = self._get_language_template(config.language)
        dockerfile_content = f"""
FROM {template['base_image']}

WORKDIR /app

# Install dependencies
{" ".join(template['setup_commands'])}

# Copy code
COPY code.* /app/

# Set resource limits and security options
ENV PYTHONUNBUFFERED=1
ENV NODE_OPTIONS="--max-old-space-size={config.memory_limit}"
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Create non-root user
RUN useradd -m -r -s /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

# Run the code
CMD {template['run_command']}
"""
        dockerfile_path = self.base_path / execution_id / "Dockerfile"
        dockerfile_path.parent.mkdir(parents=True, exist_ok=True)
        dockerfile_path.write_text(dockerfile_content)
        return str(dockerfile_path)

    async def create_container_with_dependencies(
        self,
        code: str,
        config: ContainerConfig,
        dependencies: List[ContainerDependency] = None
    ) -> str:
        """Create a container with its dependencies."""
        execution_id = str(uuid.uuid4())
        
        # Create network for dependencies
        await self.network.create_network(self.client)
        
        try:
            # Add dependencies to network
            if dependencies:
                for dep in dependencies:
                    self.network.add_container(dep)
            
            # Add main container
            main_container = ContainerDependency(
                name=execution_id,
                image=f"execution-{execution_id}",
                depends_on=[dep.name for dep in (dependencies or [])]
            )
            self.network.add_container(main_container)
            
            # Start containers in dependency order
            start_order = self.network.get_start_order()
            for container_name in start_order:
                container = self.network.containers[container_name]
                
                if container_name == execution_id:
                    # Create and start main container
                    await self.create_container(code, config)
                else:
                    # Start dependency container
                    await self._start_dependency_container(container)
            
            return execution_id
        except Exception as e:
            await self.network.remove_network()
            raise

    async def _start_dependency_container(self, container: ContainerDependency):
        """Start a dependency container."""
        try:
            # Pull image if needed
            self.client.images.pull(container.image)
            
            # Create container
            docker_container = self.client.containers.create(
                container.image,
                name=container.name,
                network=self.network.docker_network.name,
                environment=container.environment,
                ports=container.ports,
                volumes=container.volumes,
                healthcheck=container.health_check,
                detach=True
            )
            
            # Start container
            docker_container.start()
            
            # Wait for health check if specified
            if container.health_check:
                await self._wait_for_health_check(docker_container)
                
        except Exception as e:
            logger.error(f"Error starting dependency container {container.name}: {str(e)}")
            raise

    async def _wait_for_health_check(self, container: docker.Container):
        """Wait for container health check to pass."""
        health_check = container.attrs["Config"]["Healthcheck"]
        interval = health_check.get("Interval", 30) / 1000000000  # Convert to seconds
        timeout = health_check.get("Timeout", 30) / 1000000000
        retries = health_check.get("Retries", 3)
        
        for _ in range(retries):
            health = container.health()
            if health["Status"] == "healthy":
                return
            await asyncio.sleep(interval)
        
        raise TimeoutError(f"Container {container.name} failed health check")

    async def create_container(self, code: str, config: ContainerConfig) -> str:
        """Create a container for code execution."""
        execution_id = str(uuid.uuid4())
        execution_dir = self.base_path / execution_id
        execution_dir.mkdir(parents=True, exist_ok=True)

        # Write code to file
        code_file = execution_dir / f"code.{config.language}"
        code_file.write_text(code)

        # Create Dockerfile
        dockerfile_path = self._create_dockerfile(execution_id, config)

        try:
            # Build image
            image, _ = self.client.images.build(
                path=str(execution_dir),
                dockerfile=str(dockerfile_path),
                tag=f"execution-{execution_id}",
                rm=True
            )

            # Create container with security options
            container = self.client.containers.create(
                image.id,
                name=execution_id,
                mem_limit=config.memory_limit,
                cpu_period=config.cpu_period,
                cpu_quota=config.cpu_quota,
                network_disabled=config.network_disabled,
                read_only=config.read_only,
                security_opt=config.security_opt,
                ulimits=config.ulimits,
                cap_drop=config.cap_drop,
                sysctls=config.sysctls,
                detach=True
            )

            return execution_id
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            await self.cleanup_execution(execution_id)
            raise

    async def _monitor_containers(self):
        """Monitor container health and resource usage."""
        try:
            for container_id in list(self.executions.keys()):
                try:
                    container = self.client.containers.get(container_id)
                    stats = container.stats(stream=False)
                    
                    # Update Prometheus metrics
                    container_memory_usage.labels(container_id=container_id).set(
                        stats["memory_stats"]["usage"]
                    )
                    container_cpu_usage.labels(container_id=container_id).set(
                        stats["cpu_stats"]["cpu_usage"]["total_usage"] / 1000000
                    )
                    
                    # Check container health
                    if container.status != "running":
                        logger.warning(f"Container {container_id} is not running: {container.status}")
                        await self.cleanup_execution(container_id)
                except docker.errors.NotFound:
                    await self.cleanup_execution(container_id)
                except Exception as e:
                    logger.error(f"Error monitoring container {container_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")

    async def start_interactive_session(
        self,
        container_id: str,
        websocket: websockets.WebSocketServerProtocol
    ):
        """Start an interactive code execution session."""
        session = InteractiveSession(container_id, websocket)
        self.interactive_sessions[container_id] = session
        await session.start()

    async def stop_interactive_session(self, container_id: str):
        """Stop an interactive code execution session."""
        if container_id in self.interactive_sessions:
            session = self.interactive_sessions.pop(container_id)
            await session.stop()

    async def execute_code(self, execution_id: str, config: ContainerConfig) -> ExecutionResult:
        """Execute code in the container and capture output."""
        try:
            container = self.client.containers.get(execution_id)
            
            # Start container
            container.start()
            start_time = datetime.utcnow()
            
            # Increment metrics
            container_creation_counter.inc()
            container_execution_counter.inc()

            # Execute with timeout
            try:
                with container_execution_time.time():
                    output = container.exec_run(
                        config._get_language_template(config.language)["run_command"],
                        timeout=config.timeout
                    )
            except docker.errors.ExecTimeout:
                container.kill()
                container_error_counter.inc()
                raise TimeoutError(f"Execution timed out after {config.timeout} seconds")

            # Get container stats
            stats = container.stats(stream=False)
            resource_usage = {
                "cpu_usage": stats["cpu_stats"]["cpu_usage"]["total_usage"],
                "memory_usage": stats["memory_stats"]["usage"],
                "network_rx": stats["networks"]["eth0"]["rx_bytes"],
                "network_tx": stats["networks"]["eth0"]["tx_bytes"]
            }

            # Create result
            result = ExecutionResult(
                execution_id=execution_id,
                status="completed",
                output=output.output.decode()[:config.max_output_size],
                exit_code=output.exit_code,
                start_time=start_time,
                end_time=datetime.utcnow(),
                resource_usage=resource_usage
            )

            # Store result
            self.executions[execution_id] = result

            return result
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}")
            container_error_counter.inc()
            result = ExecutionResult(
                execution_id=execution_id,
                status="failed",
                output="",
                error=str(e),
                start_time=start_time,
                end_time=datetime.utcnow()
            )
            self.executions[execution_id] = result
            raise

    def get_execution_status(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get the status of a code execution."""
        return self.executions.get(execution_id)

    async def stop_execution(self, execution_id: str):
        """Stop a running execution."""
        try:
            container = self.client.containers.get(execution_id)
            container.kill()
            await self.cleanup_execution(execution_id)
        except docker.errors.NotFound:
            pass
        except Exception as e:
            logger.error(f"Error stopping execution: {str(e)}")
            raise

    def __del__(self):
        """Cleanup when the manager is destroyed."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.monitoring_task:
            self.monitoring_task.cancel()
        try:
            self.cleanup_task.result()
            self.monitoring_task.result()
        except asyncio.CancelledError:
            pass 