# AutoKubeX Actions Guide

## Overview
AutoKubeX now supports comprehensive cluster management operations including individual actions, bulk operations, and advanced scaling capabilities for both pods and deployments.

## CLI Commands

### Individual Pod Actions
```bash
# Restart a single pod
python main.py restart-pod-cmd --kubeconfig /path/to/kubeconfig --namespace default --pod my-pod

# Delete a single pod
python main.py delete-pod-cmd --kubeconfig /path/to/kubeconfig --namespace default --pod my-pod
```

### Individual Deployment Actions
```bash
# Restart a deployment
python main.py restart-deployment-cmd --kubeconfig /path/to/kubeconfig --namespace default --deployment my-app

# Scale a deployment
python main.py scale-cmd --kubeconfig /path/to/kubeconfig --namespace default --deployment my-app --replicas 5
```

### Bulk Pod Operations
```bash
# Bulk restart multiple pods
python main.py bulk-restart-pods-cmd --kubeconfig /path/to/kubeconfig --namespace default --pods "pod1,pod2,pod3"

# Bulk delete multiple pods
python main.py bulk-delete-pods-cmd --kubeconfig /path/to/kubeconfig --namespace default --pods "pod1,pod2,pod3"

# Restart all pods in namespace
python main.py restart-namespace-cmd --kubeconfig /path/to/kubeconfig --namespace default

# Restart pods with label selector
python main.py restart-namespace-cmd --kubeconfig /path/to/kubeconfig --namespace default --selector "app=myapp"
```

### Bulk Deployment Operations
```bash
# Bulk restart multiple deployments
python main.py bulk-restart-deployments-cmd --kubeconfig /path/to/kubeconfig --namespace default --deployments "app1,app2,app3"

# Bulk delete multiple deployments
python main.py bulk-delete-deployments-cmd --kubeconfig /path/to/kubeconfig --namespace default --deployments "app1,app2,app3"

# Bulk scale multiple deployments with different replica counts
python main.py bulk-scale-cmd --kubeconfig /path/to/kubeconfig --namespace default --config "app1:3,app2:5,app3:0"

# Scale all deployments in namespace to same replica count
python main.py scale-all-cmd --kubeconfig /path/to/kubeconfig --namespace default --replicas 2

# Scale all deployments with label selector
python main.py scale-all-cmd --kubeconfig /path/to/kubeconfig --namespace default --replicas 2 --selector "tier=backend"
```

### Advanced Scaling Operations
```bash
# Scale by percentage (1.5 = 50% increase, 0.5 = 50% decrease)
python main.py scale-by-percentage-cmd --kubeconfig /path/to/kubeconfig --namespace default --deployment my-app --percentage 1.5
```

### Listing Commands
```bash
# List all pods with status
python main.py list-pods --kubeconfig /path/to/kubeconfig --namespace default

# List all deployments with status
python main.py list-deployments-cmd --kubeconfig /path/to/kubeconfig --namespace default

# List problematic pods needing attention
python main.py problems --kubeconfig /path/to/kubeconfig
```

## Web UI Features

### Individual Actions Tab
- **Pod Actions**: Select namespace and pod for restart/delete operations
- **Deployment Actions**: Select deployment for scaling/restart operations with current replica display

### Bulk Operations Tab
- **Bulk Pod Operations**:
  - Multi-select pods for bulk restart/delete
  - Restart all pods in namespace (with optional label selector)
- **Bulk Deployment Operations**:
  - Multi-select deployments for bulk restart/delete
  - Configure different replica counts for multiple deployments
  - Bulk scaling with individual replica settings

### Advanced Scaling Tab
- **Scale by Percentage**: Apply scaling factors (e.g., 1.5x, 0.5x) to deployments
- **Scale All in Namespace**: Set same replica count for all deployments in namespace
- **Label Selector Support**: Filter operations by Kubernetes labels

## Key Features

### Bulk Operations
- **Parallel Processing**: All bulk operations process multiple resources simultaneously
- **Individual Results**: Each operation returns success/failure status per resource
- **Error Handling**: Comprehensive error handling with descriptive messages

### Advanced Capabilities
- **Label Selectors**: Filter resources by Kubernetes labels for targeted operations
- **Percentage Scaling**: Scale deployments by multiplication factors
- **Namespace-wide Operations**: Apply actions to all resources in a namespace
- **Real-time Status**: Live cluster data with refresh capabilities

### Safety Features
- **Minimum Replicas**: Percentage scaling ensures at least 1 replica
- **Error Isolation**: Failed operations on one resource don't affect others
- **Detailed Feedback**: Clear success/error messages with specific reasons

## Prerequisites

1. **Kubernetes Access**: Valid kubeconfig file with appropriate RBAC permissions
2. **Required Permissions**:
   ```yaml
   # Pod operations
   - apiGroups: [""]
     resources: ["pods"]
     verbs: ["get", "list", "delete"]
   
   # Deployment operations  
   - apiGroups: ["apps"]
     resources: ["deployments", "deployments/scale"]
     verbs: ["get", "list", "patch", "delete"]
   
   # HPA operations (for auto-scaling)
   - apiGroups: ["autoscaling"]
     resources: ["horizontalpodautoscalers"]
     verbs: ["get", "list", "create", "patch"]
   ```

3. **Dependencies**: All required Python packages (run `pip install -r requirements.txt`)

## Troubleshooting

### Common Issues
- **Connection Failed**: Verify kubeconfig path and cluster accessibility
- **Permission Denied**: Check RBAC permissions for your service account
- **Resource Not Found**: Ensure namespace and resource names are correct
- **Scaling Issues**: Verify deployment exists and is not managed by HPA

### Error Messages
- `❌ Failed to restart pod`: Usually indicates permission or connectivity issues
- `❌ Error scaling deployment`: Check if deployment exists and has valid replica count
- `❌ No pods found`: Namespace may be empty or label selector too restrictive

### Best Practices
- **Test First**: Try operations on non-critical resources first
- **Use Labels**: Leverage label selectors for precise resource targeting  
- **Monitor Results**: Check individual operation results in bulk operations
- **Backup Important**: Consider backing up critical deployments before bulk operations

## Examples

### Scenario 1: Rolling Restart of All Backend Services
```bash
# CLI approach
python main.py restart-namespace-cmd --kubeconfig /path/to/kubeconfig --namespace production --selector "tier=backend"

# Or bulk deployment restart
python main.py bulk-restart-deployments-cmd --kubeconfig /path/to/kubeconfig --namespace production --deployments "api,worker,scheduler"
```

### Scenario 2: Scale Down Non-Production Environment
```bash
# Scale all deployments to 1 replica
python main.py scale-all-cmd --kubeconfig /path/to/kubeconfig --namespace staging --replicas 1

# Or scale to 50% of current replicas
python main.py scale-by-percentage-cmd --kubeconfig /path/to/kubeconfig --namespace staging --deployment api --percentage 0.5
```

### Scenario 3: Clean Up Failed Pods
```bash
# List problematic pods first
python main.py problems --kubeconfig /path/to/kubeconfig

# Then bulk restart them (replace with actual pod names)
python main.py bulk-restart-pods-cmd --kubeconfig /path/to/kubeconfig --namespace default --pods "failed-pod1,failed-pod2"
```
