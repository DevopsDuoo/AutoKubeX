from kubernetes import client
from kubernetes.client import V1Patch

def patch_deployment_env(namespace: str, deployment: str, env_name: str, env_value: str):
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
    print(f"[~] Patched {deployment} in {namespace} with {env_name}={env_value}")