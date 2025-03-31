#!/bin/bash

# Exit on error
set -e

# Check for required tools
command -v eksctl >/dev/null 2>&1 || { echo "eksctl is required but not installed. Aborting." >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting." >&2; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "helm is required but not installed. Aborting." >&2; exit 1; }

# Create EKS cluster
echo "Creating EKS cluster..."
eksctl create cluster -f kubernetes/cluster.yaml

# Wait for cluster to be ready
echo "Waiting for cluster to be ready..."
kubectl wait --for=condition=ready nodes --all --timeout=300s

# Create namespaces
echo "Creating namespaces..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Install NVIDIA device plugin
echo "Installing NVIDIA device plugin..."
kubectl apply -f gpu/nvidia-device-plugin.yaml

# Apply security policies
echo "Applying security policies..."
kubectl apply -f security/network-policies.yaml
kubectl apply -f security/pod-security-policies.yaml
kubectl apply -f security/enhanced-security-policies.yaml

# Add Helm repositories
echo "Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install monitoring stack
echo "Installing monitoring stack..."
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values monitoring/prometheus-values.yaml \
  --set grafana.adminPassword=$GRAFANA_ADMIN_PASSWORD

# Wait for monitoring stack to be ready
echo "Waiting for monitoring stack to be ready..."
kubectl wait --for=condition=ready pods -l app.kubernetes.io/name=prometheus -n monitoring --timeout=300s
kubectl wait --for=condition=ready pods -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s

# Apply custom alert rules
echo "Applying custom alert rules..."
kubectl apply -f monitoring/alert-rules.yaml
kubectl apply -f monitoring/advanced-alert-rules.yaml

# Import custom Grafana dashboards
echo "Importing custom Grafana dashboards..."
kubectl create configmap gpu-dashboard -n monitoring --from-file=monitoring/gpu-dashboard.json --dry-run=client -o yaml | kubectl apply -f -
kubectl create configmap system-dashboard -n monitoring --from-file=monitoring/system-dashboard.json --dry-run=client -o yaml | kubectl apply -f -

# Create GPU test job
echo "Creating GPU test job..."
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: gpu-test
spec:
  template:
    spec:
      containers:
      - name: gpu-test
        image: nvidia/cuda:11.0-base
        resources:
          limits:
            nvidia.com/gpu: 1
        command: ["nvidia-smi"]
      restartPolicy: Never
EOF

# Create monitoring service account with enhanced permissions
echo "Creating monitoring service account with enhanced permissions..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: monitoring
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/metrics", "services", "endpoints", "pods", "events", "namespaces"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["batch"]
  resources: ["jobs", "cronjobs"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["networking.k8s.io"]
  resources: ["networkpolicies"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: monitoring
subjects:
- kind: ServiceAccount
  name: monitoring
  namespace: monitoring
EOF

echo "Infrastructure deployment completed successfully!"
echo "To verify GPU access, check the logs of the gpu-test job:"
echo "kubectl logs job/gpu-test"
echo ""
echo "To access Grafana dashboard:"
echo "kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "Available dashboards:"
echo "- GPU Monitoring: http://localhost:3000/d/gpu-monitoring"
echo "- System Overview: http://localhost:3000/d/system-overview" 