"""
Container Orchestration Layer

This module provides the interface to the container orchestration system (Kubernetes).
It handles container scheduling, networking, scaling, and monitoring.
"""

import os
import logging
import asyncio
import json
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import kubernetes.client
from kubernetes.client.rest import ApiException
from kubernetes import config

# Configure logging
logger = logging.getLogger(__name__)

class NetworkPolicy(str, Enum):
    """Network policy types for containers."""
    PUBLIC = "public"  # Accessible from outside the cluster
    INTERNAL = "internal"  # Accessible only within the cluster
    PROJECT_ONLY = "project-only"  # Accessible only within the project
    RESTRICTED = "restricted"  # Highly restricted access

class KubernetesResource(BaseModel):
    """Kubernetes resource representation."""
    kind: str
    name: str
    namespace: str
    uid: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    yaml_definition: Optional[str] = None

class ContainerOrchestrator:
    """
    Container Orchestration Layer
    
    Interfaces with Kubernetes to manage containers, including:
    - Creating and managing Kubernetes resources (Pods, Deployments, Services, etc.)
    - Managing container networking
    - Scaling containers
    - Monitoring container health
    """
    
    def __init__(self, in_cluster: bool = False, kubeconfig_path: Optional[str] = None):
        """
        Initialize the Container Orchestrator.
        
        Args:
            in_cluster: Whether to run in a Kubernetes cluster
            kubeconfig_path: Path to kubeconfig file for external access
        """
        self.in_cluster = in_cluster
        self.kubeconfig_path = kubeconfig_path
        self.initialized = False
        
        # Initialize Kubernetes client
        self._initialize_kubernetes_client()
        
        logger.info("Container Orchestrator initialized")
    
    def _initialize_kubernetes_client(self):
        """Initialize the Kubernetes client."""
        try:
            if self.in_cluster:
                # In-cluster configuration
                config.load_incluster_config()
            elif self.kubeconfig_path:
                # External configuration with kubeconfig
                config.load_kube_config(config_file=self.kubeconfig_path)
            else:
                # Default kubeconfig location
                config.load_kube_config()
            
            # Initialize API clients
            self.core_v1 = kubernetes.client.CoreV1Api()
            self.apps_v1 = kubernetes.client.AppsV1Api()
            self.networking_v1 = kubernetes.client.NetworkingV1Api()
            self.custom_objects = kubernetes.client.CustomObjectsApi()
            
            self.initialized = True
            logger.info("Kubernetes client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            # For development/testing, we'll continue without a working Kubernetes client
            self.initialized = False
    
    async def create_namespace(self, name: str, labels: Dict[str, str] = None) -> KubernetesResource:
        """
        Create a Kubernetes namespace.
        
        Args:
            name: Name of the namespace
            labels: Labels to apply to the namespace
            
        Returns:
            The created namespace resource
        """
        if not self.initialized:
            # Mock implementation for development/testing
            logger.warning("Using mock implementation for create_namespace")
            await asyncio.sleep(1)
            return KubernetesResource(
                kind="Namespace",
                name=name,
                namespace="",
                uid=f"mock-uid-{name}",
                labels=labels or {},
                status="Active",
                created_at=datetime.now()
            )
        
        try:
            # Create namespace object
            namespace = kubernetes.client.V1Namespace(
                metadata=kubernetes.client.V1ObjectMeta(
                    name=name,
                    labels=labels or {}
                )
            )
            
            # Create namespace
            api_response = self.core_v1.create_namespace(body=namespace)
            
            # Convert to our model
            result = KubernetesResource(
                kind="Namespace",
                name=api_response.metadata.name,
                namespace="",
                uid=api_response.metadata.uid,
                labels=api_response.metadata.labels or {},
                annotations=api_response.metadata.annotations or {},
                status=api_response.status.phase,
                created_at=api_response.metadata.creation_timestamp
            )
            
            logger.info(f"Created namespace: {name}")
            return result
        except ApiException as e:
            logger.error(f"Failed to create namespace {name}: {e}")
            raise ValueError(f"Failed to create namespace: {e}")
    
    async def create_deployment(
        self,
        name: str,
        namespace: str,
        image: str,
        replicas: int = 1,
        labels: Dict[str, str] = None,
        env_vars: Dict[str, str] = None,
        ports: List[int] = None,
        resources: Dict[str, Dict[str, str]] = None,
        volumes: List[Dict[str, Any]] = None,
        command: List[str] = None,
        args: List[str] = None
    ) -> KubernetesResource:
        """
        Create a Kubernetes deployment.
        
        Args:
            name: Name of the deployment
            namespace: Namespace to create the deployment in
            image: Container image to use
            replicas: Number of replicas
            labels: Labels to apply to the deployment
            env_vars: Environment variables for the container
            ports: Container ports to expose
            resources: Resource requirements (requests and limits)
            volumes: Volumes to mount
            command: Container command
            args: Container command arguments
            
        Returns:
            The created deployment resource
        """
        if not self.initialized:
            # Mock implementation for development/testing
            logger.warning("Using mock implementation for create_deployment")
            await asyncio.sleep(1)
            return KubernetesResource(
                kind="Deployment",
                name=name,
                namespace=namespace,
                uid=f"mock-uid-{name}",
                labels=labels or {},
                status="Available",
                created_at=datetime.now()
            )
        
        try:
            # Create container environment variables
            container_env = []
            if env_vars:
                for key, value in env_vars.items():
                    container_env.append(
                        kubernetes.client.V1EnvVar(name=key, value=value)
                    )
            
            # Create container ports
            container_ports = []
            if ports:
                for port in ports:
                    container_ports.append(
                        kubernetes.client.V1ContainerPort(container_port=port)
                    )
            
            # Create container resources
            container_resources = None
            if resources:
                container_resources = kubernetes.client.V1ResourceRequirements(
                    requests=resources.get("requests"),
                    limits=resources.get("limits")
                )
            
            # Create container volume mounts
            volume_mounts = []
            deployment_volumes = []
            if volumes:
                for volume in volumes:
                    volume_mounts.append(
                        kubernetes.client.V1VolumeMount(
                            name=volume["name"],
                            mount_path=volume["mount_path"],
                            read_only=volume.get("read_only", False)
                        )
                    )
                    
                    if "config_map" in volume:
                        deployment_volumes.append(
                            kubernetes.client.V1Volume(
                                name=volume["name"],
                                config_map=kubernetes.client.V1ConfigMapVolumeSource(
                                    name=volume["config_map"]
                                )
                            )
                        )
                    elif "secret" in volume:
                        deployment_volumes.append(
                            kubernetes.client.V1Volume(
                                name=volume["name"],
                                secret=kubernetes.client.V1SecretVolumeSource(
                                    secret_name=volume["secret"]
                                )
                            )
                        )
                    elif "persistent_volume_claim" in volume:
                        deployment_volumes.append(
                            kubernetes.client.V1Volume(
                                name=volume["name"],
                                persistent_volume_claim=kubernetes.client.V1PersistentVolumeClaimVolumeSource(
                                    claim_name=volume["persistent_volume_claim"]
                                )
                            )
                        )
            
            # Create container
            container = kubernetes.client.V1Container(
                name=name,
                image=image,
                ports=container_ports,
                env=container_env,
                resources=container_resources,
                volume_mounts=volume_mounts,
                command=command,
                args=args
            )
            
            # Create deployment spec
            template = kubernetes.client.V1PodTemplateSpec(
                metadata=kubernetes.client.V1ObjectMeta(labels=labels or {}),
                spec=kubernetes.client.V1PodSpec(
                    containers=[container],
                    volumes=deployment_volumes
                )
            )
            
            spec = kubernetes.client.V1DeploymentSpec(
                replicas=replicas,
                selector=kubernetes.client.V1LabelSelector(
                    match_labels=labels or {}
                ),
                template=template
            )
            
            # Create deployment
            deployment = kubernetes.client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=kubernetes.client.V1ObjectMeta(
                    name=name,
                    namespace=namespace,
                    labels=labels or {}
                ),
                spec=spec
            )
            
            # Create deployment
            api_response = self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            
            # Convert to our model
            result = KubernetesResource(
                kind="Deployment",
                name=api_response.metadata.name,
                namespace=api_response.metadata.namespace,
                uid=api_response.metadata.uid,
                labels=api_response.metadata.labels or {},
                annotations=api_response.metadata.annotations or {},
                status="Created",
                created_at=api_response.metadata.creation_timestamp
            )
            
            logger.info(f"Created deployment: {name} in namespace {namespace}")
            return result
        except ApiException as e:
            logger.error(f"Failed to create deployment {name} in namespace {namespace}: {e}")
            raise ValueError(f"Failed to create deployment: {e}")
    
    async def create_service(
        self,
        name: str,
        namespace: str,
        selector: Dict[str, str],
        ports: List[Dict[str, Union[int, str]]],
        service_type: str = "ClusterIP",
        labels: Dict[str, str] = None
    ) -> KubernetesResource:
        """
        Create a Kubernetes service.
        
        Args:
            name: Name of the service
            namespace: Namespace to create the service in
            selector: Label selector for the service
            ports: Service ports (list of dicts with port, target_port, protocol)
            service_type: Service type (ClusterIP, NodePort, LoadBalancer)
            labels: Labels to apply to the service
            
        Returns:
            The created service resource
        """
        if not self.initialized:
            # Mock implementation for development/testing
            logger.warning("Using mock implementation for create_service")
            await asyncio.sleep(1)
            return KubernetesResource(
                kind="Service",
                name=name,
                namespace=namespace,
                uid=f"mock-uid-{name}",
                labels=labels or {},
                status="Active",
                created_at=datetime.now()
            )
        
        try:
            # Create service ports
            service_ports = []
            for port_info in ports:
                service_ports.append(
                    kubernetes.client.V1ServicePort(
                        port=port_info["port"],
                        target_port=port_info.get("target_port", port_info["port"]),
                        protocol=port_info.get("protocol", "TCP"),
                        name=port_info.get("name", f"port-{port_info['port']}")
                    )
                )
            
            # Create service
            service = kubernetes.client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=kubernetes.client.V1ObjectMeta(
                    name=name,
                    namespace=namespace,
                    labels=labels or {}
                ),
                spec=kubernetes.client.V1ServiceSpec(
                    selector=selector,
                    ports=service_ports,
                    type=service_type
                )
            )
            
            # Create service
            api_response = self.core_v1.create_namespaced_service(
                namespace=namespace,
                body=service
            )
            
            # Convert to our model
            result = KubernetesResource(
                kind="Service",
                name=api_response.metadata.name,
                namespace=api_response.metadata.namespace,
                uid=api_response.metadata.uid,
                labels=api_response.metadata.labels or {},
                annotations=api_response.metadata.annotations or {},
                status="Active",
                created_at=api_response.metadata.creation_timestamp
            )
            
            logger.info(f"Created service: {name} in namespace {namespace}")
            return result
        except ApiException as e:
            logger.error(f"Failed to create service {name} in namespace {namespace}: {e}")
            raise ValueError(f"Failed to create service: {e}")
    
    async def create_network_policy(
        self,
        name: str,
        namespace: str,
        pod_selector: Dict[str, str],
        policy_type: NetworkPolicy,
        labels: Dict[str, str] = None
    ) -> KubernetesResource:
        """
        Create a Kubernetes network policy.
        
        Args:
            name: Name of the network policy
            namespace: Namespace to create the network policy in
            pod_selector: Label selector for the pods to apply the policy to
            policy_type: Type of network policy
            labels: Labels to apply to the network policy
            
        Returns:
            The created network policy resource
        """
        if not self.initialized:
            # Mock implementation for development/testing
            logger.warning("Using mock implementation for create_network_policy")
            await asyncio.sleep(1)
            return KubernetesResource(
                kind="NetworkPolicy",
                name=name,
                namespace=namespace,
                uid=f"mock-uid-{name}",
                labels=labels or {},
                status="Active",
                created_at=datetime.now()
            )
        
        try:
            # Create ingress rules based on policy type
            ingress_rules = []
            egress_rules = []
            
            if policy_type == NetworkPolicy.PUBLIC:
                # Allow all ingress traffic
                ingress_rules.append(kubernetes.client.V1NetworkPolicyIngressRule())
                # Allow all egress traffic
                egress_rules.append(kubernetes.client.V1NetworkPolicyEgressRule())
            
            elif policy_type == NetworkPolicy.INTERNAL:
                # Allow ingress traffic from within the cluster
                ingress_rules.append(
                    kubernetes.client.V1NetworkPolicyIngressRule(
                        _from=[
                            kubernetes.client.V1NetworkPolicyPeer(
                                namespace_selector=kubernetes.client.V1LabelSelector()
                            )
                        ]
                    )
                )
                # Allow all egress traffic
                egress_rules.append(kubernetes.client.V1NetworkPolicyEgressRule())
            
            elif policy_type == NetworkPolicy.PROJECT_ONLY:
                # Allow ingress traffic only from within the same namespace
                ingress_rules.append(
                    kubernetes.client.V1NetworkPolicyIngressRule(
                        _from=[
                            kubernetes.client.V1NetworkPolicyPeer(
                                pod_selector=kubernetes.client.V1LabelSelector()
                            )
                        ]
                    )
                )
                # Allow egress traffic only within the same namespace
                egress_rules.append(
                    kubernetes.client.V1NetworkPolicyEgressRule(
                        to=[
                            kubernetes.client.V1NetworkPolicyPeer(
                                pod_selector=kubernetes.client.V1LabelSelector()
                            )
                        ]
                    )
                )
            
            elif policy_type == NetworkPolicy.RESTRICTED:
                # No ingress rules (deny all ingress)
                # Allow egress only to specific services (DNS, etc.)
                egress_rules.append(
                    kubernetes.client.V1NetworkPolicyEgressRule(
                        to=[
                            kubernetes.client.V1NetworkPolicyPeer(
                                pod_selector=kubernetes.client.V1LabelSelector(
                                    match_labels={"k8s-app": "kube-dns"}
                                ),
                                namespace_selector=kubernetes.client.V1LabelSelector(
                                    match_labels={"kubernetes.io/name": "kube-system"}
                                )
                            )
                        ],
                        ports=[
                            kubernetes.client.V1NetworkPolicyPort(
                                port=53,
                                protocol="UDP"
                            ),
                            kubernetes.client.V1NetworkPolicyPort(
                                port=53,
                                protocol="TCP"
                            )
                        ]
                    )
                )
            
            # Create network policy
            policy_types = ["Ingress", "Egress"]
            
            network_policy = kubernetes.client.V1NetworkPolicy(
                api_version="networking.k8s.io/v1",
                kind="NetworkPolicy",
                metadata=kubernetes.client.V1ObjectMeta(
                    name=name,
                    namespace=namespace,
                    labels=labels or {}
                ),
                spec=kubernetes.client.V1NetworkPolicySpec(
                    pod_selector=kubernetes.client.V1LabelSelector(
                        match_labels=pod_selector
                    ),
                    ingress=ingress_rules,
                    egress=egress_rules,
                    policy_types=policy_types
                )
            )
            
            # Create network policy
            api_response = self.networking_v1.create_namespaced_network_policy(
                namespace=namespace,
                body=network_policy
            )
            
            # Convert to our model
            result = KubernetesResource(
                kind="NetworkPolicy",
                name=api_response.metadata.name,
                namespace=api_response.metadata.namespace,
                uid=api_response.metadata.uid,
                labels=api_response.metadata.labels or {},
                annotations=api_response.metadata.annotations or {},
                status="Active",
                created_at=api_response.metadata.creation_timestamp
            )
            
            logger.info(f"Created network policy: {name} in namespace {namespace}")
            return result
        except ApiException as e:
            logger.error(f"Failed to create network policy {name} in namespace {namespace}: {e}")
            raise ValueError(f"Failed to create network policy: {e}")
    
    async def delete_resource(self, kind: str, name: str, namespace: str) -> None:
        """
        Delete a Kubernetes resource.
        
        Args:
            kind: Kind of resource (Namespace, Deployment, Service, etc.)
            name: Name of the resource
            namespace: Namespace of the resource (empty for cluster-level resources)
        """
        if not self.initialized:
            # Mock implementation for development/testing
            logger.warning(f"Using mock implementation for delete_resource: {kind}/{name}")
            await asyncio.sleep(1)
            return
        
        try:
            if kind == "Namespace":
                self.core_v1.delete_namespace(name=name)
            elif kind == "Deployment":
                self.apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)
            elif kind == "Service":
                self.core_v1.delete_namespaced_service(name=name, namespace=namespace)
            elif kind == "NetworkPolicy":
                self.networking_v1.delete_namespaced_network_policy(name=name, namespace=namespace)
            else:
                raise ValueError(f"Unsupported resource kind: {kind}")
            
            logger.info(f"Deleted {kind}: {name} in namespace {namespace}")
        except ApiException as e:
            logger.error(f"Failed to delete {kind} {name} in namespace {namespace}: {e}")
            raise ValueError(f"Failed to delete {kind}: {e}")
    
    async def get_resource_status(self, kind: str, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get the status of a Kubernetes resource.
        
        Args:
            kind: Kind of resource (Namespace, Deployment, Service, etc.)
            name: Name of the resource
            namespace: Namespace of the resource (empty for cluster-level resources)
            
        Returns:
            Status information for the resource
        """
        if not self.initialized:
            # Mock implementation for development/testing
            logger.warning(f"Using mock implementation for get_resource_status: {kind}/{name}")
            await asyncio.sleep(1)
            
            if kind == "Deployment":
                return {
                    "replicas": 1,
                    "ready_replicas": 1,
                    "available_replicas": 1,
                    "unavailable_replicas": 0,
                    "conditions": [
                        {
                            "type": "Available",
                            "status": "True",
                            "reason": "MinimumReplicasAvailable",
                            "message": "Deployment has minimum availability."
                        }
                    ]
                }
            elif kind == "Service":
                return {
                    "type": "ClusterIP",
                    "cluster_ip": "10.0.0.1",
                    "ports": [
                        {
                            "name": "http",
                            "port": 80,
                            "target_port": 8080,
                            "protocol": "TCP"
                        }
                    ]
                }
            elif kind == "Namespace":
                return {
                    "phase": "Active"
                }
            else:
                return {"status": "Unknown"}
        
        try:
            if kind == "Namespace":
                api_response = self.core_v1.read_namespace(name=name)
                return {
                    "phase": api_response.status.phase
                }
            elif kind == "Deployment":
                api_response = self.apps_v1.read_namespaced_deployment_status(name=name, namespace=namespace)
                conditions = []
                if api_response.status.conditions:
                    for condition in api_response.status.conditions:
                        conditions.append({
                            "type": condition.type,
                            "status": condition.status,
                            "reason": condition.reason,
                            "message": condition.message
                        })
                
                return {
                    "replicas": api_response.status.replicas,
                    "ready_replicas": api_response.status.ready_replicas,
                    "available_replicas": api_response.status.available_replicas,
                    "unavailable_replicas": api_response.status.unavailable_replicas,
                    "conditions": conditions
                }
            elif kind == "Service":
                api_response = self.core_v1.read_namespaced_service(name=name, namespace=namespace)
                ports = []
                for port in api_response.spec.ports:
                    ports.append({
                        "name": port.name,
                        "port": port.port,
                        "target_port": port.target_port,
                        "protocol": port.protocol
                    })
                
                return {
                    "type": api_response.spec.type,
                    "cluster_ip": api_response.spec.cluster_ip,
                    "ports": ports
                }
            else:
                raise ValueError(f"Unsupported resource kind: {kind}")
        except ApiException as e:
            logger.error(f"Failed to get status for {kind} {name} in namespace {namespace}: {e}")
            raise ValueError(f"Failed to get status: {e}")
    
    async def get_pod_logs(self, name: str, namespace: str, container: Optional[str] = None, lines: int = 100) -> str:
        """
        Get logs for a pod.
        
        Args:
            name: Name of the pod
            namespace: Namespace of the pod
            container: Name of the container (if pod has multiple containers)
            lines: Number of log lines to retrieve
            
        Returns:
            Pod logs
        """
        if not self.initialized:
            # Mock implementation for development/testing
            logger.warning(f"Using mock implementation for get_pod_logs: {name}")
            await asyncio.sleep(1)
            return "\n".join([f"Mock log line {i} for pod {name}" for i in range(lines)])
        
        try:
            api_response = self.core_v1.read_namespaced_pod_log(
                name=name,
                namespace=namespace,
                container=container,
                tail_lines=lines
            )
            return api_response
        except ApiException as e:
            logger.error(f"Failed to get logs for pod {name} in namespace {namespace}: {e}")
            raise ValueError(f"Failed to get logs: {e}")

# Singleton instance
container_orchestrator = ContainerOrchestrator()
