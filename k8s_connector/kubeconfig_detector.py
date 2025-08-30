#!/usr/bin/env python3
"""
Kubeconfig Auto-Detection Utility
Automatically detects and validates kubeconfig files
"""

import os
import yaml
from typing import Optional, List, Dict, Any


def detect_kubeconfig_paths() -> List[str]:
    """
    Detect potential kubeconfig file paths from various sources
    """
    paths = []
    
    # 1. Environment variable KUBECONFIG
    env_kubeconfig = os.environ.get('KUBECONFIG')
    if env_kubeconfig:
        # Handle multiple paths separated by ':'
        for path in env_kubeconfig.split(':'):
            if path.strip():
                paths.append(os.path.expanduser(path.strip()))
    
    # 2. Default kubectl location
    default_path = os.path.expanduser('~/.kube/config')
    if default_path not in paths:
        paths.append(default_path)
    
    # 3. Common development locations
    common_paths = [
        '/Users/hrushi/DevBoxLite/mixed-os-cluster-config.yaml',
        '/Users/hrushi/.kube/config',
        './kubeconfig',
        './config',
        '~/.k8s/config',
        '/tmp/kubeconfig'
    ]
    
    for path in common_paths:
        expanded_path = os.path.expanduser(path)
        if expanded_path not in paths:
            paths.append(expanded_path)
    
    return paths


def validate_kubeconfig(path: str) -> Dict[str, Any]:
    """
    Validate a kubeconfig file and extract basic info
    """
    result = {
        'valid': False,
        'path': path,
        'exists': False,
        'clusters': [],
        'contexts': [],
        'current_context': None,
        'error': None
    }
    
    try:
        if not os.path.exists(path):
            result['error'] = f"File does not exist: {path}"
            return result
        
        result['exists'] = True
        
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            result['error'] = "Invalid YAML structure"
            return result
        
        # Extract cluster info
        clusters = config.get('clusters', [])
        result['clusters'] = [c.get('name') for c in clusters if isinstance(c, dict)]
        
        # Extract context info
        contexts = config.get('contexts', [])
        result['contexts'] = [c.get('name') for c in contexts if isinstance(c, dict)]
        
        # Current context
        result['current_context'] = config.get('current-context')
        
        # Basic validation
        if clusters and contexts:
            result['valid'] = True
        else:
            result['error'] = "Missing clusters or contexts in kubeconfig"
    
    except yaml.YAMLError as e:
        result['error'] = f"YAML parsing error: {e}"
    except Exception as e:
        result['error'] = f"Validation error: {e}"
    
    return result


def find_working_kubeconfig() -> Optional[Dict[str, Any]]:
    """
    Find the first working kubeconfig from detected paths
    """
    paths = detect_kubeconfig_paths()
    
    for path in paths:
        validation = validate_kubeconfig(path)
        if validation['valid']:
            return {
                'path': path,
                'validation': validation,
                'source': 'environment' if path == os.environ.get('KUBECONFIG') else 'default' if '/.kube/config' in path else 'detected'
            }
    
    return None


def get_kubeconfig_status() -> Dict[str, Any]:
    """
    Get comprehensive status of kubeconfig detection
    """
    paths = detect_kubeconfig_paths()
    validations = []
    
    for path in paths:
        validation = validate_kubeconfig(path)
        validations.append(validation)
    
    working = find_working_kubeconfig()
    
    return {
        'detected_paths': paths,
        'validations': validations,
        'working_config': working,
        'environment_kubeconfig': os.environ.get('KUBECONFIG'),
        'default_exists': os.path.exists(os.path.expanduser('~/.kube/config'))
    }


if __name__ == "__main__":
    print("🔍 AutoKubeX Kubeconfig Detection")
    print("=" * 50)
    
    status = get_kubeconfig_status()
    
    print(f"Environment KUBECONFIG: {status['environment_kubeconfig']}")
    print(f"Default config exists: {status['default_exists']}")
    print()
    
    print("Detected paths:")
    for i, path in enumerate(status['detected_paths'], 1):
        print(f"  {i}. {path}")
    print()
    
    print("Validation results:")
    for validation in status['validations']:
        path = validation['path']
        exists = "✅" if validation['exists'] else "❌"
        valid = "✅" if validation['valid'] else "❌"
        
        print(f"  {exists} {valid} {path}")
        if validation['error']:
            print(f"       Error: {validation['error']}")
        elif validation['valid']:
            print(f"       Clusters: {', '.join(validation['clusters'])}")
            print(f"       Current context: {validation['current_context']}")
    print()
    
    working = status['working_config']
    if working:
        print(f"✅ Working kubeconfig found:")
        print(f"   Path: {working['path']}")
        print(f"   Source: {working['source']}")
        print(f"   Clusters: {', '.join(working['validation']['clusters'])}")
    else:
        print("❌ No working kubeconfig found")
