# actions/action_handler.py
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from typing import List, Dict, Any

def get_all_pods(namespace: str = None) -> List[Dict[str, Any]]:
    """Get all pods with their status"""
    try:
        v1 = client.CoreV1Api()
        if namespace:
            pods = v1.list_namespaced_pod(namespace)
        else:
            pods = v1.list_pod_for_all_namespaces()
        
        result = []
        for pod in pods.items:
            pod_info = {
                'name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'phase': pod.status.phase,
                'ready': False,
                'restarts': 0,
                'age': pod.metadata.creation_timestamp,
                'node': pod.spec.node_name or 'Unknown'
            }
            
            if pod.status.container_statuses:
                pod_info['ready'] = all(cs.ready for cs in pod.status.container_statuses)
                pod_info['restarts'] = sum(cs.restart_count for cs in pod.status.container_statuses)
            
            result.append(pod_info)
        
        return result
    except ApiException as e:
        return [{'error': f"Failed to get pods: {e.reason}"}]
    except Exception as e:
        return [{'error': f"Error getting pods: {str(e)}"}]

def get_all_deployments(namespace: str = None) -> List[Dict[str, Any]]:
    """Get all deployments with their status"""
    try:
        apps_v1 = client.AppsV1Api()
        if namespace:
            deployments = apps_v1.list_namespaced_deployment(namespace)
        else:
            deployments = apps_v1.list_deployment_for_all_namespaces()
        
        result = []
        for dep in deployments.items:
            result.append({
                'name': dep.metadata.name,
                'namespace': dep.metadata.namespace,
                'replicas': dep.spec.replicas,
                'ready_replicas': dep.status.ready_replicas or 0,
                'available_replicas': dep.status.available_replicas or 0,
                'updated_replicas': dep.status.updated_replicas or 0,
                'age': dep.metadata.creation_timestamp
            })
        
        return result
    except ApiException as e:
        return [{'error': f"Failed to get deployments: {e.reason}"}]
    except Exception as e:
        return [{'error': f"Error getting deployments: {str(e)}"}]

def get_all_namespaces() -> List[str]:
    """Get all available namespaces"""
    try:
        v1 = client.CoreV1Api()
        namespaces = v1.list_namespace()
        return [ns.metadata.name for ns in namespaces.items]
    except ApiException as e:
        return [f"Error: {e.reason}"]
    except Exception as e:
        return [f"Error: {str(e)}"]

def get_problematic_pods() -> List[Dict[str, Any]]:
    """Get pods that are not running or not ready"""
    all_pods = get_all_pods()
    problematic = []
    
    for pod in all_pods:
        if 'error' in pod:
            continue
        
        if (pod['phase'] != 'Running' or 
            not pod['ready'] or 
            pod['restarts'] > 5):
            problematic.append(pod)
    
    return problematic
