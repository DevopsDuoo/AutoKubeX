# actions/scaler.py
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from typing import List, Dict

def scale_deployment(namespace: str, deployment: str, replicas: int):
    """Scale a deployment to specified number of replicas"""
    try:
        apps_v1 = client.AppsV1Api()
        body = {"spec": {"replicas": replicas}}
        apps_v1.patch_namespaced_deployment_scale(deployment, namespace, body)
        return f"✅ Scaled {deployment} in {namespace} to {replicas} replicas"
    except ApiException as e:
        return f"❌ Failed to scale {deployment} in {namespace}: {e.reason}"
    except Exception as e:
        return f"❌ Error scaling {deployment} in {namespace}: {str(e)}"

def get_current_replicas(namespace: str, deployment: str):
    """Get current replica count for a deployment"""
    try:
        apps_v1 = client.AppsV1Api()
        dep = apps_v1.read_namespaced_deployment(deployment, namespace)
        return dep.spec.replicas
    except ApiException as e:
        return f"❌ Failed to get replicas for {deployment} in {namespace}: {e.reason}"
    except Exception as e:
        return f"❌ Error getting replicas for {deployment} in {namespace}: {str(e)}"

def list_deployments(namespace: str = None):
    """List all deployments in namespace (or all namespaces if None)"""
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
                'available_replicas': dep.status.available_replicas or 0
            })
        return result
    except ApiException as e:
        return f"❌ Failed to list deployments: {e.reason}"
    except Exception as e:
        return f"❌ Error listing deployments: {str(e)}"


def bulk_scale_deployments(namespace: str, deployments_config: Dict[str, int]) -> Dict[str, str]:
    """Scale multiple deployments in bulk
    
    Args:
        namespace: Kubernetes namespace
        deployments_config: Dict with deployment names as keys and desired replicas as values
                           Example: {'app1': 3, 'app2': 5, 'app3': 0}
    """
    results = {}
    apps_v1 = client.AppsV1Api()
    
    for deployment_name, replicas in deployments_config.items():
        try:
            body = {"spec": {"replicas": replicas}}
            apps_v1.patch_namespaced_deployment_scale(deployment_name, namespace, body)
            results[deployment_name] = f"✅ Scaled {deployment_name} in {namespace} to {replicas} replicas"
        except ApiException as e:
            results[deployment_name] = f"❌ Failed to scale {deployment_name} in {namespace}: {e.reason}"
        except Exception as e:
            results[deployment_name] = f"❌ Error scaling {deployment_name} in {namespace}: {str(e)}"
    
    return results


def scale_all_deployments_in_namespace(namespace: str, replicas: int, label_selector: str = None) -> Dict[str, str]:
    """Scale all deployments in a namespace to the same number of replicas
    
    Args:
        namespace: Kubernetes namespace
        replicas: Desired number of replicas for all deployments
        label_selector: Optional label selector to filter deployments
    """
    try:
        apps_v1 = client.AppsV1Api()
        deployments = apps_v1.list_namespaced_deployment(namespace=namespace, label_selector=label_selector)
        deployment_names = [dep.metadata.name for dep in deployments.items]
        
        if not deployment_names:
            return {"info": f"No deployments found in namespace {namespace}" + (f" with selector {label_selector}" if label_selector else "")}
        
        deployments_config = {name: replicas for name in deployment_names}
        return bulk_scale_deployments(namespace, deployments_config)
    except ApiException as e:
        return {"error": f"❌ Failed to list deployments in namespace {namespace}: {e.reason}"}
    except Exception as e:
        return {"error": f"❌ Error listing deployments in namespace {namespace}: {str(e)}"}


def scale_deployment_by_percentage(namespace: str, deployment: str, percentage: float):
    """Scale a deployment by a percentage (e.g., 1.5 for 50% increase, 0.5 for 50% decrease)"""
    try:
        apps_v1 = client.AppsV1Api()
        dep = apps_v1.read_namespaced_deployment(deployment, namespace)
        current_replicas = dep.spec.replicas
        new_replicas = max(1, int(current_replicas * percentage))  # Ensure at least 1 replica
        
        body = {"spec": {"replicas": new_replicas}}
        apps_v1.patch_namespaced_deployment_scale(deployment, namespace, body)
        return f"✅ Scaled {deployment} in {namespace} from {current_replicas} to {new_replicas} replicas ({percentage}x)"
    except ApiException as e:
        return f"❌ Failed to scale {deployment} in {namespace}: {e.reason}"
    except Exception as e:
        return f"❌ Error scaling {deployment} in {namespace}: {str(e)}"


def bulk_scale_deployments_by_percentage(namespace: str, deployment_names: List[str], percentage: float) -> Dict[str, str]:
    """Scale multiple deployments by percentage in bulk"""
    results = {}
    
    for deployment_name in deployment_names:
        result = scale_deployment_by_percentage(namespace, deployment_name, percentage)
        results[deployment_name] = result
    
    return results


def auto_scale_based_on_cpu(namespace: str, deployment: str, target_cpu_percent: int = 70):
    """Create or update HPA (Horizontal Pod Autoscaler) for a deployment"""
    try:
        autoscaling_v2 = client.AutoscalingV2Api()
        
        # Check if HPA already exists
        try:
            existing_hpa = autoscaling_v2.read_namespaced_horizontal_pod_autoscaler(deployment, namespace)
            # Update existing HPA
            existing_hpa.spec.target_cpu_utilization_percentage = target_cpu_percent
            autoscaling_v2.patch_namespaced_horizontal_pod_autoscaler(deployment, namespace, existing_hpa)
            return f"✅ Updated HPA for {deployment} in {namespace} with {target_cpu_percent}% CPU target"
        except ApiException as e:
            if e.status == 404:
                # Create new HPA
                hpa_body = client.V2HorizontalPodAutoscaler(
                    metadata=client.V1ObjectMeta(name=deployment),
                    spec=client.V2HorizontalPodAutoscalerSpec(
                        scale_target_ref=client.V2CrossVersionObjectReference(
                            api_version="apps/v1",
                            kind="Deployment",
                            name=deployment
                        ),
                        min_replicas=1,
                        max_replicas=10,
                        metrics=[
                            client.V2MetricSpec(
                                type="Resource",
                                resource=client.V2ResourceMetricSource(
                                    name="cpu",
                                    target=client.V2MetricTarget(
                                        type="Utilization",
                                        average_utilization=target_cpu_percent
                                    )
                                )
                            )
                        ]
                    )
                )
                autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(namespace, hpa_body)
                return f"✅ Created HPA for {deployment} in {namespace} with {target_cpu_percent}% CPU target"
            else:
                raise e
    except ApiException as e:
        return f"❌ Failed to setup HPA for {deployment} in {namespace}: {e.reason}"
    except Exception as e:
        return f"❌ Error setting up HPA for {deployment} in {namespace}: {str(e)}"