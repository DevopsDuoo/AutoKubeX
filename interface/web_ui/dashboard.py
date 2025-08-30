import streamlit as st
import tempfile, os, sys
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, ROOT)

from interface.cli import diagnose_cluster_from_path
from ai_engine.autonomous_agent import run_autonomous_diagnosis, AutonomousAgent
from ai_engine.kubectl_converter import KubectlConverter
from models.feedback_db import store_feedback
from k8s_connector.cluster_connector import load_cluster, auto_connect_cluster
from actions.restarter import restart_pod, delete_pod, restart_deployment, bulk_restart_pods, bulk_delete_pods, bulk_restart_deployments, bulk_delete_deployments, restart_all_pods_in_namespace
from actions.scaler import scale_deployment, get_current_replicas, bulk_scale_deployments, scale_all_deployments_in_namespace, scale_deployment_by_percentage
from actions.action_handler import get_all_pods, get_all_deployments, get_problematic_pods, get_all_namespaces
from interface.simple_session import SimpleSessionManager

st.set_page_config("AutoKubeX", layout="wide", page_icon="🔍")

# Initialize simple session manager
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SimpleSessionManager()

session_manager = st.session_state.session_manager

# Initialize session state
for key in ['cluster_connected', 'kubeconfig_path', 'cluster_name', 'auto_restored', 'last_diag', 'last_custom']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['kubeconfig_path', 'cluster_name', 'last_diag', 'last_custom'] else False

# Auto-restore session on startup (only once per session)
if not st.session_state.get('restore_attempted'):
    if session_manager.auto_restore():
        st.success("✅ Previous session restored automatically!")
    else:
        # Try auto-connecting if no previous session
        try:
            result = auto_connect_cluster()
            if result:
                st.session_state.cluster_connected = True
                st.session_state.kubeconfig_path = result['path']
                st.session_state.cluster_name = result['cluster_name']
                st.success(f"🔍 Auto-detected and connected to {result['cluster_name']}")
        except Exception:
            pass  # Silent fail for auto-detection
    st.session_state.restore_attempted = True

st.title("🔍 AutoKubeX")
st.markdown("**AI-powered Kubernetes cluster diagnosis and management**")

# Connection status in header
if st.session_state.cluster_connected:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        cluster_name = st.session_state.cluster_name or "Kubernetes Cluster"
        if st.session_state.get('auto_restored'):
            st.success(f"🔄 Connected: **{cluster_name}** (Session Restored)")
        else:
            st.success(f"✅ Connected: **{cluster_name}**")
    with col2:
        if st.button("🔄 Refresh", type="secondary"):
            st.rerun()
    with col3:
        if st.button("📤 Disconnect", type="secondary"):
            session_manager.clear_session()
            for key in ['cluster_connected', 'kubeconfig_path', 'cluster_name']:
                st.session_state[key] = None if key != 'cluster_connected' else False
            st.rerun()

