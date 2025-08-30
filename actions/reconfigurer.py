from kubernetes import client
from typing import Dict, Any


def update_pod_resources(namespace: str, deployment: str, cpu_request: str = None, memory_request: str = None, cpu_limit: str = None, memory_limit: str = None):
    """Update resource requests and limits for a deployment"""
    try:
        apps_v1 = client.AppsV1Api()
        
        # Get current deployment
        deployment_obj = apps_v1.read_namespaced_deployment(name=deployment, namespace=namespace)
        
        # Update resources
        container = deployment_obj.spec.template.spec.containers[0]
        if not container.resources:
            container.resources = client.V1ResourceRequirements()
        
        if not container.resources.requests:
            container.resources.requests = {}
        if not container.resources.limits:
            container.resources.limits = {}
        
        if cpu_request:
            container.resources.requests['cpu'] = cpu_request
        if memory_request:
            container.resources.requests['memory'] = memory_request
        if cpu_limit:
            container.resources.limits['cpu'] = cpu_limit
        if memory_limit:
            container.resources.limits['memory'] = memory_limit
        
        # Apply the update
        apps_v1.patch_namespaced_deployment(
            name=deployment,
            namespace=namespace,
            body=deployment_obj
        )
        
        return f"✅ Updated resources for {deployment} in {namespace}"
        
    except Exception as e:
        return f"❌ Failed to update resources: {e}"


def apply_hpa(namespace: str, deployment: str, min_replicas: int = 2, max_replicas: int = 10, cpu_target: int = 70):
    """Apply Horizontal Pod Autoscaler to a deployment"""
    try:
        autoscaling_v2 = client.AutoscalingV2Api()
        
        hpa = client.V2HorizontalPodAutoscaler(
            metadata=client.V1ObjectMeta(name=f"{deployment}-hpa", namespace=namespace),
            spec=client.V2HorizontalPodAutoscalerSpec(
                scale_target_ref=client.V2CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=deployment
                ),
                min_replicas=min_replicas,
                max_replicas=max_replicas,
                metrics=[
                    client.V2MetricSpec(
                        type="Resource",
                        resource=client.V2ResourceMetricSource(
                            name="cpu",
                            target=client.V2MetricTarget(
                                type="Utilization",
                                average_utilization=cpu_target
                            )
                        )
                    )
                ]
            )
        )
        
        autoscaling_v2.create_namespaced_horizontal_pod_autoscaler(namespace=namespace, body=hpa)
        return f"✅ Created HPA for {deployment} in {namespace} (min: {min_replicas}, max: {max_replicas})"
        
    except Exception as e:
        return f"❌ Failed to create HPA: {e}"


def patch_deployment_env(namespace: str, deployment: str, env_name: str, env_value: str):
    """Patch deployment environment variables"""
    try:
        patch = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": deployment,
                            "env": [{"name": env_name, "value": env_value}]
                        }]
                    }
                }
            }
        }
        apps_v1 = client.AppsV1Api()
        apps_v1.patch_namespaced_deployment(name=deployment, namespace=namespace, body=patch)
        return f"✅ Patched {deployment} in {namespace} with {env_name}={env_value}"
        
    except Exception as e:
        return f"❌ Failed to patch deployment: {e}"
