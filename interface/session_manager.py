import streamlit as st
import os
import json
import hashlib
import tempfile
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from k8s_connector.cluster_connector import load_cluster

class SessionManager:
    """Manages persistent sessions for AutoKubeX web UI"""
    
    def __init__(self):
        self.session_dir = os.path.join(tempfile.gettempdir(), "autokubex_sessions")
        self.ensure_session_dir()
        
    def ensure_session_dir(self):
        """Create session directory if it doesn't exist"""
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)
    
    def get_session_id(self) -> str:
        """Get or create a unique session ID"""
        if 'session_id' not in st.session_state:
            # Create unique session ID based on timestamp and random data
            session_data = f"{datetime.now().isoformat()}_{os.urandom(16).hex()}"
            st.session_state.session_id = hashlib.md5(session_data.encode()).hexdigest()
        return st.session_state.session_id
    
    def get_session_file_path(self, session_id: str) -> str:
        """Get the file path for a session"""
        return os.path.join(self.session_dir, f"session_{session_id}.json")
    
    def save_session_data(self, data: Dict[str, Any]) -> bool:
        """Save session data to file"""
        try:
            session_id = self.get_session_id()
            session_file = self.get_session_file_path(session_id)
            
            # Add metadata
            data_with_metadata = {
                'session_id': session_id,
                'last_updated': datetime.now().isoformat(),
                'data': data
            }
            
            with open(session_file, 'w') as f:
                json.dump(data_with_metadata, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Failed to save session: {e}")
            return False
    
    def load_session_data(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load session data from file"""
        try:
            if session_id is None:
                session_id = self.get_session_id()
            
            session_file = self.get_session_file_path(session_id)
            
            if not os.path.exists(session_file):
                return None
                
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired (24 hours)
            last_updated = datetime.fromisoformat(session_data['last_updated'])
            if datetime.now() - last_updated > timedelta(hours=24):
                self.cleanup_session(session_id)
                return None
            
            return session_data['data']
        except Exception as e:
            st.error(f"Failed to load session: {e}")
            return None
    
    def cleanup_session(self, session_id: str) -> bool:
        """Remove session file"""
        try:
            session_file = self.get_session_file_path(session_id)
            if os.path.exists(session_file):
                os.remove(session_file)
            return True
        except Exception as e:
            st.error(f"Failed to cleanup session: {e}")
            return False
    
    def list_active_sessions(self) -> Dict[str, Dict[str, str]]:
        """List all active sessions with metadata"""
        sessions = {}
        try:
            for filename in os.listdir(self.session_dir):
                if filename.startswith('session_') and filename.endswith('.json'):
                    session_id = filename.replace('session_', '').replace('.json', '')
                    session_file = os.path.join(self.session_dir, filename)
                    
                    try:
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                        
                        # Check if session is expired
                        last_updated = datetime.fromisoformat(session_data['last_updated'])
                        if datetime.now() - last_updated > timedelta(hours=24):
                            self.cleanup_session(session_id)
                            continue
                        
                        sessions[session_id] = {
                            'last_updated': session_data['last_updated'],
                            'has_cluster': 'kubeconfig_path' in session_data.get('data', {}),
                            'cluster_name': session_data.get('data', {}).get('cluster_name', 'Unknown')
                        }
                    except Exception:
                        continue
        except Exception as e:
            st.error(f"Failed to list sessions: {e}")
        
        return sessions
    
    def restore_cluster_connection(self, kubeconfig_path: str) -> bool:
        """Restore cluster connection from saved session"""
        try:
            if os.path.exists(kubeconfig_path):
                load_cluster(kubeconfig_path)
                return True
            else:
                st.warning("Saved kubeconfig file no longer exists. Please re-upload.")
                return False
        except Exception as e:
            st.error(f"Failed to restore cluster connection: {e}")
            return False
    
    def init_session_state(self):
        """Initialize all session state variables"""
        defaults = {
            'last_diag': None,
            'last_custom': None,
            'cluster_connected': False,
            'kubeconfig_path': None,
            'cluster_name': None,
            'connection_time': None,
            'session_started': False
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def start_session(self, kubeconfig_content: bytes, cluster_name: str = None) -> bool:
        """Start a new session with cluster connection"""
        try:
            # Save kubeconfig to persistent location
            session_id = self.get_session_id()
            kubeconfig_path = os.path.join(self.session_dir, f"kubeconfig_{session_id}.yaml")
            
            with open(kubeconfig_path, 'wb') as f:
                f.write(kubeconfig_content)
            
            # Test cluster connection
            load_cluster(kubeconfig_path)
            
            # Save session data
            session_data = {
                'kubeconfig_path': kubeconfig_path,
                'cluster_name': cluster_name or 'Kubernetes Cluster',
                'connection_time': datetime.now().isoformat()
            }
            
            if self.save_session_data(session_data):
                # Update session state
                st.session_state.cluster_connected = True
                st.session_state.kubeconfig_path = kubeconfig_path
                st.session_state.cluster_name = session_data['cluster_name']
                st.session_state.connection_time = session_data['connection_time']
                st.session_state.session_started = True
                return True
            
            return False
        except Exception as e:
            st.error(f"Failed to start session: {e}")
            return False
    
    def restore_session(self) -> bool:
        """Restore session from saved data"""
        try:
            session_data = self.load_session_data()
            if not session_data:
                return False
            
            kubeconfig_path = session_data.get('kubeconfig_path')
            if kubeconfig_path and self.restore_cluster_connection(kubeconfig_path):
                # Restore session state
                st.session_state.cluster_connected = True
                st.session_state.kubeconfig_path = kubeconfig_path
                st.session_state.cluster_name = session_data.get('cluster_name', 'Kubernetes Cluster')
                st.session_state.connection_time = session_data.get('connection_time')
                st.session_state.session_started = True
                return True
            
            return False
        except Exception as e:
            st.error(f"Failed to restore session: {e}")
            return False
    
    def end_session(self) -> bool:
        """End current session and cleanup"""
        try:
            session_id = self.get_session_id()
            
            # Cleanup session file
            self.cleanup_session(session_id)
            
            # Cleanup kubeconfig file
            if st.session_state.get('kubeconfig_path'):
                kubeconfig_path = st.session_state.kubeconfig_path
                if os.path.exists(kubeconfig_path):
                    os.remove(kubeconfig_path)
            
            # Reset session state
            for key in ['cluster_connected', 'kubeconfig_path', 'cluster_name', 
                       'connection_time', 'session_started', 'last_diag', 'last_custom']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Force rerun to refresh UI
            st.rerun()
            return True
        except Exception as e:
            st.error(f"Failed to end session: {e}")
            return False
    
    def get_session_info(self) -> Dict[str, str]:
        """Get current session information"""
        return {
            'session_id': self.get_session_id(),
            'cluster_name': st.session_state.get('cluster_name', 'Not connected'),
            'connection_time': st.session_state.get('connection_time', 'Not connected'),
            'connected': str(st.session_state.get('cluster_connected', False))
        }
