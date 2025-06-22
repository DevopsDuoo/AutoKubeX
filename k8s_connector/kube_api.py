from kubernetes import client

def get_pod_issues():
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces()
    unhealthy = []
    for pod in pods.items:
        for cs in pod.status.container_statuses or []:
            if not cs.ready:
                unhealthy.append((pod.metadata.namespace, pod.metadata.name))
    return unhealthy

def get_cluster_summary():
    v1 = client.CoreV1Api()
    summary = []
    pods = v1.list_pod_for_all_namespaces()
    for pod in pods.items:
        summary.append(f"{pod.metadata.namespace}/{pod.metadata.name} - {pod.status.phase}")
    return "\n".join(summary)