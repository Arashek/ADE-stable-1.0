from typing import Dict, List, Optional, Any
import logging
import os
import subprocess
import json
import re
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class DockerBuilder:
    """
    Utility class for building and managing Docker containers
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def check_docker_available(self) -> bool:
        """
        Check if Docker is available on the system
        
        Returns:
            True if Docker is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"Docker not available: {str(e)}")
            return False
    
    def build_image(
        self, 
        project_path: str, 
        image_name: str, 
        tag: str = "latest",
        dockerfile_path: Optional[str] = None,
        build_args: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Build a Docker image from a project
        
        Args:
            project_path: Path to the project
            image_name: Name for the Docker image
            tag: Tag for the Docker image
            dockerfile_path: Path to the Dockerfile (if not in project root)
            build_args: Build arguments for Docker
            
        Returns:
            Dictionary with build results
        """
        self.logger.info(f"Building Docker image {image_name}:{tag}")
        
        if not os.path.exists(project_path):
            return {"error": f"Project path does not exist: {project_path}"}
        
        if not self.check_docker_available():
            return {"error": "Docker is not available"}
        
        result = {
            "image_name": image_name,
            "tag": tag,
            "project_path": project_path,
            "success": False
        }
        
        try:
            # Prepare build command
            cmd = ["docker", "build"]
            
            # Add tag
            cmd.extend(["-t", f"{image_name}:{tag}"])
            
            # Add build args if provided
            if build_args:
                for key, value in build_args.items():
                    cmd.extend(["--build-arg", f"{key}={value}"])
            
            # Add Dockerfile path if provided
            if dockerfile_path:
                cmd.extend(["-f", dockerfile_path])
            
            # Add project path
            cmd.append(project_path)
            
            # Run the build command
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            
            if process.returncode == 0:
                result["success"] = True
                result["image_id"] = self._extract_image_id(process.stdout)
            else:
                result["error"] = f"Docker build failed with exit code {process.returncode}"
                
        except Exception as e:
            self.logger.error(f"Error building Docker image: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def run_container(
        self, 
        image_name: str, 
        tag: str = "latest", 
        ports: Optional[List[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[List[str]] = None,
        name: Optional[str] = None,
        detach: bool = True
    ) -> Dict[str, Any]:
        """
        Run a Docker container
        
        Args:
            image_name: Name of the Docker image
            tag: Tag of the Docker image
            ports: List of port mappings (e.g. ["8000:8000"])
            environment: Environment variables
            volumes: Volume mappings
            name: Container name
            detach: Run in detached mode
            
        Returns:
            Dictionary with container results
        """
        self.logger.info(f"Running Docker container from {image_name}:{tag}")
        
        if not self.check_docker_available():
            return {"error": "Docker is not available"}
        
        result = {
            "image_name": image_name,
            "tag": tag,
            "success": False
        }
        
        try:
            # Prepare run command
            cmd = ["docker", "run"]
            
            # Add name if provided
            if name:
                cmd.extend(["--name", name])
                result["container_name"] = name
            
            # Add detach flag if true
            if detach:
                cmd.append("-d")
            
            # Add ports if provided
            if ports:
                for port in ports:
                    cmd.extend(["-p", port])
            
            # Add environment variables if provided
            if environment:
                for key, value in environment.items():
                    cmd.extend(["-e", f"{key}={value}"])
            
            # Add volumes if provided
            if volumes:
                for volume in volumes:
                    cmd.extend(["-v", volume])
            
            # Add image name and tag
            cmd.append(f"{image_name}:{tag}")
            
            # Run the container
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            
            if process.returncode == 0:
                result["success"] = True
                # Extract container ID from stdout (it's usually just the ID)
                result["container_id"] = process.stdout.strip()
                
                # Get container details
                if detach and result["container_id"]:
                    container_details = self.inspect_container(result["container_id"])
                    if "error" not in container_details:
                        result["container_details"] = container_details
            else:
                result["error"] = f"Docker run failed with exit code {process.returncode}"
                
        except Exception as e:
            self.logger.error(f"Error running Docker container: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def inspect_container(self, container_id: str) -> Dict[str, Any]:
        """
        Inspect a Docker container
        
        Args:
            container_id: ID of the container
            
        Returns:
            Dictionary with container details
        """
        try:
            cmd = ["docker", "inspect", container_id]
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if process.returncode == 0:
                try:
                    details = json.loads(process.stdout)
                    if details and isinstance(details, list):
                        return details[0]
                    return details
                except json.JSONDecodeError:
                    return {"error": "Failed to parse container details"}
            else:
                return {"error": f"Failed to inspect container: {process.stderr}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def stop_container(self, container_id: str) -> Dict[str, Any]:
        """
        Stop a Docker container
        
        Args:
            container_id: ID of the container
            
        Returns:
            Dictionary with stop results
        """
        self.logger.info(f"Stopping Docker container {container_id}")
        
        if not self.check_docker_available():
            return {"error": "Docker is not available"}
        
        result = {
            "container_id": container_id,
            "success": False
        }
        
        try:
            cmd = ["docker", "stop", container_id]
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            
            if process.returncode == 0:
                result["success"] = True
            else:
                result["error"] = f"Docker stop failed with exit code {process.returncode}"
                
        except Exception as e:
            self.logger.error(f"Error stopping Docker container: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def generate_dockerfile(
        self, 
        project_path: str, 
        app_type: str, 
        base_image: Optional[str] = None,
        expose_ports: Optional[List[int]] = None,
        environment: Optional[Dict[str, str]] = None,
        commands: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a Dockerfile for a project
        
        Args:
            project_path: Path to the project
            app_type: Type of application (e.g. "python", "node", "react")
            base_image: Base Docker image
            expose_ports: Ports to expose
            environment: Environment variables
            commands: Additional commands to run
            
        Returns:
            Dictionary with generation results
        """
        self.logger.info(f"Generating Dockerfile for {app_type} project")
        
        if not os.path.exists(project_path):
            return {"error": f"Project path does not exist: {project_path}"}
        
        result = {
            "project_path": project_path,
            "app_type": app_type,
            "success": False
        }
        
        try:
            # Determine the appropriate base image if not provided
            if not base_image:
                base_image = self._get_default_base_image(app_type)
            
            # Determine default ports if not provided
            if not expose_ports:
                expose_ports = self._get_default_ports(app_type)
            
            # Create Dockerfile content
            dockerfile_path = os.path.join(project_path, "Dockerfile")
            
            # Start with the base image
            content = f"FROM {base_image}\n\n"
            
            # Set working directory
            content += "WORKDIR /app\n\n"
            
            # Add app-specific setup (e.g., install dependencies)
            content += self._get_dependency_setup(app_type, project_path)
            
            # Copy the application code
            content += "COPY . .\n\n"
            
            # Set environment variables
            if environment:
                for key, value in environment.items():
                    content += f"ENV {key}={value}\n"
                content += "\n"
            
            # Expose ports
            if expose_ports:
                for port in expose_ports:
                    content += f"EXPOSE {port}\n"
                content += "\n"
            
            # Add custom commands
            if commands:
                for cmd in commands:
                    content += f"RUN {cmd}\n"
                content += "\n"
            
            # Add default command
            content += self._get_default_command(app_type, project_path)
            
            # Write Dockerfile
            with open(dockerfile_path, "w") as f:
                f.write(content)
            
            result["dockerfile_path"] = dockerfile_path
            result["dockerfile_content"] = content
            result["success"] = True
                
        except Exception as e:
            self.logger.error(f"Error generating Dockerfile: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def _extract_image_id(self, build_output: str) -> Optional[str]:
        """Extract the image ID from the build output"""
        # Look for "Successfully built <image_id>"
        match = re.search(r"Successfully built ([a-f0-9]+)", build_output)
        if match:
            return match.group(1)
        return None
    
    def _get_default_base_image(self, app_type: str) -> str:
        """Get the default base image for an app type"""
        app_type = app_type.lower()
        
        if app_type == "python" or app_type == "fastapi" or app_type == "django":
            return "python:3.9-slim"
        elif app_type == "node" or app_type == "express":
            return "node:14-alpine"
        elif app_type == "react" or app_type == "vue":
            return "node:14-alpine"
        elif app_type == "golang" or app_type == "go":
            return "golang:1.17-alpine"
        elif app_type == "java" or app_type == "spring":
            return "openjdk:11-jdk-slim"
        elif app_type == "dotnet" or app_type == "csharp":
            return "mcr.microsoft.com/dotnet/sdk:6.0"
        elif app_type == "php" or app_type == "laravel":
            return "php:8.0-apache"
        else:
            return "alpine:latest"
    
    def _get_default_ports(self, app_type: str) -> List[int]:
        """Get the default ports for an app type"""
        app_type = app_type.lower()
        
        if app_type == "python" or app_type == "fastapi":
            return [8000]
        elif app_type == "django":
            return [8000]
        elif app_type == "node" or app_type == "express":
            return [3000]
        elif app_type == "react":
            return [3000]
        elif app_type == "vue":
            return [8080]
        elif app_type == "golang" or app_type == "go":
            return [8080]
        elif app_type == "java" or app_type == "spring":
            return [8080]
        elif app_type == "dotnet" or app_type == "csharp":
            return [5000, 5001]
        elif app_type == "php" or app_type == "laravel":
            return [80]
        else:
            return [8080]
    
    def _get_dependency_setup(self, app_type: str, project_path: str) -> str:
        """Get the dependency setup commands for an app type"""
        app_type = app_type.lower()
        
        if app_type == "python" or app_type == "fastapi" or app_type == "django":
            if os.path.exists(os.path.join(project_path, "requirements.txt")):
                return "COPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\n"
            else:
                return "RUN pip install --no-cache-dir fastapi uvicorn\n\n"
                
        elif app_type in ["node", "express", "react", "vue"]:
            if os.path.exists(os.path.join(project_path, "package.json")):
                return "COPY package*.json ./\nRUN npm install\n\n"
            else:
                if app_type == "express":
                    return "RUN npm init -y && npm install express\n\n"
                elif app_type == "react":
                    return "RUN npm install -g create-react-app\n\n"
                elif app_type == "vue":
                    return "RUN npm install -g @vue/cli\n\n"
                else:
                    return "RUN npm init -y\n\n"
                    
        elif app_type == "golang" or app_type == "go":
            return "COPY go.* ./\nRUN go mod download\n\n"
            
        elif app_type == "java" or app_type == "spring":
            if os.path.exists(os.path.join(project_path, "pom.xml")):
                return "COPY pom.xml ./\nRUN mvn dependency:go-offline\n\n"
            elif os.path.exists(os.path.join(project_path, "build.gradle")):
                return "COPY build.gradle ./\nRUN gradle dependencies\n\n"
            else:
                return ""
                
        elif app_type == "dotnet" or app_type == "csharp":
            return "COPY *.csproj ./\nRUN dotnet restore\n\n"
            
        elif app_type == "php" or app_type == "laravel":
            if os.path.exists(os.path.join(project_path, "composer.json")):
                return "COPY composer.json composer.lock ./\nRUN composer install --no-scripts --no-autoloader\n\n"
            else:
                return ""
                
        else:
            return ""
    
    def _get_default_command(self, app_type: str, project_path: str) -> str:
        """Get the default command for an app type"""
        app_type = app_type.lower()
        
        if app_type == "python":
            # Look for a main.py file
            if os.path.exists(os.path.join(project_path, "main.py")):
                return 'CMD ["python", "main.py"]'
            else:
                return 'CMD ["python", "-m", "http.server", "8000"]'
                
        elif app_type == "fastapi":
            # Look for a main.py file with FastAPI app
            if os.path.exists(os.path.join(project_path, "main.py")):
                return 'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]'
            else:
                return 'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]'
                
        elif app_type == "django":
            return 'CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]'
            
        elif app_type == "node" or app_type == "express":
            # Check for package.json start script
            if os.path.exists(os.path.join(project_path, "package.json")):
                with open(os.path.join(project_path, "package.json"), 'r') as f:
                    try:
                        package_data = json.load(f)
                        if "scripts" in package_data and "start" in package_data["scripts"]:
                            return 'CMD ["npm", "start"]'
                    except json.JSONDecodeError:
                        pass
            
            # Look for index.js or server.js
            if os.path.exists(os.path.join(project_path, "server.js")):
                return 'CMD ["node", "server.js"]'
            elif os.path.exists(os.path.join(project_path, "index.js")):
                return 'CMD ["node", "index.js"]'
            else:
                return 'CMD ["npm", "start"]'
                
        elif app_type == "react":
            return 'CMD ["npm", "start"]'
            
        elif app_type == "vue":
            return 'CMD ["npm", "run", "serve"]'
            
        elif app_type == "golang" or app_type == "go":
            return 'CMD ["go", "run", "main.go"]'
            
        elif app_type == "java":
            # Check if it's a Spring Boot application
            if os.path.exists(os.path.join(project_path, "pom.xml")):
                return 'CMD ["java", "-jar", "target/*.jar"]'
            else:
                # Try to find a main class
                return 'CMD ["java", "-cp", ".", "Main"]'
                
        elif app_type == "spring":
            return 'CMD ["java", "-jar", "target/*.jar"]'
            
        elif app_type == "dotnet" or app_type == "csharp":
            return 'CMD ["dotnet", "run", "--urls", "http://0.0.0.0:5000"]'
            
        elif app_type == "php":
            return 'CMD ["php", "-S", "0.0.0.0:80"]'
            
        elif app_type == "laravel":
            return 'CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=80"]'
            
        else:
            return 'CMD ["/bin/sh"]'
