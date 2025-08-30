from kubernetes import config
import os
import sys

# Add project root to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, ROOT)

from k8s_connector.kubeconfig_detector import find_working_kubeconfig


def load_cluster(kubeconfig_path: str = None):
    """
    Load Kubernetes cluster configuration
    If no path provided, auto-detect from environment
    """
    try:
        if kubeconfig_path:
            # Use provided path
            config.load_kube_config(config_file=kubeconfig_path)
            print(f"[+] Connected to cluster using: {kubeconfig_path}")
            return {"status": "connected", "cluster_name": "Kubernetes Cluster", "path": kubeconfig_path}
        else:
            # Auto-detect kubeconfig
            working_config = find_working_kubeconfig()
            if working_config:
                config.load_kube_config(config_file=working_config['path'])
                cluster_name = working_config['validation']['current_context'] or "Kubernetes Cluster"
                print(f"[+] Auto-detected and connected to cluster: {cluster_name}")
                print(f"[+] Using kubeconfig: {working_config['path']}")
                return {
                    "status": "connected", 
                    "cluster_name": cluster_name,
                    "path": working_config['path'],
                    "source": working_config['source']
                }
            else:
                print("[!] No working kubeconfig found")
                return None
                
    except Exception as e:
        print(f"[!] Failed to load kubeconfig: {e}")
        raise


def auto_connect_cluster():
    """
    Automatically connect to cluster using detected kubeconfig
    """
    return load_cluster()
