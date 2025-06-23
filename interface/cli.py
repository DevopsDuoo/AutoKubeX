import typer
from k8s_connector.cluster_connector import load_cluster
from ai_engine.planner import diagnose_cluster

app = typer.Typer()

@app.command()
def connect(cluster_config: str):
    """Connect to a Kubernetes cluster."""
    load_cluster(cluster_config)
    typer.echo("✔️ Connected.")

@app.command()
def diagnose(kubeconfig_path: str = typer.Option(..., "--kubeconfig")):
    """Run AI diagnosis from CLI."""
    load_cluster(kubeconfig_path)
    result = diagnose_cluster()
    typer.echo(result["ai_response"])

def diagnose_cluster_from_path(kubeconfig_path: str, custom_prompt: str = None):
    """
    Load cluster, run diagnose_cluster, and return a dict of:
      prompt, cluster_snapshot, ai_response
    """
    load_cluster(kubeconfig_path)
    return diagnose_cluster(prompt_override=custom_prompt)
