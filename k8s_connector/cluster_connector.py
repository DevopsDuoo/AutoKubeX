from kubernetes import config

def load_cluster(kubeconfig_path: str):
    try:
        config.load_kube_config(config_file=kubeconfig_path)
        print(f"[+] Connected to cluster using: {kubeconfig_path}")
    except Exception as e:
        print(f"[!] Failed to load kubeconfig: {e}")
        raise
