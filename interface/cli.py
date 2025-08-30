import typer
import json
from typing import Optional
from k8s_connector.cluster_connector import load_cluster
from ai_engine.planner import diagnose_cluster
from ai_engine.autonomous_agent import run_autonomous_diagnosis, run_continuous_monitoring, AutonomousAgent
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


@app.command()
def autonomous_fix(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Custom analysis prompt"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Dry run mode (default) or execute actions"),
    show_safety: bool = typer.Option(False, "--show-safety", help="Show safety constraints")
):
    """Run autonomous AI diagnosis and fixes."""
    load_cluster(kubeconfig_path)
    
    if show_safety:
        agent = AutonomousAgent(dry_run=True)
        safety_status = agent.get_safety_status()
        typer.echo("🛡️  Safety Constraints:")
        typer.echo(f"   Actions per hour: {safety_status['actions_last_hour']}/{safety_status['actions_limit']}")
        typer.echo(f"   Deletions per hour: {safety_status['deletions_last_hour']}/{safety_status['deletions_limit']}")
        typer.echo(f"   Protected namespaces: {', '.join(safety_status['protected_namespaces'])}")
        typer.echo("")
    
    mode = "🧪 DRY RUN MODE" if dry_run else "🚀 EXECUTION MODE"
    typer.echo(f"{mode} - Running autonomous cluster analysis...")
    
    result = run_autonomous_diagnosis(prompt, dry_run=dry_run)
    
    if 'error' in result:
        typer.echo(f"❌ Error: {result['error']}")
        return
    
    typer.echo("\n🤖 AI Diagnosis:")
    typer.echo("-" * 60)
    typer.echo(result['ai_diagnosis'])
    
    if result.get('action_plan'):
        typer.echo(f"\n🛠️  Action Plan ({len(result['action_plan'])} actions):")
        typer.echo("-" * 60)
        
        for i, action in enumerate(result['execution_results'], 1):
            status_emoji = {
                'success': '✅',
                'failed': '❌', 
                'blocked': '🚫',
                'simulated': '🧪'
            }.get(action['status'], '❓')
            
            typer.echo(f"{i}. {status_emoji} {action['action']}")
            typer.echo(f"   Reason: {action['reason']}")
            typer.echo(f"   Status: {action['message']}")
            if action.get('parameters'):
                typer.echo(f"   Params: {action['parameters']}")
            typer.echo("")
    else:
        typer.echo("\n✅ No issues detected - cluster is healthy!")


