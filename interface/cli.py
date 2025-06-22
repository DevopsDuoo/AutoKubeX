import typer
from k8s_connector.cluster_connector import load_cluster
from ai_engine.planner import diagnose_cluster

app = typer.Typer()

@app.command()
def connect(cluster_config: str):
    """Connect to Kubernetes cluster."""
    load_cluster(cluster_config)
    
    from kubernetes import config
    context = config.list_kube_config_contexts()[1]
    typer.echo(f"[✔] Active context: {context['name']}")

# @app.command()
# def connect(cluster_config: str):
#     """Connect to a Kubernetes cluster using kubeconfig path."""
#     load_cluster(cluster_config)

# @app.command()
# def diagnose():
#     """Run diagnosis using AI engine."""
#     result = diagnose_cluster()
#     typer.echo(result)

@app.command()
def diagnose(kubeconfig_path: str = typer.Option(..., "--kubeconfig", help="/Users/Shared/cloud/.kube/dev_blue")):
    from k8s_connector.cluster_connector import load_cluster
    load_cluster(kubeconfig_path)

    result = diagnose_cluster()
    typer.echo(result)

from k8s_connector.cluster_connector import load_cluster
from ai_engine.planner import diagnose_cluster

def diagnose_cluster_from_path(kubeconfig_path: str) -> str:
    load_cluster(kubeconfig_path)
    return diagnose_cluster()
