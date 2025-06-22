import streamlit as st
import tempfile
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from interface.cli import diagnose_cluster_from_path

st.set_page_config(page_title="AutoKubeX - AI Cluster Diagnosis", layout="centered")

st.title("🔍 AutoKubeX - AI Cluster Diagnosis")
st.write("📁 Upload your kubeconfig file to run cluster health analysis")

uploaded_file = st.file_uploader("Choose kubeconfig file")

if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")
    
    # Write uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    if st.button("🔍 Run Diagnosis"):
        with st.spinner("Running AI diagnostics..."):
            try:
                result = diagnose_cluster_from_path(tmp_path)
                st.success("✅ Cluster Diagnosed Successfully!")
                st.markdown("### 📋 Cluster Diagnosis Report")
                st.markdown(result)
            except Exception as e:
                st.error(f"❌ Diagnosis Failed: {e}")

    # Optional: Clean up temp file later (not on same run or will break on rerun)
    # os.remove(tmp_path)
