# ai_engine/safety_manager.py
"""
Safety Manager for Autonomous Kubernetes Operations
Ensures AI actions are safe and controlled
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import json
import os

class SafetyManager:
    """Manages safety constraints for autonomous AI operations"""
    
    def __init__(self):
        self.safety_log_path = "/tmp/autokubex_safety_log.json"
        self.max_actions_per_hour = 20
        self.max_deletions_per_hour = 5
        self.protected_namespaces = ['kube-system', 'kube-public', 'istio-system']
        self.protected_resources = ['coredns', 'kube-proxy', 'etcd']
        self.action_history = self._load_action_history()
    
    def _load_action_history(self) -> List[Dict]:
        """Load recent action history from file"""
        if os.path.exists(self.safety_log_path):
            try:
                with open(self.safety_log_path, 'r') as f:
                    history = json.load(f)
                # Filter to last 24 hours
                cutoff = datetime.now() - timedelta(hours=24)
                return [
                    action for action in history 
                    if datetime.fromisoformat(action['timestamp']) > cutoff
                ]
            except:
                pass
        return []
    
    def _save_action_history(self):
        """Save action history to file"""
        try:
            os.makedirs(os.path.dirname(self.safety_log_path), exist_ok=True)
            with open(self.safety_log_path, 'w') as f:
                json.dump(self.action_history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save safety log: {e}")
    
    def validate_action(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate if an action is safe to execute
        
        Returns:
            (is_safe, reason)
        """
        action_name = action.get('action', '')
        params = action.get('parameters', {})
        namespace = params.get('namespace', '')
        
        # Check 1: Protected namespaces
        if namespace in self.protected_namespaces:
            return False, f"❌ Cannot modify protected namespace: {namespace}"
        
        # Check 2: Protected resources
        resource_name = params.get('pod_name', params.get('deployment', ''))
        if any(protected in resource_name.lower() for protected in self.protected_resources):
            return False, f"❌ Cannot modify protected resource: {resource_name}"
        
        # Check 3: Rate limiting
        recent_actions = self._count_recent_actions()
        if recent_actions >= self.max_actions_per_hour:
            return False, f"❌ Rate limit exceeded: {recent_actions}/{self.max_actions_per_hour} actions per hour"
        
        # Check 4: Deletion limits
        if 'delete' in action_name.lower():
            recent_deletions = self._count_recent_deletions()
            if recent_deletions >= self.max_deletions_per_hour:
                return False, f"❌ Deletion limit exceeded: {recent_deletions}/{self.max_deletions_per_hour} deletions per hour"
        
        # Check 5: Bulk operation limits
        if 'bulk' in action_name.lower():
            resource_list = params.get('pod_names', params.get('deployment_names', []))
            if len(resource_list) > 10:
                return False, f"❌ Bulk operation too large: {len(resource_list)} resources (max 10)"
        
        # Check 6: Scaling limits
        if 'scale' in action_name.lower():
            replicas = params.get('replicas', 0)
            if replicas > 20:
                return False, f"❌ Scale target too high: {replicas} replicas (max 20)"
            
            percentage = params.get('percentage', 0)
            if percentage > 300:  # Max 3x scaling
                return False, f"❌ Scale percentage too high: {percentage}% (max 300%)"
        
        return True, "✅ Action is safe to execute"
    
    def _count_recent_actions(self) -> int:
        """Count actions in the last hour"""
        cutoff = datetime.now() - timedelta(hours=1)
        return len([
            action for action in self.action_history
            if datetime.fromisoformat(action['timestamp']) > cutoff
        ])
    
    def _count_recent_deletions(self) -> int:
        """Count deletion actions in the last hour"""
        cutoff = datetime.now() - timedelta(hours=1)
        return len([
            action for action in self.action_history
            if datetime.fromisoformat(action['timestamp']) > cutoff
            and 'delete' in action.get('action', '').lower()
        ])
    
    def log_action(self, action: Dict[str, Any], result: Dict[str, Any]):
        """Log an executed action for safety tracking"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action.get('action'),
            'parameters': action.get('parameters'),
            'status': result.get('status'),
            'reason': action.get('reason')
        }
        
        self.action_history.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.action_history) > 100:
            self.action_history = self.action_history[-100:]
        
        self._save_action_history()
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status and limits"""
        recent_actions = self._count_recent_actions()
        recent_deletions = self._count_recent_deletions()
        
        return {
            'actions_last_hour': recent_actions,
            'actions_limit': self.max_actions_per_hour,
            'deletions_last_hour': recent_deletions,
            'deletions_limit': self.max_deletions_per_hour,
            'protected_namespaces': self.protected_namespaces,
            'protected_resources': self.protected_resources,
            'total_logged_actions': len(self.action_history)
        }


def create_safety_manager() -> SafetyManager:
    """Factory function to create a safety manager"""
    return SafetyManager()
