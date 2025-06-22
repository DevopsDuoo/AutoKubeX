import requests

def get_prometheus_metrics(prometheus_url: str):
    try:
        response = requests.get(f"{prometheus_url}/api/v1/query?query=up")
        if response.ok:
            results = response.json().get("data", {}).get("result", [])
            return results
        return []
    except Exception as e:
        return [f"[Error fetching metrics]: {str(e)}"]


def get_k8s_events():
    from kubernetes import client
    v1 = client.CoreV1Api()
    events = v1.list_event_for_all_namespaces()
    return [(e.involved_object.name, e.message) for e in events.items if e.type == "Warning"]
