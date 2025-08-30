import streamlit as st
import os
import json
import tempfile
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from k8s_connector.cluster_connector import load_cluster

class SimpleSessionManager:
    """Simplified session manager that just works without complex UI"""
    
    def __init__(self):
        self.session_file = os.path.join(tempfile.gettempdir(), "autokubex_session.json")
        self.kubeconfig_file = os.path.join(tempfile.gettempdir(), "autokubex_kubeconfig.yaml")
    
    def save_session(self, kubeconfig_content: bytes, cluster_name: str = None) -> bool:
        """Save session data simply"""
        try:
            # Save kubeconfig
            with open(self.kubeconfig_file, 'wb') as f:
                f.write(kubeconfig_content)
            
            # Save session info
            session_data = {
                'cluster_name': cluster_name or 'Kubernetes Cluster',
                'saved_at': datetime.now().isoformat(),
                'kubeconfig_path': self.kubeconfig_file
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            
            return True
        except Exception as e:
            st.error(f"Failed to save session: {e}")
            return False
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """Load session data if available"""
        try:
            if not os.path.exists(self.session_file) or not os.path.exists(self.kubeconfig_file):
                return None
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is still valid (48 hours)
            saved_at = datetime.fromisoformat(session_data['saved_at'])
            if datetime.now() - saved_at > timedelta(hours=48):
                self.clear_session()
                return None
            
            return session_data
        except Exception:
            return None
    
    def test_connection(self) -> bool:
        """Test if kubeconfig still works"""
        try:
            if not os.path.exists(self.kubeconfig_file):
                return False
            load_cluster(self.kubeconfig_file)
            return True
        except Exception:
            return False
    
    def clear_session(self) -> bool:
        """Clear session files"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            if os.path.exists(self.kubeconfig_file):
                os.remove(self.kubeconfig_file)
            return True
        except Exception:
            return False
    
    def auto_restore(self) -> bool:
        """Automatically restore session if available"""
        session_data = self.load_session()
        if not session_data:
            return False
        
        if self.test_connection():
            # Restore to session state
            st.session_state.cluster_connected = True
            st.session_state.kubeconfig_path = self.kubeconfig_file
            st.session_state.cluster_name = session_data['cluster_name']
            st.session_state.auto_restored = True
            return True
        else:
            # Clear invalid session
            self.clear_session()
            return False
