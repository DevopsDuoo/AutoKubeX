import typer
from typing import Optional
from k8s_connector.cluster_connector import load_cluster
from ai_engine.planner import diagnose_cluster
from actions.restarter import restart_pod, delete_pod, restart_deployment, bulk_restart_pods, bulk_delete_pods, bulk_restart_deployments, bulk_delete_deployments, restart_all_pods_in_namespace
from actions.scaler import scale_deployment, get_current_replicas, list_deployments, bulk_scale_deployments, scale_all_deployments_in_namespace, scale_deployment_by_percentage, bulk_scale_deployments_by_percentage
from actions.action_handler import get_all_pods, get_all_deployments, get_problematic_pods

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

@app.command()
def restart_pod_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    pod_name: str = typer.Option(..., "--pod", "-p")
):
    """Restart a specific pod."""
    load_cluster(kubeconfig_path)
    result = restart_pod(namespace, pod_name)
    typer.echo(result)

@app.command()
def delete_pod_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    pod_name: str = typer.Option(..., "--pod", "-p")
):
    """Delete a specific pod."""
    load_cluster(kubeconfig_path)
    result = delete_pod(namespace, pod_name)
    typer.echo(result)

@app.command()
def restart_deployment_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    deployment_name: str = typer.Option(..., "--deployment", "-d")
):
    """Restart all pods in a deployment."""
    load_cluster(kubeconfig_path)
    result = restart_deployment(namespace, deployment_name)
    typer.echo(result)

@app.command()
def scale_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    deployment: str = typer.Option(..., "--deployment", "-d"),
    replicas: int = typer.Option(..., "--replicas", "-r")
):
    """Scale a deployment to specified number of replicas."""
    load_cluster(kubeconfig_path)
    result = scale_deployment(namespace, deployment, replicas)
    typer.echo(result)

@app.command()
def list_pods(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: Optional[str] = typer.Option(None, "--namespace", "-n")
):
    """List all pods with their status."""
    load_cluster(kubeconfig_path)
    pods = get_all_pods(namespace)
    
    typer.echo("\n📋 Pod Status:")
    typer.echo("-" * 80)
    for pod in pods:
        if 'error' in pod:
            typer.echo(f"❌ {pod['error']}")
            continue
        
        status = "✅" if pod['ready'] else "❌"
        typer.echo(f"{status} {pod['namespace']}/{pod['name']} | {pod['phase']} | Restarts: {pod['restarts']}")

@app.command()
def list_deployments_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: Optional[str] = typer.Option(None, "--namespace", "-n")
):
    """List all deployments with their status."""
    load_cluster(kubeconfig_path)
    deployments = get_all_deployments(namespace)
    
    typer.echo("\n🚀 Deployment Status:")
    typer.echo("-" * 80)
    for dep in deployments:
        if 'error' in dep:
            typer.echo(f"❌ {dep['error']}")
            continue
        
        status = "✅" if dep['ready_replicas'] == dep['replicas'] else "❌"
        typer.echo(f"{status} {dep['namespace']}/{dep['name']} | {dep['ready_replicas']}/{dep['replicas']} ready")

@app.command()
def problems(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig")
):
    """List problematic pods that need attention."""
    load_cluster(kubeconfig_path)
    pods = get_problematic_pods()
    
    if not pods:
        typer.echo("✅ No problematic pods found!")
        return
    
    typer.echo("\n⚠️  Problematic Pods:")
    typer.echo("-" * 80)
    for pod in pods:
        typer.echo(f"❌ {pod['namespace']}/{pod['name']} | {pod['phase']} | Restarts: {pod['restarts']}")


@app.command()
def bulk_restart_pods_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    pod_names: str = typer.Option(..., "--pods", "-p", help="Comma-separated list of pod names")
):
    """Restart multiple pods in bulk."""
    load_cluster(kubeconfig_path)
    pod_list = [name.strip() for name in pod_names.split(",")]
    results = bulk_restart_pods(namespace, pod_list)
    
    typer.echo("\n🔄 Bulk Pod Restart Results:")
    typer.echo("-" * 80)
    for pod_name, result in results.items():
        typer.echo(f"{result}")


