# actions/restarter.py
from kubernetes import client

def restart_pod(namespace: str, pod_name: str):
    v1 = client.CoreV1Api()
    v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
    print(f"[!] Restart triggered for {namespace}/{pod_name}")