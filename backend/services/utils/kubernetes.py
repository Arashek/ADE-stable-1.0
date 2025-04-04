from typing import Dict, List, Optional, Any
import logging
import os
import subprocess
import yaml
import json
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class KubernetesManager:
    """
    Utility class for managing Kubernetes deployments
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def check_kubernetes_available(self) -> bool:
        """
        Check if kubectl is available on the system
        
        Returns:
            True if kubectl is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"kubectl not available: {str(e)}")
            return False
    
    def deploy_application(
        self, 
        k8s_config: Dict[str, Any],
        namespace: Optional[str] = None,
        apply_only: bool = False
    ) -> Dict[str, Any]:
        """
        Deploy an application to Kubernetes
        
        Args:
            k8s_config: Kubernetes configuration (deployment, service, etc.)
            namespace: Kubernetes namespace to deploy to
            apply_only: If True, will only apply the configuration without waiting
            
        Returns:
            Dictionary with deployment results
        """
        self.logger.info(f"Deploying application to Kubernetes")
        
        if not self.check_kubernetes_available():
            return {"error": "kubectl is not available"}
        
        result = {
            "success": False,
            "resources_applied": [],
            "logs": []
        }
        
        try:
            # Set namespace if provided
            if namespace:
                result["namespace"] = namespace
                
                # Check if namespace exists
                namespace_exists = self._check_namespace_exists(namespace)
                if not namespace_exists:
                    # Create namespace
                    ns_result = self._create_namespace(namespace)
                    result["namespace_created"] = ns_result["success"]
                    if not ns_result["success"]:
                        return {**result, "error": f"Failed to create namespace: {ns_result.get('error')}"}
            
            # Write Kubernetes config to temp files and apply them
            with tempfile.TemporaryDirectory() as temp_dir:
                applied_resources = []
                
                # Handle deployment
                if "deployment" in k8s_config:
                    dep_result = self._apply_resource(k8s_config["deployment"], "deployment.yaml", temp_dir, namespace)
                    applied_resources.append(dep_result)
                    
                # Handle service
                if "service" in k8s_config:
                    svc_result = self._apply_resource(k8s_config["service"], "service.yaml", temp_dir, namespace)
                    applied_resources.append(svc_result)
                    
                # Handle config maps
                if "config_maps" in k8s_config and k8s_config["config_maps"]:
                    for i, cm in enumerate(k8s_config["config_maps"]):
                        cm_result = self._apply_resource(cm, f"configmap-{i}.yaml", temp_dir, namespace)
                        applied_resources.append(cm_result)
                        
                # Handle secrets
                if "secrets" in k8s_config and k8s_config["secrets"]:
                    for i, secret in enumerate(k8s_config["secrets"]):
                        secret_result = self._apply_resource(secret, f"secret-{i}.yaml", temp_dir, namespace)
                        applied_resources.append(secret_result)
                        
                # Handle ingress
                if "ingress" in k8s_config:
                    ing_result = self._apply_resource(k8s_config["ingress"], "ingress.yaml", temp_dir, namespace)
                    applied_resources.append(ing_result)
                
                # Update result with applied resources
                result["resources_applied"] = applied_resources
                
                # Check for any application failures
                failures = [r for r in applied_resources if not r.get("success", False)]
                if failures:
                    first_failure = failures[0]
                    result["error"] = f"Failed to apply {first_failure.get('resource_type')}: {first_failure.get('error')}"
                    return result
                
                # Wait for deployment to be ready if not apply_only
                if not apply_only and "deployment" in k8s_config:
                    dep_name = k8s_config["deployment"]["metadata"]["name"]
                    wait_result = self._wait_for_deployment(dep_name, namespace)
                    
                    result["deployment_ready"] = wait_result["success"]
                    result["logs"].append(f"Deployment readiness: {wait_result.get('status', 'unknown')}")
                    
                    if not wait_result["success"]:
                        result["error"] = f"Deployment not ready: {wait_result.get('error')}"
                        return result
                    
                # Get service URL if service exists
                if "service" in k8s_config:
                    svc_name = k8s_config["service"]["metadata"]["name"]
                    svc_result = self._get_service_url(svc_name, namespace)
                    result["service_url"] = svc_result.get("url")
                    
                    # Get ingress URL if ingress exists
                    if "ingress" in k8s_config:
                        ing_name = k8s_config["ingress"]["metadata"]["name"]
                        ing_result = self._get_ingress_url(ing_name, namespace)
                        result["ingress_url"] = ing_result.get("url")
                
                # Set success flag
                result["success"] = True
                
        except Exception as e:
            self.logger.error(f"Error deploying to Kubernetes: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def delete_application(
        self,
        resources: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete an application from Kubernetes
        
        Args:
            resources: List of Kubernetes resources to delete
            namespace: Kubernetes namespace
            
        Returns:
            Dictionary with deletion results
        """
        self.logger.info(f"Deleting application from Kubernetes")
        
        if not self.check_kubernetes_available():
            return {"error": "kubectl is not available"}
        
        result = {
            "success": False,
            "resources_deleted": []
        }
        
        try:
            # Write Kubernetes resources to temp files and delete them
            with tempfile.TemporaryDirectory() as temp_dir:
                deleted_resources = []
                
                for i, resource in enumerate(resources):
                    del_result = self._delete_resource(resource, f"resource-{i}.yaml", temp_dir, namespace)
                    deleted_resources.append(del_result)
                
                # Update result with deleted resources
                result["resources_deleted"] = deleted_resources
                
                # Check for any deletion failures
                failures = [r for r in deleted_resources if not r.get("success", False)]
                if failures:
                    first_failure = failures[0]
                    result["error"] = f"Failed to delete {first_failure.get('resource_type')}: {first_failure.get('error')}"
                    return result
                
                # Set success flag
                result["success"] = True
                
        except Exception as e:
            self.logger.error(f"Error deleting from Kubernetes: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def generate_kubernetes_config(
        self,
        app_name: str,
        image_name: str,
        namespace: str = "default",
        replicas: int = 1,
        ports: List[Dict[str, Any]] = None,
        env_vars: List[Dict[str, str]] = None,
        volume_mounts: List[Dict[str, Any]] = None,
        resource_limits: Dict[str, str] = None,
        ingress_host: Optional[str] = None,
        ingress_tls: bool = False
    ) -> Dict[str, Any]:
        """
        Generate Kubernetes configuration for an application
        
        Args:
            app_name: Name of the application
            image_name: Docker image name (and tag)
            namespace: Kubernetes namespace
            replicas: Number of replicas
            ports: List of port configurations
            env_vars: List of environment variables
            volume_mounts: List of volume mount configurations
            resource_limits: CPU and memory limits
            ingress_host: Host for ingress
            ingress_tls: Enable TLS for ingress
            
        Returns:
            Dictionary with Kubernetes configuration
        """
        self.logger.info(f"Generating Kubernetes config for {app_name}")
        
        if not ports:
            ports = [{"containerPort": 8080, "name": "http"}]
            
        # Set up basic service port
        service_port = 80
        target_port = ports[0]["containerPort"]
        port_name = ports[0].get("name", "http")
        
        # Generate deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": app_name,
                "labels": {
                    "app": app_name
                }
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": app_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": app_name
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": app_name,
                                "image": image_name,
                                "ports": ports
                            }
                        ]
                    }
                }
            }
        }
        
        # Add environment variables if provided
        if env_vars:
            deployment["spec"]["template"]["spec"]["containers"][0]["env"] = env_vars
        
        # Add volume mounts if provided
        if volume_mounts:
            deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = volume_mounts["mounts"]
            deployment["spec"]["template"]["spec"]["volumes"] = volume_mounts["volumes"]
        
        # Add resource limits if provided
        if resource_limits:
            deployment["spec"]["template"]["spec"]["containers"][0]["resources"] = {
                "limits": resource_limits
            }
        
        # Generate service
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": app_name,
                "labels": {
                    "app": app_name
                }
            },
            "spec": {
                "selector": {
                    "app": app_name
                },
                "ports": [
                    {
                        "port": service_port,
                        "targetPort": target_port,
                        "name": port_name
                    }
                ],
                "type": "ClusterIP"
            }
        }
        
        # Generate ingress if host is provided
        ingress = None
        if ingress_host:
            ingress = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": app_name,
                    "annotations": {
                        "kubernetes.io/ingress.class": "nginx"
                    }
                },
                "spec": {
                    "rules": [
                        {
                            "host": ingress_host,
                            "http": {
                                "paths": [
                                    {
                                        "path": "/",
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": app_name,
                                                "port": {
                                                    "name": port_name
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
            
            # Add TLS if enabled
            if ingress_tls:
                ingress["spec"]["tls"] = [
                    {
                        "hosts": [ingress_host],
                        "secretName": f"{app_name}-tls"
                    }
                ]
                ingress["metadata"]["annotations"]["cert-manager.io/cluster-issuer"] = "letsencrypt-prod"
        
        # Build final config
        k8s_config = {
            "deployment": deployment,
            "service": service
        }
        
        if ingress:
            k8s_config["ingress"] = ingress
        
        return k8s_config
    
    def _check_namespace_exists(self, namespace: str) -> bool:
        """Check if a Kubernetes namespace exists"""
        try:
            cmd = ["kubectl", "get", "namespace", namespace, "-o", "name"]
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return process.returncode == 0
        except Exception:
            return False
    
    def _create_namespace(self, namespace: str) -> Dict[str, Any]:
        """Create a Kubernetes namespace"""
        try:
            cmd = ["kubectl", "create", "namespace", namespace]
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            result = {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr
            }
            
            if process.returncode != 0:
                result["error"] = f"Failed to create namespace: {process.stderr}"
                
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _apply_resource(
        self, 
        resource: Dict[str, Any], 
        filename: str, 
        temp_dir: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply a Kubernetes resource"""
        resource_type = resource.get("kind", "Unknown").lower()
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        
        result = {
            "resource_type": resource_type,
            "resource_name": resource_name,
            "success": False
        }
        
        try:
            # Write resource to temp file
            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, "w") as f:
                yaml.dump(resource, f)
            
            # Build kubectl command
            cmd = ["kubectl", "apply", "-f", temp_path]
            if namespace:
                cmd.extend(["-n", namespace])
            
            # Apply the resource
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            
            if process.returncode == 0:
                result["success"] = True
            else:
                result["error"] = f"kubectl apply failed: {process.stderr}"
                
            return result
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def _delete_resource(
        self, 
        resource: Dict[str, Any], 
        filename: str, 
        temp_dir: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete a Kubernetes resource"""
        resource_type = resource.get("kind", "Unknown").lower()
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        
        result = {
            "resource_type": resource_type,
            "resource_name": resource_name,
            "success": False
        }
        
        try:
            # Write resource to temp file
            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, "w") as f:
                yaml.dump(resource, f)
            
            # Build kubectl command
            cmd = ["kubectl", "delete", "-f", temp_path]
            if namespace:
                cmd.extend(["-n", namespace])
            
            # Delete the resource
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            
            if process.returncode == 0:
                result["success"] = True
            else:
                result["error"] = f"kubectl delete failed: {process.stderr}"
                
            return result
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def _wait_for_deployment(
        self, 
        deployment_name: str, 
        namespace: Optional[str] = None,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """Wait for a deployment to be ready"""
        result = {
            "deployment": deployment_name,
            "success": False
        }
        
        try:
            # Build kubectl command
            cmd = ["kubectl", "rollout", "status", f"deployment/{deployment_name}", f"--timeout={timeout_seconds}s"]
            if namespace:
                cmd.extend(["-n", namespace])
            
            # Wait for deployment
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            
            if process.returncode == 0:
                result["success"] = True
                result["status"] = "ready"
            else:
                result["error"] = f"Deployment not ready in {timeout_seconds} seconds: {process.stderr}"
                result["status"] = "not_ready"
                
            return result
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            return result
    
    def _get_service_url(self, service_name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get the URL for a service"""
        result = {
            "service": service_name,
            "success": False
        }
        
        try:
            # Build kubectl command to get service details
            cmd = ["kubectl", "get", "service", service_name, "-o", "json"]
            if namespace:
                cmd.extend(["-n", namespace])
            
            # Get service details
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if process.returncode == 0:
                try:
                    service_data = json.loads(process.stdout)
                    service_type = service_data.get("spec", {}).get("type", "ClusterIP")
                    
                    # Determine URL based on service type
                    if service_type == "LoadBalancer":
                        # Check for external IP
                        ingress = service_data.get("status", {}).get("loadBalancer", {}).get("ingress", [])
                        if ingress and "ip" in ingress[0]:
                            ip = ingress[0]["ip"]
                            port = service_data.get("spec", {}).get("ports", [])[0].get("port", 80)
                            result["url"] = f"http://{ip}:{port}"
                            result["success"] = True
                        else:
                            result["error"] = "LoadBalancer service does not have an external IP yet"
                    elif service_type == "NodePort":
                        # Get node port
                        node_port = service_data.get("spec", {}).get("ports", [])[0].get("nodePort")
                        if node_port:
                            # Get a node IP
                            node_cmd = ["kubectl", "get", "nodes", "-o", "json"]
                            node_process = subprocess.run(node_cmd, capture_output=True, text=True, check=False)
                            
                            if node_process.returncode == 0:
                                node_data = json.loads(node_process.stdout)
                                nodes = node_data.get("items", [])
                                
                                if nodes:
                                    # Use the first node's external IP or internal IP if external is not available
                                    addresses = nodes[0].get("status", {}).get("addresses", [])
                                    external_ip = None
                                    internal_ip = None
                                    
                                    for addr in addresses:
                                        if addr.get("type") == "ExternalIP":
                                            external_ip = addr.get("address")
                                        elif addr.get("type") == "InternalIP":
                                            internal_ip = addr.get("address")
                                    
                                    ip = external_ip or internal_ip
                                    if ip:
                                        result["url"] = f"http://{ip}:{node_port}"
                                        result["success"] = True
                                    else:
                                        result["error"] = "Could not determine node IP"
                                else:
                                    result["error"] = "No nodes found in the cluster"
                            else:
                                result["error"] = f"Error getting nodes: {node_process.stderr}"
                        else:
                            result["error"] = "NodePort service does not have a nodePort"
                    else:
                        # For ClusterIP, can only access within the cluster
                        cluster_ip = service_data.get("spec", {}).get("clusterIP")
                        port = service_data.get("spec", {}).get("ports", [])[0].get("port", 80)
                        result["url"] = f"http://{cluster_ip}:{port}"
                        result["cluster_only"] = True
                        result["success"] = True
                        
                except json.JSONDecodeError:
                    result["error"] = "Failed to parse service details"
            else:
                result["error"] = f"Error getting service: {process.stderr}"
                
            return result
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def _get_ingress_url(self, ingress_name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get the URL for an ingress"""
        result = {
            "ingress": ingress_name,
            "success": False
        }
        
        try:
            # Build kubectl command to get ingress details
            cmd = ["kubectl", "get", "ingress", ingress_name, "-o", "json"]
            if namespace:
                cmd.extend(["-n", namespace])
            
            # Get ingress details
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if process.returncode == 0:
                try:
                    ingress_data = json.loads(process.stdout)
                    
                    # Get host from ingress rules
                    rules = ingress_data.get("spec", {}).get("rules", [])
                    if rules and "host" in rules[0]:
                        host = rules[0]["host"]
                        
                        # Check if TLS is enabled
                        tls = ingress_data.get("spec", {}).get("tls", [])
                        protocol = "https" if tls else "http"
                        
                        result["url"] = f"{protocol}://{host}"
                        result["success"] = True
                    else:
                        result["error"] = "Ingress does not have a host rule"
                        
                except json.JSONDecodeError:
                    result["error"] = "Failed to parse ingress details"
            else:
                result["error"] = f"Error getting ingress: {process.stderr}"
                
            return result
        except Exception as e:
            result["error"] = str(e)
            return result