# Cluster connection section
if not st.session_state.cluster_connected:
    st.markdown("### 🔗 Connect to Kubernetes Cluster")
    
    # Auto-detect kubeconfig from environment
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**🔍 Auto-detect kubeconfig:**")
        if st.button("🔍 Use Environment Kubeconfig", type="primary"):
            try:
                # Try environment variable first
                env_kubeconfig = os.environ.get('KUBECONFIG')
                default_kubeconfig = os.path.expanduser('~/.kube/config')
                
                kubeconfig_path = None
                if env_kubeconfig and os.path.exists(env_kubeconfig):
                    kubeconfig_path = env_kubeconfig
                    st.info(f"Found KUBECONFIG: {env_kubeconfig}")
                elif os.path.exists(default_kubeconfig):
                    kubeconfig_path = default_kubeconfig
                    st.info(f"Found default kubeconfig: {default_kubeconfig}")
                else:
                    st.error("❌ No kubeconfig found in environment or default location")
                
                if kubeconfig_path:
                    with st.spinner("Testing connection..."):
                        try:
                            result = load_cluster(kubeconfig_path)
                            if result and result.get('status') == 'connected':
                                st.session_state.cluster_connected = True
                                st.session_state.kubeconfig_path = kubeconfig_path
                                st.session_state.cluster_name = result.get('cluster_name', 'Kubernetes Cluster')
                                
                                # Save session
                                session_manager.save_session(kubeconfig_path, st.session_state.cluster_name)
                                
                                st.success(f"✅ Connected to {st.session_state.cluster_name}")
                                st.rerun()
                            else:
                                st.error("❌ Failed to connect. Invalid kubeconfig or cluster unreachable.")
                        except Exception as e:
                            st.error(f"❌ Connection error: {str(e)}")
                            with st.expander("🔧 Error Details"):
                                st.code(str(e))
                            
            except Exception as e:
                st.error(f"❌ Auto-detection failed: {e}")
    
    with col2:
        st.markdown("**📝 Manual path:**")
        manual_path = st.text_input("Kubeconfig file path", placeholder="/path/to/kubeconfig")
        if st.button("🔗 Connect") and manual_path:
            try:
                if os.path.exists(manual_path):
                    with st.spinner("Testing connection..."):
                        try:
                            result = load_cluster(manual_path)
                            if result and result.get('status') == 'connected':
                                st.session_state.cluster_connected = True
                                st.session_state.kubeconfig_path = manual_path
                                st.session_state.cluster_name = result.get('cluster_name', 'Kubernetes Cluster')
                                
                                # Save session
                                session_manager.save_session(manual_path, st.session_state.cluster_name)
                                
                                st.success(f"✅ Connected to {st.session_state.cluster_name}")
                                st.rerun()
                            else:
                                st.error("❌ Failed to connect. Invalid kubeconfig or cluster unreachable.")
                        except Exception as e:
                            st.error(f"❌ Connection error: {str(e)}")
                            with st.expander("🔧 Error Details"):
                                st.code(str(e))
                else:
                    st.error("❌ File not found. Please check the path.")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
    
    # Load kubeconfig with file uploader
    with st.expander("📁 Upload Kubeconfig File"):
        uploaded_file = st.file_uploader("Choose kubeconfig file", type=['yaml', 'yml', 'txt'])
        
        if uploaded_file:
            try:
                # Save uploaded file to temp location
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    f.write(uploaded_file.read().decode())
                    temp_path = f.name
                
                st.info(f"📄 Uploaded file saved to: {temp_path}")
                
                # Test connection with detailed error reporting
                with st.spinner("Testing connection..."):
                    try:
                        result = load_cluster(temp_path)
                        if result and result.get('status') == 'connected':
                            st.session_state.cluster_connected = True
                            st.session_state.kubeconfig_path = temp_path
                            st.session_state.cluster_name = result.get('cluster_name', 'Kubernetes Cluster')
                            
                            # Save session
                            session_manager.save_session(temp_path, st.session_state.cluster_name)
                            
                            st.success(f"✅ Connected to {st.session_state.cluster_name}")
                            st.rerun()
                        else:
                            st.error("❌ Failed to connect. Invalid kubeconfig or cluster unreachable.")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
                        # Show more details for debugging
                        with st.expander("🔧 Error Details"):
                            st.code(str(e))
                        
            except Exception as e:
                st.error(f"❌ File processing failed: {e}")
                with st.expander("🔧 Error Details"):
                    st.code(str(e))
    
    # Show detected paths for debugging
    with st.expander("🔧 Debug Info"):
        st.write("**Environment KUBECONFIG:**", os.environ.get('KUBECONFIG', 'Not set'))
        st.write("**Default kubeconfig:**", os.path.expanduser('~/.kube/config'))
        st.write("**Current working directory:**", os.getcwd())
        
        env_kubeconfig = os.environ.get('KUBECONFIG')
        if env_kubeconfig:
            st.write(f"**KUBECONFIG exists:** {os.path.exists(env_kubeconfig)}")
        default_kubeconfig = os.path.expanduser('~/.kube/config')
        st.write(f"**Default config exists:** {os.path.exists(default_kubeconfig)}")
        
        # Quick test with the known working path
        st.markdown("---")
        st.markdown("**🧪 Quick Test with Known Working Path:**")
        working_path = "/Users/hrushi/DevBoxLite/mixed-os-cluster-config.yaml"
        if st.button("🧪 Test Known Working Config"):
            if os.path.exists(working_path):
                try:
                    with st.spinner("Testing known working config..."):
                        result = load_cluster(working_path)
                        if result and result.get('status') == 'connected':
                            st.session_state.cluster_connected = True
                            st.session_state.kubeconfig_path = working_path
                            st.session_state.cluster_name = result.get('cluster_name', 'Mixed OS Cluster')
                            
                            # Save session
                            session_manager.save_session(working_path, st.session_state.cluster_name)
                            
                            st.success(f"✅ Connected using working path!")
                            st.rerun()
                        else:
                            st.error("❌ Even the known working path failed!")
                except Exception as e:
                    st.error(f"❌ Error with working path: {e}")
                    st.code(str(e))
            else:
                st.warning(f"❌ Working path doesn't exist: {working_path}")

