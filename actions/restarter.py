# actions/restarter.py
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from typing import List, Dict

def restart_pod(namespace: str, pod_name: str):
    """Restart a pod by deleting it (letting the controller recreate it)"""
    try:
        v1 = client.CoreV1Api()
        v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        return f"✅ Restart triggered for {namespace}/{pod_name}"
    except ApiException as e:
        return f"❌ Failed to restart pod {namespace}/{pod_name}: {e.reason}"
    except Exception as e:
        return f"❌ Error restarting pod {namespace}/{pod_name}: {str(e)}"

def delete_pod(namespace: str, pod_name: str):
    """Delete a pod permanently"""
    try:
        v1 = client.CoreV1Api()
        v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        return f"✅ Pod {namespace}/{pod_name} deleted successfully"
    except ApiException as e:
        return f"❌ Failed to delete pod {namespace}/{pod_name}: {e.reason}"
    except Exception as e:
        return f"❌ Error deleting pod {namespace}/{pod_name}: {str(e)}"

def restart_deployment(namespace: str, deployment_name: str):
    """Restart all pods in a deployment by adding a restart annotation"""
    try:
        apps_v1 = client.AppsV1Api()
        import datetime
        now = datetime.datetime.now().isoformat()
        
        body = {
            'spec': {
                'template': {
                    'metadata': {
                        'annotations': {
                            'kubectl.kubernetes.io/restartedAt': now
                        }
                    }
                }
            }
        }
        
        apps_v1.patch_namespaced_deployment(deployment_name, namespace, body)
        return f"✅ Deployment {namespace}/{deployment_name} restart triggered"
    except ApiException as e:
        return f"❌ Failed to restart deployment {namespace}/{deployment_name}: {e.reason}"
    except Exception as e:
        return f"❌ Error restarting deployment {namespace}/{deployment_name}: {str(e)}"


def bulk_restart_pods(namespace: str, pod_names: List[str]) -> Dict[str, str]:
    """Restart multiple pods in bulk"""
    results = {}
    v1 = client.CoreV1Api()
    
    for pod_name in pod_names:
        try:
            v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
            results[pod_name] = f"✅ Restart triggered for {namespace}/{pod_name}"
        except ApiException as e:
            results[pod_name] = f"❌ Failed to restart pod {namespace}/{pod_name}: {e.reason}"
        except Exception as e:
            results[pod_name] = f"❌ Error restarting pod {namespace}/{pod_name}: {str(e)}"
    
    return results


def bulk_delete_pods(namespace: str, pod_names: List[str]) -> Dict[str, str]:
    """Delete multiple pods in bulk"""
    results = {}
    v1 = client.CoreV1Api()
    
    for pod_name in pod_names:
        try:
            v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
            results[pod_name] = f"✅ Pod {namespace}/{pod_name} deleted successfully"
        except ApiException as e:
            results[pod_name] = f"❌ Failed to delete pod {namespace}/{pod_name}: {e.reason}"
        except Exception as e:
            results[pod_name] = f"❌ Error deleting pod {namespace}/{pod_name}: {str(e)}"
    
    return results


def bulk_restart_deployments(namespace: str, deployment_names: List[str]) -> Dict[str, str]:
    """Restart multiple deployments in bulk"""
    results = {}
    apps_v1 = client.AppsV1Api()
    
    import datetime
    now = datetime.datetime.now().isoformat()
    
    body = {
        'spec': {
            'template': {
                'metadata': {
                    'annotations': {
                        'kubectl.kubernetes.io/restartedAt': now
                    }
                }
            }
        }
    }
    
    for deployment_name in deployment_names:
        try:
            apps_v1.patch_namespaced_deployment(deployment_name, namespace, body)
            results[deployment_name] = f"✅ Deployment {namespace}/{deployment_name} restart triggered"
        except ApiException as e:
            results[deployment_name] = f"❌ Failed to restart deployment {namespace}/{deployment_name}: {e.reason}"
        except Exception as e:
            results[deployment_name] = f"❌ Error restarting deployment {namespace}/{deployment_name}: {str(e)}"
    
    return results


def bulk_delete_deployments(namespace: str, deployment_names: List[str]) -> Dict[str, str]:
    """Delete multiple deployments in bulk"""
    results = {}
    apps_v1 = client.AppsV1Api()
    
    for deployment_name in deployment_names:
        try:
            apps_v1.delete_namespaced_deployment(name=deployment_name, namespace=namespace)
            results[deployment_name] = f"✅ Deployment {namespace}/{deployment_name} deleted successfully"
        except ApiException as e:
            results[deployment_name] = f"❌ Failed to delete deployment {namespace}/{deployment_name}: {e.reason}"
        except Exception as e:
            results[deployment_name] = f"❌ Error deleting deployment {namespace}/{deployment_name}: {str(e)}"
    
    return results


def restart_all_pods_in_namespace(namespace: str, label_selector: str = None) -> Dict[str, str]:
    """Restart all pods in a namespace (optionally filtered by label selector)"""
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
        pod_names = [pod.metadata.name for pod in pods.items]
        
        if not pod_names:
            return {"info": f"No pods found in namespace {namespace}" + (f" with selector {label_selector}" if label_selector else "")}
        
        return bulk_restart_pods(namespace, pod_names)
    except ApiException as e:
        return {"error": f"❌ Failed to list pods in namespace {namespace}: {e.reason}"}
    except Exception as e:
        return {"error": f"❌ Error listing pods in namespace {namespace}: {str(e)}"}