@app.command()
def bulk_delete_pods_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    pod_names: str = typer.Option(..., "--pods", "-p", help="Comma-separated list of pod names")
):
    """Delete multiple pods in bulk."""
    load_cluster(kubeconfig_path)
    pod_list = [name.strip() for name in pod_names.split(",")]
    results = bulk_delete_pods(namespace, pod_list)
    
    typer.echo("\n🗑️  Bulk Pod Delete Results:")
    typer.echo("-" * 80)
    for pod_name, result in results.items():
        typer.echo(f"{result}")


@app.command()
def bulk_restart_deployments_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    deployment_names: str = typer.Option(..., "--deployments", "-d", help="Comma-separated list of deployment names")
):
    """Restart multiple deployments in bulk."""
    load_cluster(kubeconfig_path)
    deployment_list = [name.strip() for name in deployment_names.split(",")]
    results = bulk_restart_deployments(namespace, deployment_list)
    
    typer.echo("\n🔄 Bulk Deployment Restart Results:")
    typer.echo("-" * 80)
    for deployment_name, result in results.items():
        typer.echo(f"{result}")


@app.command()
def bulk_delete_deployments_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    deployment_names: str = typer.Option(..., "--deployments", "-d", help="Comma-separated list of deployment names")
):
    """Delete multiple deployments in bulk."""
    load_cluster(kubeconfig_path)
    deployment_list = [name.strip() for name in deployment_names.split(",")]
    results = bulk_delete_deployments(namespace, deployment_list)
    
    typer.echo("\n🗑️  Bulk Deployment Delete Results:")
    typer.echo("-" * 80)
    for deployment_name, result in results.items():
        typer.echo(f"{result}")


@app.command()
def bulk_scale_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    deployments_config: str = typer.Option(..., "--config", "-c", help="deployment1:replicas1,deployment2:replicas2")
):
    """Scale multiple deployments in bulk. Format: app1:3,app2:5,app3:0"""
    load_cluster(kubeconfig_path)
    
    config_dict = {}
    for item in deployments_config.split(","):
        if ":" in item:
            deployment, replicas = item.strip().split(":")
            config_dict[deployment] = int(replicas)
    
    if not config_dict:
        typer.echo("❌ Invalid configuration format. Use: app1:3,app2:5,app3:0")
        return
    
    results = bulk_scale_deployments(namespace, config_dict)
    
    typer.echo("\n📏 Bulk Scale Results:")
    typer.echo("-" * 80)
    for deployment_name, result in results.items():
        typer.echo(f"{result}")


@app.command()
def scale_all_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    replicas: int = typer.Option(..., "--replicas", "-r"),
    label_selector: Optional[str] = typer.Option(None, "--selector", "-s")
):
    """Scale all deployments in a namespace to the same number of replicas."""
    load_cluster(kubeconfig_path)
    results = scale_all_deployments_in_namespace(namespace, replicas, label_selector)
    
    typer.echo(f"\n📏 Scale All Deployments to {replicas} replicas:")
    typer.echo("-" * 80)
    for deployment_name, result in results.items():
        typer.echo(f"{result}")


@app.command()
def scale_by_percentage_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    deployment: str = typer.Option(..., "--deployment", "-d"),
    percentage: float = typer.Option(..., "--percentage", "-p", help="Scaling factor (e.g., 1.5 for 50% increase, 0.5 for 50% decrease)")
):
    """Scale a deployment by percentage."""
    load_cluster(kubeconfig_path)
    result = scale_deployment_by_percentage(namespace, deployment, percentage)
    typer.echo(result)


@app.command()
def restart_namespace_cmd(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    namespace: str = typer.Option(..., "--namespace", "-n"),
    label_selector: Optional[str] = typer.Option(None, "--selector", "-s")
):
    """Restart all pods in a namespace (optionally filtered by label selector)."""
    load_cluster(kubeconfig_path)
    results = restart_all_pods_in_namespace(namespace, label_selector)
    
    typer.echo(f"\n🔄 Restart All Pods in Namespace {namespace}:")
    typer.echo("-" * 80)
    for pod_name, result in results.items():
        typer.echo(f"{result}")


def diagnose_cluster_from_path(kubeconfig_path: str, custom_prompt: str = None):
    """
    Load cluster, run diagnose_cluster, and return a dict of:
      prompt, cluster_snapshot, ai_response
    """
    load_cluster(kubeconfig_path)
    return diagnose_cluster(prompt_override=custom_prompt)