@app.command()
def autonomous_monitor(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    interval: int = typer.Option(5, "--interval", help="Check interval in minutes"),
    cycles: int = typer.Option(10, "--cycles", help="Number of monitoring cycles"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Dry run mode (default) or execute actions")
):
    """Run continuous autonomous monitoring and fixing."""
    load_cluster(kubeconfig_path)
    
    mode = "🧪 DRY RUN MODE" if dry_run else "🚀 EXECUTION MODE"
    typer.echo(f"{mode} - Starting continuous autonomous monitoring...")
    typer.echo(f"📊 Interval: {interval} minutes, Cycles: {cycles}")
    
    history = run_continuous_monitoring(
        interval_minutes=interval,
        max_iterations=cycles,
        dry_run=dry_run
    )
    
    typer.echo(f"\n📋 Monitoring completed. Total actions taken: {len(history)}")
    
    if history:
        typer.echo("\n🔍 Action Summary:")
        for action in history[-5:]:  # Show last 5 actions
            status_emoji = {
                'success': '✅',
                'failed': '❌',
                'blocked': '🚫', 
                'simulated': '🧪'
            }.get(action['status'], '❓')
            typer.echo(f"  {status_emoji} {action['action']} - {action['message']}")


@app.command()
def ai_analysis(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    output_format: str = typer.Option("summary", "--format", "-f", help="Output format: summary, detailed, json")
):
    """Run advanced AI analysis on the cluster using ML libraries."""
    load_cluster(kubeconfig_path)
    
    try:
        from ai_engine.k8s_ai_analyzer import run_advanced_cluster_analysis
        
        typer.echo("🧠 Running advanced AI analysis...")
        analysis = run_advanced_cluster_analysis()
        
        if 'error' in analysis:
            typer.echo(f"❌ Analysis failed: {analysis['error']}")
            return
        
        if output_format == "json":
            typer.echo(json.dumps(analysis, indent=2))
            return
        
        # Summary format
        typer.echo("\n🧠 Advanced AI Analysis Results")
        typer.echo("=" * 50)
        
        # Health score
        health_score = analysis.get('health_score', {})
        if health_score:
            typer.echo(f"\n🏥 Overall Health: {health_score.get('overall', 0):.1f}% (Grade: {health_score.get('grade', 'N/A')})")
            typer.echo(f"   Pod Health: {health_score.get('pod_health', 0):.1f}%")
            typer.echo(f"   Deployment Health: {health_score.get('deployment_health', 0):.1f}%")
            typer.echo(f"   Status: {health_score.get('status', 'Unknown')}")
        
        # Critical issues
        critical_issues = analysis.get('critical_issues', [])
        if critical_issues:
            typer.echo(f"\n🚨 Critical Issues ({len(critical_issues)}):")
            for i, issue in enumerate(critical_issues[:5], 1):
                severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
                emoji = severity_emoji.get(issue.get('severity', 'low'), '🔵')
                typer.echo(f"  {i}. {emoji} {issue.get('type', 'Unknown')}: {issue.get('message', 'No details')}")
                if 'recommended_action' in issue:
                    typer.echo(f"     → Action: {issue['recommended_action']}")
        
        # Anomalies
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            typer.echo(f"\n🎯 ML-Detected Anomalies ({len(anomalies)}):")
            for i, anomaly in enumerate(anomalies[:3], 1):
                pod_info = anomaly.get('pod', {})
                typer.echo(f"  {i}. Pod: {pod_info.get('name')} in {pod_info.get('namespace')}")
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            typer.echo(f"\n💡 AI Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:3], 1):
                priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
                emoji = priority_emoji.get(rec.get('priority', 'low'), '🔵')
                typer.echo(f"  {i}. {emoji} {rec.get('message', 'No details')}")
        
        if output_format == "detailed":
            typer.echo(f"\n📋 Full Analysis:")
            typer.echo(json.dumps(analysis, indent=2))
        
    except Exception as e:
        typer.echo(f"❌ AI analysis failed: {e}")


@app.command() 
def predictive_analysis(
    kubeconfig_path: str = typer.Option(..., "--kubeconfig"),
    deployment: str = typer.Option(None, "--deployment", "-d", help="Specific deployment to analyze"),
    namespace: str = typer.Option("default", "--namespace", "-n"),
):
    """Run predictive analysis for cluster management."""
    load_cluster(kubeconfig_path)
    
    try:
        from ai_engine.autonomous_agent import AutonomousAgent
        
        agent = AutonomousAgent(dry_run=True)
        insights = agent.get_predictive_insights()
        
        typer.echo("🔮 Predictive Analysis Results")
        typer.echo("=" * 40)
        
        if 'error' in insights:
            typer.echo(f"❌ Analysis failed: {insights['error']}")
            return
        
        # Predicted issues
        predicted_issues = insights.get('predicted_issues', [])
        if predicted_issues:
            typer.echo(f"\n⚠️ Predicted Issues ({len(predicted_issues)}):")
            for i, issue in enumerate(predicted_issues, 1):
                typer.echo(f"  {i}. {issue.get('type', 'Unknown')} - Confidence: {issue.get('confidence', 0):.0%}")
                typer.echo(f"     Timeline: {issue.get('timeline', 'Unknown')}")
                typer.echo(f"     Resource: {issue.get('resource', 'Unknown')}")
                typer.echo(f"     Action: {issue.get('action', 'None')}")
        
        # Scaling recommendations
        scaling_recs = insights.get('scaling_recommendations', [])
        if scaling_recs:
            typer.echo(f"\n📊 Scaling Recommendations ({len(scaling_recs)}):")
            for i, rec in enumerate(scaling_recs, 1):
                typer.echo(f"  {i}. {rec.get('recommendation', 'No details')} - Confidence: {rec.get('confidence', 0):.0%}")
        
        # If specific deployment requested, run intelligent scaling
        if deployment:
            typer.echo(f"\n🎯 Intelligent Scaling Analysis for {namespace}/{deployment}")
            try:
                from actions.ai_action_handler import run_intelligent_scaling
                scaling_result = run_intelligent_scaling(deployment, namespace)
                
                if 'error' not in scaling_result:
                    rec = scaling_result.get('recommendation', {})
                    typer.echo(f"   Recommendation: {rec.get('action', 'Unknown')}")
                    typer.echo(f"   Reason: {rec.get('reason', 'No reason')}")
                    typer.echo(f"   Confidence: {scaling_result.get('confidence', 0):.0%}")
                    if 'suggested_replicas' in rec:
                        typer.echo(f"   Suggested Replicas: {rec['suggested_replicas']}")
                else:
                    typer.echo(f"   ❌ Error: {scaling_result['error']}")
            except Exception as e:
                typer.echo(f"   ❌ Intelligent scaling failed: {e}")
        
    except Exception as e:
        typer.echo(f"❌ Predictive analysis failed: {e}")


def diagnose_cluster_from_path(kubeconfig_path: str, custom_prompt: str = None):
    """
    Load cluster, run diagnose_cluster, and return a dict of:
      prompt, cluster_snapshot, ai_response
    """
    load_cluster(kubeconfig_path)
    return diagnose_cluster(prompt_override=custom_prompt)