# Show quick cluster status if connected
if st.session_state.cluster_connected:
    try:
        problems = get_problematic_pods()
        if problems:
            st.warning(f"⚠️ Found {len(problems)} problematic pods")
        else:
            st.info("✅ All pods appear healthy")
    except Exception:
        pass
    
    # Tabs for functionality
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗣️ Natural Language Deploy", "🤖 Autonomous AI", "🚀 Quick Actions", "📊 Bulk Operations", "⚠️ Problems"])
    
    with tab1:
        st.subheader("🗣️ Natural Language Deployment")
        st.markdown("**Deploy Kubernetes resources using plain English commands**")
        
        # Initialize kubectl converter
        converter = KubectlConverter(st.session_state.kubeconfig_path)
        
        # Examples section
        with st.expander("💡 Example Commands"):
            st.markdown("""
            **Deployment Examples:**
            - `create app using nginx image in default namespace`
            - `deploy redis called cache with 2 replicas`
            - `run pod named test-pod using python:3.9 image`
            - `create deployment web-server using httpd:latest image with port 80`
            
            **Management Examples:**
            - `delete pod test-pod`
            - `scale deployment web-server to 5 replicas`
            - `expose deployment web-server on port 80`
            - `get all pods in kube-system namespace`
            """)
        
        # Natural language input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            nl_command = st.text_input(
                "Enter your deployment command in natural language:",
                placeholder="create app using nginx image in default namespace",
                key="nl_deploy_input"
            )
        
        with col2:
            dry_run = st.checkbox("Dry Run", value=True, help="Preview command without executing")
        
        # Execute button
        if st.button("🚀 Execute Command", type="primary", disabled=not nl_command.strip()):
            if nl_command.strip():
                with st.spinner("Processing natural language command..."):
                    try:
                        result = converter.process_natural_language(nl_command.strip(), dry_run=dry_run)
                        
                        if result.get('success', False):
                            st.success("✅ Command processed successfully!")
                            
                            # Show parsed command
                            with st.expander("🔍 Command Analysis"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("**Parsed Command:**")
                                    parsed = result['parsed']
                                    st.json({
                                        'Action': parsed['action'],
                                        'Resource': parsed['resource_type'], 
                                        'Name': parsed['name'],
                                        'Image': parsed['image'],
                                        'Namespace': parsed['namespace'],
                                        'Replicas': parsed['replicas'],
                                        'Ports': parsed['ports']
                                    })
                                
                                with col2:
                                    st.markdown("**Generated kubectl Command:**")
                                    st.code(result['kubectl_command'])
                            
                            # Show execution result
                            if not dry_run:
                                st.markdown("### 📋 Execution Result")
                                if result['result']['success']:
                                    st.success("✅ Command executed successfully!")
                                    if result['result']['stdout']:
                                        st.code(result['result']['stdout'])
                                else:
                                    st.error("❌ Command failed!")
                                    if result['result']['stderr']:
                                        st.code(result['result']['stderr'])
                            else:
                                st.info("🔍 Dry run completed - no actual changes made")
                                if result['result']['stdout']:
                                    st.code(result['result']['stdout'])
                        
                        else:
                            # Command failed - show detailed error information
                            error_msg = result.get('error', 'Unknown error')
                            
                            # If it's a kubectl execution error, show more details
                            if result.get('result') and not result['result'].get('success', True):
                                kubectl_result = result['result']
                                if kubectl_result.get('stderr'):
                                    error_msg = f"kubectl error: {kubectl_result['stderr']}"
                                elif kubectl_result.get('stdout'):
                                    error_msg = f"kubectl output: {kubectl_result['stdout']}"
                            
                            st.error(f"❌ Could not process command: {error_msg}")
                            
                            # Show debug information
                            with st.expander("🔧 Debug Info"):
                                st.json({
                                    'parsed_command': result.get('parsed', {}),
                                    'kubectl_command': result.get('kubectl_command', 'None generated'),
                                    'full_result': result
                                })
                    
                    except Exception as e:
                        st.error(f"❌ Error processing command: {e}")
        
        # Command history
        if 'nl_command_history' not in st.session_state:
            st.session_state.nl_command_history = []
        
        if st.session_state.nl_command_history:
            st.markdown("### � Recent Commands")
            for i, cmd in enumerate(reversed(st.session_state.nl_command_history[-5:])):
                with st.expander(f"Command {len(st.session_state.nl_command_history) - i}: {cmd[:50]}..."):
                    st.code(cmd)
        
        # Add current command to history
        if nl_command.strip() and st.button("� Save to History"):
            if nl_command not in st.session_state.nl_command_history:
                st.session_state.nl_command_history.append(nl_command)
                st.success("Command saved to history!")
    
    with tab2:
        st.subheader("🤖 Autonomous AI Cluster Management")
        st.markdown("**Let AI automatically detect and fix cluster issues**")
        
        # Safety status
        with st.expander("🛡️ Safety Constraints & Status"):
            try:
                agent = AutonomousAgent(dry_run=True)
                safety_status = agent.get_safety_status()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Actions/Hour", f"{safety_status['actions_last_hour']}/{safety_status['actions_limit']}")
                with col2:
                    st.metric("Deletions/Hour", f"{safety_status['deletions_last_hour']}/{safety_status['deletions_limit']}")
                with col3:
                    st.metric("Total Logged", safety_status['total_logged_actions'])
                
                st.write("**Protected Namespaces:**")
                st.code(", ".join(safety_status['protected_namespaces']))
                
            except Exception as e:
                st.error(f"Failed to get safety status: {e}")
        
        # Autonomous analysis controls
        col1, col2 = st.columns([2, 1])
        
        with col1:
            custom_ai_prompt = st.text_area(
                "Custom AI Analysis Prompt (optional)", 
                placeholder="e.g., 'Focus on performance issues' or 'Check for security problems'",
                height=100,
                help="Guide the AI to focus on specific areas"
            )
        
        with col2:
            st.markdown("**Execution Mode:**")
            execution_mode = st.radio(
                "Mode", 
                ["🧪 Dry Run (Safe)", "🚀 Execute Actions"],
                help="Dry run shows what would be done without executing",
                key="autonomous_mode"
            )
            
            st.markdown("**Monitoring:**")
            auto_monitor = st.checkbox("� Auto-monitor (5 min)", help="Continuously monitor and fix issues")
        
        # Run autonomous analysis
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🤖 Analyze & Fix Issues", type="primary"):
                dry_run = execution_mode == "🧪 Dry Run (Safe)"
                
                with st.spinner("🤖 AI is analyzing your cluster and planning fixes..."):
                    try:
                        result = run_autonomous_diagnosis(
                            user_prompt=custom_ai_prompt if custom_ai_prompt else None,
                            dry_run=dry_run
                        )
                        
                        st.session_state['autonomous_result'] = result
                        
                    except Exception as e:
                        st.error(f"Failed to run autonomous analysis: {e}")
        
        with col2:
            if st.button("🧠 Advanced AI Analysis", type="secondary"):
                with st.spinner("🧠 Running advanced ML analysis..."):
                    try:
                        from ai_engine.k8s_ai_analyzer import run_advanced_cluster_analysis
                        advanced_result = run_advanced_cluster_analysis()
                        st.session_state['advanced_analysis'] = advanced_result
                    except Exception as e:
                        st.error(f"Advanced analysis failed: {e}")
        
        with col3:
            if st.button("🧹 Clear History", type="secondary"):
                keys_to_clear = ['autonomous_result', 'advanced_analysis']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ History cleared")
        
        # Display advanced analysis results
        if st.session_state.get('advanced_analysis'):
            st.markdown("### 🧠 Advanced AI Analysis Results")
            analysis = st.session_state['advanced_analysis']
            
            if 'error' not in analysis:
                # Health Score Display
                health_score = analysis.get('health_score', {})
                if health_score:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        score = health_score.get('overall', 0)
                        grade = health_score.get('grade', 'N/A')
                        status = health_score.get('status', 'Unknown')
                        st.metric("🏥 Overall Health", f"{score}%", f"Grade: {grade}")
                    with col2:
                        st.metric("🔄 Pod Health", f"{health_score.get('pod_health', 0):.1f}%")
                    with col3:
                        st.metric("📦 Deployment Health", f"{health_score.get('deployment_health', 0):.1f}%")
                    with col4:
                        st.metric("⚡ Efficiency", f"{health_score.get('replica_efficiency', 0):.1f}%")
                
                # Critical Issues
                critical_issues = analysis.get('critical_issues', [])
                if critical_issues:
                    st.markdown("**🚨 Critical Issues Detected:**")
                    for issue in critical_issues[:3]:  # Show top 3
                        severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
                        emoji = severity_emoji.get(issue.get('severity', 'low'), '🔵')
                        
                        with st.expander(f"{emoji} {issue.get('type', 'Unknown Issue')} - {issue.get('severity', 'unknown').upper()}"):
                            st.write(f"**Message:** {issue.get('message', 'No details')}")
                            if 'recommended_action' in issue:
                                st.write(f"**Recommended Action:** {issue['recommended_action']}")
                            if 'namespace' in issue:
                                st.write(f"**Namespace:** {issue['namespace']}")
                            if 'affected_pods' in issue:
                                st.write(f"**Affected Pods:** {issue['affected_pods']}")
                
                # Anomalies
                anomalies = analysis.get('anomalies', [])
                if anomalies:
                    st.markdown("**🎯 ML-Detected Anomalies:**")
                    for i, anomaly in enumerate(anomalies[:3], 1):  # Show top 3
                        pod_info = anomaly.get('pod', {})
                        with st.expander(f"🎯 Anomaly #{i}: {pod_info.get('name', 'Unknown Pod')}"):
                            st.write(f"**Pod:** {pod_info.get('name')} in `{pod_info.get('namespace')}`")
                            st.write(f"**Status:** {pod_info.get('status')}")
                            if 'features' in anomaly:
                                st.write(f"**Anomaly Features:** {anomaly['features']}")
                
                # AI Recommendations
                recommendations = analysis.get('recommendations', [])
                if recommendations:
                    st.markdown("**💡 AI Recommendations:**")
                    for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                        priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
                        emoji = priority_emoji.get(rec.get('priority', 'low'), '🔵')
                        
                        with st.expander(f"{emoji} Recommendation #{i}: {rec.get('type', 'Unknown')}"):
                            st.write(f"**Priority:** {rec.get('priority', 'unknown').upper()}")
                            st.write(f"**Message:** {rec.get('message', 'No details')}")
                            if 'actions' in rec:
                                st.write(f"**Suggested Actions:** {', '.join(rec['actions'])}")
                
                # Resource Efficiency
                resource_efficiency = analysis.get('resource_efficiency', {})
                if resource_efficiency:
                    with st.expander("📊 Resource Efficiency Analysis"):
                        if 'namespace_distribution' in resource_efficiency:
                            st.write("**Namespace Distribution:**")
                            for ns, count in resource_efficiency['namespace_distribution'].items():
                                st.write(f"  • {ns}: {count} deployments")
                        
                        if 'pod_health_ratio' in resource_efficiency:
                            st.metric("Pod Health Ratio", f"{resource_efficiency['pod_health_ratio']:.1f}%")
            else:
                st.error(f"Analysis failed: {analysis.get('error')}")
        
        # Show autonomous results
        if st.session_state.get('autonomous_result'):
            result = st.session_state['autonomous_result']
            
            if 'error' in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                # Show AI diagnosis
                st.markdown("### 🧠 AI Analysis")
                with st.expander("Full AI Diagnosis", expanded=True):
                    st.markdown(result['ai_diagnosis'])
                
                # Show action plan
                if result.get('action_plan'):
                    st.markdown(f"### 🛠️ Execution Results ({len(result['action_plan'])} actions)")
                    
                    # Summary metrics
                    execution_results = result['execution_results']
                    success_count = len([a for a in execution_results if a['status'] == 'success'])
                    failed_count = len([a for a in execution_results if a['status'] == 'failed'])
                    blocked_count = len([a for a in execution_results if a['status'] == 'blocked'])
                    simulated_count = len([a for a in execution_results if a['status'] == 'simulated'])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("✅ Successful", success_count)
                    with col2:
                        st.metric("❌ Failed", failed_count)
                    with col3:
                        st.metric("� Blocked", blocked_count)
                    with col4:
                        st.metric("🧪 Simulated", simulated_count)
                    
                    # Detailed results
                    for i, action in enumerate(execution_results, 1):
                        status_emoji = {
                            'success': '✅',
                            'failed': '❌',
                            'blocked': '🚫',
                            'simulated': '🧪'
                        }.get(action['status'], '❓')
                        
                        with st.expander(f"{status_emoji} Action {i}: {action['action']}"):
                            st.write(f"**Reason:** {action['reason']}")
                            st.write(f"**Status:** {action['message']}")
                            st.write(f"**Timestamp:** {action['timestamp']}")
                            
                            if action.get('parameters'):
                                st.write("**Parameters:**")
                                st.json(action['parameters'])
                            
                            if action.get('result'):
                                st.write("**Result:**")
                                st.code(str(action['result']))
                            
                            if action.get('error'):
                                st.error(f"Error: {action['error']}")
                else:
                    st.success("✅ No issues detected - cluster is healthy!")
        
        # Auto-monitoring info
        if auto_monitor:
            st.info("🔄 Auto-monitoring is a future feature - currently shows latest analysis results")
    
    with tab3:
        st.subheader("🚀 Quick Resource Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Pod Operations**")
            namespaces = get_all_namespaces()
            selected_ns = st.selectbox("Namespace", namespaces, key="ns1")
            
            if selected_ns and not selected_ns.startswith("Error"):
                pods = get_all_pods(selected_ns)
                pod_names = [pod['name'] for pod in pods if 'error' not in pod]
                
                if pod_names:
                    selected_pod = st.selectbox("Pod", pod_names)
                    
                    col1a, col1b = st.columns(2)
                    with col1a:
                        if st.button("🔄 Restart"):
                            result = restart_pod(selected_ns, selected_pod)
                            st.write(result)
                    with col1b:
                        if st.button("�️ Delete"):
                            result = delete_pod(selected_ns, selected_pod)
                            st.write(result)
        
        with col2:
            st.write("**Deployment Operations**")
            deployments = get_all_deployments()
            if deployments and 'error' not in deployments[0]:
                dep_options = [f"{d['namespace']}/{d['name']}" for d in deployments if 'error' not in d]
                
                if dep_options:
                    selected_dep = st.selectbox("Deployment", dep_options)
                    
                    if selected_dep:
                        ns, name = selected_dep.split('/')
                        current_replicas = next(d['replicas'] for d in deployments if d['namespace'] == ns and d['name'] == name)
                        
                        new_replicas = st.number_input("Replicas", min_value=0, value=current_replicas)
                        
                        col2a, col2b = st.columns(2)
                        with col2a:
                            if st.button("📈 Scale"):
                                result = scale_deployment(ns, name, new_replicas)
                                st.write(result)
                        with col2b:
                            if st.button("🔄 Restart Deployment"):
                                result = restart_deployment(ns, name)
                                st.write(result)

    with tab4:
        st.subheader("� Bulk Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Pod Operations**")
            namespaces = get_all_namespaces()
            selected_ns = st.selectbox("Namespace", namespaces, key="quick_ns1")
            
            if selected_ns and not selected_ns.startswith("Error"):
                pods = get_all_pods(selected_ns)
                pod_names = [pod['name'] for pod in pods if 'error' not in pod]
                
                if pod_names:
                    selected_pod = st.selectbox("Pod", pod_names, key="quick_pod1")
                    
                    col1a, col1b = st.columns(2)
                    with col1a:
                        if st.button("🔄 Restart", key="quick_restart1"):
                            result = restart_pod(selected_ns, selected_pod)
                            st.write(result)
                    with col1b:
                        if st.button("🗑️ Delete", key="quick_delete1"):
                            result = delete_pod(selected_ns, selected_pod)
                            st.write(result)
        
        with col2:
            st.write("**Deployment Operations**")
            deployments = get_all_deployments()
            if deployments and 'error' not in deployments[0]:
                dep_options = [f"{d['namespace']}/{d['name']}" for d in deployments if 'error' not in d]
                
                if dep_options:
                    selected_dep = st.selectbox("Deployment", dep_options, key="quick_dep1")
                    
                    if selected_dep:
                        ns, name = selected_dep.split('/')
                        current_replicas = next(d['replicas'] for d in deployments if d['namespace'] == ns and d['name'] == name)
                        
                        new_replicas = st.number_input("Replicas", min_value=0, value=current_replicas, key="quick_replicas1")
                        
                        col2a, col2b = st.columns(2)
                        with col2a:
                            if st.button("📈 Scale", key="quick_scale1"):
                                result = scale_deployment(ns, name, new_replicas)
                                st.write(result)
                        with col2b:
                            if st.button("🔄 Restart Deployment", key="quick_restart_dep1"):
                                result = restart_deployment(ns, name)
                                st.write(result)

    with tab4:
        st.subheader("⚠️ Problem Detection & Resolution")
        
        bulk_type = st.radio("Operation Type", ["Pods", "Deployments"], horizontal=True)
        
        if bulk_type == "Pods":
            ns_bulk = st.selectbox("Namespace", get_all_namespaces(), key="bulk_ns")
            if ns_bulk and not ns_bulk.startswith("Error"):
                pods = get_all_pods(ns_bulk)
                pod_names = [pod['name'] for pod in pods if 'error' not in pod]
                
                if pod_names:
                    selected_pods = st.multiselect("Select Pods", pod_names)
                    
                    if selected_pods:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("🔄 Bulk Restart Pods"):
                                results = bulk_restart_pods(ns_bulk, selected_pods)
                                for pod, result in results.items():
                                    st.write(f"{pod}: {result}")
                        
                        with col2:
                            if st.button("🗑️ Bulk Delete Pods"):
                                results = bulk_delete_pods(ns_bulk, selected_pods)
                                for pod, result in results.items():
                                    st.write(f"{pod}: {result}")
                        
                        with col3:
                            if st.button("🔄 Restart All Pods in NS"):
                                results = restart_all_pods_in_namespace(ns_bulk)
                                for item, result in results.items():
                                    st.write(result)
        
        else:  # Deployments
            deployments = get_all_deployments()
            if deployments and 'error' not in deployments[0]:
                ns_deps = {}
                for dep in deployments:
                    if 'error' not in dep:
                        ns = dep['namespace']
                        if ns not in ns_deps:
                            ns_deps[ns] = []
                        ns_deps[ns].append(dep)
                
                selected_ns_dep = st.selectbox("Namespace", list(ns_deps.keys()), key="bulk_dep_ns")
                
                if selected_ns_dep:
                    dep_names = [dep['name'] for dep in ns_deps[selected_ns_dep]]
                    selected_deps = st.multiselect("Select Deployments", dep_names)
                    
                    if selected_deps:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("🔄 Bulk Restart Deployments"):
                                results = bulk_restart_deployments(selected_ns_dep, selected_deps)
                                for dep, result in results.items():
                                    st.write(f"{dep}: {result}")
                        
                        with col2:
                            # Scale configuration
                            st.write("**Bulk Scale Configuration**")
                            scale_configs = {}
                            for dep_name in selected_deps:
                                current = next(d['replicas'] for d in ns_deps[selected_ns_dep] if d['name'] == dep_name)
                                scale_configs[dep_name] = st.number_input(
                                    f"{dep_name} replicas", 
                                    min_value=0, 
                                    value=current,
                                    key=f"scale_{dep_name}"
                                )
                            
                            if st.button("📈 Bulk Scale"):
                                results = bulk_scale_deployments(selected_ns_dep, scale_configs)
                                for dep, result in results.items():
                                    st.write(f"{dep}: {result}")
    
    with tab5:
        st.subheader("⚠️ Problem Detection & Resolution")
        
        try:
            problems = get_problematic_pods()
            
            if problems:
                st.error(f"Found {len(problems)} problematic pods")
                
                for pod in problems:
                    with st.expander(f"❌ {pod['namespace']}/{pod['name']} - {pod['phase']}"):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.write(f"**Status:** {pod['phase']}")
                            st.write(f"**Ready:** {'Yes' if pod.get('ready', False) else 'No'}")
                        
                        with col2:
                            st.write(f"**Restarts:** {pod.get('restarts', 0)}")
                            st.write(f"**Node:** {pod.get('node', 'Unknown')}")
                        
                        with col3:
                            if st.button("🔄 Fix", key=f"fix_{pod['namespace']}_{pod['name']}"):
                                result = restart_pod(pod['namespace'], pod['name'])
                                st.write(result)
            else:
                st.success("✅ No problematic pods found! Cluster is healthy.")
                
        except Exception as e:
            st.error(f"Failed to check for problems: {e}")

# Footer info
if st.session_state.cluster_connected:
    st.markdown("---")
    st.markdown("💡 **Tip:** Your session is automatically saved. You can refresh the browser without losing connection.")
