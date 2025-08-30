import streamlit as st
import tempfile, os, sys
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, ROOT)

from interface.cli import diagnose_cluster_from_path
from models.feedback_db import store_feedback
from k8s_connector.cluster_connector import load_cluster
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
        if st.button("🔴 Disconnect", type="secondary"):
            session_manager.clear_session()
            for key in ['cluster_connected', 'kubeconfig_path', 'cluster_name', 'auto_restored', 'last_diag', 'last_custom']:
                st.session_state[key] = None if key in ['kubeconfig_path', 'cluster_name', 'last_diag', 'last_custom'] else False
            st.rerun()
else:
    # Upload section - simple and clean
    st.header("🚀 Connect to Your Cluster")
    
    uploaded = st.file_uploader("Upload your kubeconfig file", type=['yaml', 'yml', 'config'])
    cluster_name = st.text_input("Cluster Name (optional)", placeholder="My Kubernetes Cluster")
    
    if uploaded and st.button("🔗 Connect", type="primary"):
        try:
            # Test connection first
            with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_file:
                temp_file.write(uploaded.read())
                temp_path = temp_file.name
            
            with st.spinner("Testing connection..."):
                load_cluster(temp_path)
                st.success("✅ Connection successful!")
            
            # Save session
            uploaded.seek(0)  # Reset file pointer
            if session_manager.save_session(uploaded.read(), cluster_name):
                st.session_state.cluster_connected = True
                st.session_state.kubeconfig_path = session_manager.kubeconfig_file
                st.session_state.cluster_name = cluster_name or "Kubernetes Cluster"
                st.session_state.auto_restored = False
                st.rerun()
            
            os.unlink(temp_path)  # Cleanup temp file
            
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")
            if 'temp_path' in locals():
                os.unlink(temp_path)

# Main interface - only show if connected
if st.session_state.cluster_connected:
    
    # Quick status bar
    try:
        problems = get_problematic_pods()
        if problems:
            st.warning(f"⚠️ {len(problems)} problematic pods detected")
        else:
            st.info("✅ All pods appear healthy")
    except Exception:
        pass
    
    # Tabs for functionality
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 AI Diagnosis", "🚀 Quick Actions", "📊 Bulk Operations", "⚠️ Problems"])
    
    with tab1:
        st.subheader("AI Cluster Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Run Full Diagnosis", type="primary"):
                with st.spinner("Analyzing cluster..."):
                    try:
                        st.session_state.last_diag = diagnose_cluster_from_path(st.session_state.kubeconfig_path)
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
        
        with col2:
            custom_prompt = st.text_input("Ask a specific question about your cluster")
            if st.button("🤔 Ask AI") and custom_prompt.strip():
                with st.spinner("Thinking..."):
                    try:
                        st.session_state.last_custom = diagnose_cluster_from_path(
                            st.session_state.kubeconfig_path, custom_prompt=custom_prompt
                        )
                    except Exception as e:
                        st.error(f"Query failed: {e}")
        
        # Show results
        if st.session_state.last_diag:
            st.markdown("### 🎯 Full Diagnosis Results")
            st.markdown(st.session_state.last_diag["ai_response"])
        
        if st.session_state.last_custom:
            st.markdown("### 💬 Custom Query Results")
            st.markdown(st.session_state.last_custom["ai_response"])
    
    with tab2:
        st.subheader("Quick Resource Actions")
        
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
                        if st.button("🗑️ Delete"):
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
    
    with tab3:
        st.subheader("Bulk Operations")
        
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
    
    with tab4:
        st.subheader("Problem Detection & Resolution")
        
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
