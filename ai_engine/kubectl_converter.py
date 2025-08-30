#!/usr/bin/env python3
"""
Natural Language to Kubectl Command Converter
Converts natural language instructions into kubectl commands and executes them.
"""

import re
import yaml
import subprocess
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class KubectlConverter:
    """Convert natural language to kubectl commands and execute them"""
    
    def __init__(self, kubeconfig_path: str = None):
        self.kubeconfig_path = kubeconfig_path
        self.kubectl_base = ["kubectl"]
        if kubeconfig_path:
            self.kubectl_base.extend(["--kubeconfig", kubeconfig_path])
    
    def parse_natural_language(self, command: str) -> Dict:
        """Parse natural language command into structured data"""
        command = command.lower().strip()
        
        result = {
            'action': None,
            'resource_type': None,
            'name': None,
            'image': None,
            'namespace': 'default',
            'ports': [],
            'replicas': 1,
            'env_vars': {},
            'labels': {},
            'service_type': 'ClusterIP',
            'raw_command': command
        }
        
        # Detect action
        if any(word in command for word in ['scale', 'resize']):
            result['action'] = 'scale'
        elif any(word in command for word in ['create', 'deploy', 'run', 'make', 'start']):
            result['action'] = 'create'
        elif any(word in command for word in ['delete', 'remove', 'destroy']):
            result['action'] = 'delete'
        elif any(word in command for word in ['expose', 'service']):
            result['action'] = 'expose'
        elif any(word in command for word in ['get', 'list', 'show']):
            result['action'] = 'get'
        
        # Detect resource type
        if any(word in command for word in ['pod', 'app', 'application']):
            result['resource_type'] = 'pod'
        elif any(word in command for word in ['deployment', 'deploy']):
            result['resource_type'] = 'deployment'
        elif any(word in command for word in ['service', 'svc']):
            result['resource_type'] = 'service'
        elif any(word in command for word in ['configmap', 'config']):
            result['resource_type'] = 'configmap'
        elif any(word in command for word in ['secret']):
            result['resource_type'] = 'secret'
        
        # Extract image
        image_patterns = [
            r'(?:using|with|from)\s+([a-zA-Z0-9\-_./:]+(?::[a-zA-Z0-9\-_.]+)?)\s*(?:image)?',
            r'image\s+([a-zA-Z0-9\-_./:]+(?::[a-zA-Z0-9\-_.]+)?)',
            r'([a-zA-Z0-9\-_./:]+(?::[a-zA-Z0-9\-_.]+)?)\s+image'
        ]
        for pattern in image_patterns:
            image_match = re.search(pattern, command)
            if image_match:
                potential_image = image_match.group(1)
                # Make sure it's not a number (replicas) or other non-image word
                if not potential_image.isdigit() and potential_image not in ['with', 'using', 'and', 'the']:
                    result['image'] = potential_image
                    break
        
        # Extract name
        name_patterns = [
            r'(?:named|called)\s+([a-zA-Z0-9\-]+)',
            r'(?:deployment|pod|app)\s+([a-zA-Z0-9\-]+)',
            r'create\s+([a-zA-Z0-9\-]+)',
            r'run\s+([a-zA-Z0-9\-]+)',
            r'deploy\s+([a-zA-Z0-9\-]+)(?:\s+called|\s+named|$)'
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, command)
            if name_match:
                potential_name = name_match.group(1)
                # Make sure it's not an image name or keyword
                if not potential_name in ['using', 'with', 'from', 'image', 'in', 'on'] and ':' not in potential_name:
                    result['name'] = potential_name
                    break
        
        # If no name found, generate from image
        if not result['name'] and result['image']:
            result['name'] = result['image'].split('/')[-1].split(':')[0].replace('_', '-').replace('.', '-')[:20]
        
        # Extract namespace
        namespace_match = re.search(r'(?:in|namespace)\s+([a-zA-Z0-9\-]+)\s+namespace', command)
        if namespace_match:
            result['namespace'] = namespace_match.group(1)
        
        # Extract ports
        port_matches = re.findall(r'port\s+(\d+)', command)
        if port_matches:
            result['ports'] = [int(p) for p in port_matches]
        
        # Extract replicas
        replica_match = re.search(r'(\d+)\s+(?:replicas?|instances?|copies)', command)
        if replica_match:
            result['replicas'] = int(replica_match.group(1))
        
        return result
    
    def generate_kubectl_command(self, parsed: Dict) -> List[str]:
        """Generate kubectl command from parsed natural language"""
        
        if parsed['action'] == 'create':
            return self._generate_create_command(parsed)
        elif parsed['action'] == 'delete':
            return self._generate_delete_command(parsed)
        elif parsed['action'] == 'scale':
            return self._generate_scale_command(parsed)
        elif parsed['action'] == 'expose':
            return self._generate_expose_command(parsed)
        elif parsed['action'] == 'get':
            return self._generate_get_command(parsed)
        else:
            return []
    
    def _generate_create_command(self, parsed: Dict) -> List[str]:
        """Generate create command"""
        if not parsed['image']:
            return []  # Can't create without an image
            
        if parsed['resource_type'] == 'pod':
            cmd = self.kubectl_base + [
                "run", parsed['name'],
                "--image", parsed['image'],
                "--namespace", parsed['namespace']
            ]
            if parsed['ports']:
                cmd.extend(["--port", str(parsed['ports'][0])])
            return cmd
        
        elif parsed['resource_type'] == 'deployment':
            cmd = self.kubectl_base + [
                "create", "deployment", parsed['name'],
                "--image", parsed['image'],
                "--namespace", parsed['namespace']
            ]
            if parsed['replicas'] > 1:
                cmd.extend(["--replicas", str(parsed['replicas'])])
            return cmd
        
        return []
    
    def _generate_delete_command(self, parsed: Dict) -> List[str]:
        """Generate delete command"""
        resource_type = parsed['resource_type'] or 'pod'
        name = parsed['name'] or '--all'
        return self.kubectl_base + [
            "delete", resource_type,
            name,
            "--namespace", parsed['namespace']
        ]
    
    def _generate_scale_command(self, parsed: Dict) -> List[str]:
        """Generate scale command"""
        resource_type = parsed['resource_type'] or 'deployment'
        if not parsed['name']:
            return []
        return self.kubectl_base + [
            "scale", f"{resource_type}/{parsed['name']}",
            f"--replicas={parsed['replicas']}",
            "--namespace", parsed['namespace']
        ]
    
    def _generate_expose_command(self, parsed: Dict) -> List[str]:
        """Generate expose command"""
        resource_type = parsed['resource_type'] or 'deployment'
        if not parsed['name']:
            return []
        cmd = self.kubectl_base + [
            "expose", resource_type,
            parsed['name'],
            "--namespace", parsed['namespace']
        ]
        if parsed['ports']:
            cmd.extend(["--port", str(parsed['ports'][0])])
        return cmd
    
    def _generate_get_command(self, parsed: Dict) -> List[str]:
        """Generate get command"""
        cmd = self.kubectl_base + ["get", parsed['resource_type'] or "pods"]
        if parsed['namespace'] != 'default':
            cmd.extend(["--namespace", parsed['namespace']])
        return cmd
    
    def execute_kubectl(self, command: List[str], dry_run: bool = False) -> Dict:
        """Execute kubectl command"""
        if dry_run:
            command.append("--dry-run=client")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(command)
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out after 30 seconds',
                'command': ' '.join(command)
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'command': ' '.join(command)
            }
    
    def process_natural_language(self, nl_command: str, dry_run: bool = False) -> Dict:
        """Main method to process natural language command"""
        
        # Parse the natural language
        parsed = self.parse_natural_language(nl_command)
        
        # Generate kubectl command
        kubectl_cmd = self.generate_kubectl_command(parsed)
        
        if not kubectl_cmd:
            return {
                'success': False,
                'error': 'Could not understand the command',
                'parsed': parsed,
                'kubectl_command': None,
                'result': None
            }
        
        # Execute the command
        result = self.execute_kubectl(kubectl_cmd, dry_run)
        
        return {
            'success': result['success'],
            'parsed': parsed,
            'kubectl_command': ' '.join(kubectl_cmd),
            'result': result,
            'dry_run': dry_run
        }


def demo_converter():
    """Demo the natural language converter"""
    converter = KubectlConverter()
    
    test_commands = [
        "create app using nginx image in default namespace",
        "deploy nginx called my-web-app with 3 replicas",
        "run pod named test-pod using python:3.9 image",
        "create deployment web-server using httpd image with port 80",
        "delete pod test-pod",
        "scale deployment my-web-app to 5 replicas",
        "get all pods",
        "expose deployment web-server on port 80"
    ]
    
    print("🚀 Natural Language to Kubectl Converter Demo")
    print("=" * 50)
    
    for cmd in test_commands:
        print(f"\n📝 Natural Language: '{cmd}'")
        result = converter.process_natural_language(cmd, dry_run=True)
        
        if result['success']:
            print(f"✅ Kubectl Command: {result['kubectl_command']}")
            print(f"🔍 Parsed: {result['parsed']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    demo_converter()
