# actions/scaler.py
from kubernetes import client

def scale_deployment(namespace: str, deployment: str, replicas: int):
    apps_v1 = client.AppsV1Api()
    body = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment_scale(deployment, namespace, body)
    print(f"[+] Scaled {deployment} in {namespace} to {replicas} replicas")


def get_current_replicas(namespace: str, deployment: str):
    apps_v1 = client.AppsV1Api()
    dep = apps_v1.read_namespaced_deployment(deployment, namespace)
    return dep.spec.replicas