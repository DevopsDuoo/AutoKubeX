import streamlit as st
import tempfile, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, ROOT)

from interface.cli import diagnose_cluster_from_path
from models.feedback_db import store_feedback

st.set_page_config("AutoKubeX", layout="centered", page_icon="🔍")
st.title("🔍 AutoKubeX")
st.markdown("**AI-powered Kubernetes cluster diagnosis**")

# --- Upload kubeconfig ---
uploaded = st.file_uploader("Choose your kubeconfig file")
if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as f:
        f.write(uploaded.read())
        st.session_state.tmp_kube = f.name
    st.success("Uploaded.")

# Initialize session state slots
if 'last_diag' not in st.session_state:
    st.session_state['last_diag'] = None
if 'last_custom' not in st.session_state:
    st.session_state['last_custom'] = None

# --- Standard Diagnosis ---
if st.session_state.get('tmp_kube') and st.button("🚀 Run Cluster Diagnosis"):
    with st.spinner("Diagnosing..."):
        try:
            st.session_state['last_diag'] = diagnose_cluster_from_path(st.session_state.tmp_kube)
        except Exception as e:
            st.error(e)

if st.session_state['last_diag']:
    out = st.session_state['last_diag']
    st.markdown("### 📋 Report")
    st.markdown(out["ai_response"])

    choice = st.selectbox("Was this helpful?", ["", "👍 Yes", "👎 No"], key="diag_fb")
    if choice and st.button("Submit Feedback", key="submit_diag_fb"):
        store_feedback(
            out["prompt"],
            out["cluster_snapshot"],
            out["ai_response"],
            1 if choice == "👍 Yes" else 0
        )
        st.success("Thanks for your feedback!")

st.markdown("---")

# --- Custom Prompt ---
st.markdown("### 💬 Custom Prompt")
ask = st.text_area("Your question about the cluster")
if st.session_state.get('tmp_kube') and st.button("🧠 Ask AI"):
    with st.spinner("Thinking..."):
        try:
            st.session_state['last_custom'] = diagnose_cluster_from_path(
                st.session_state.tmp_kube, custom_prompt=ask
            )
        except Exception as e:
            st.error(e)

if st.session_state['last_custom']:
    out = st.session_state['last_custom']
    st.markdown("### 💡 AI Says")
    st.markdown(out["ai_response"])

    choice = st.selectbox("Was this helpful?", ["", "👍 Yes", "👎 No"], key="custom_fb")
    if choice and st.button("Submit Feedback", key="submit_custom_fb"):
        store_feedback(
            out["prompt"],
            out["cluster_snapshot"],
            out["ai_response"],
            1 if choice == "👍 Yes" else 0
        )
        st.success("Thanks for your feedback!")
