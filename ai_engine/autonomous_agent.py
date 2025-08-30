# ai_engine/autonomous_agent.py
"""
Autonomous AI Agent for Kubernetes Cluster Management
Analyzes cluster state and automatically applies fixes
"""

import re
import json
import yaml
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from ai_engine.prompt_templates import AUTONOMOUS_DIAGNOSIS_TEMPLATE, EXECUTION_PLAN_TEMPLATE
from ai_engine.safety_manager import SafetyManager
from ai_engine.k8s_ai_analyzer import KubernetesAIAnalyzer, run_advanced_cluster_analysis
from ai_engine.local_ai_engine import LocalAIEngine, run_local_ai_analysis, extract_local_actions
from k8s_connector.kube_api import get_cluster_summary
from actions.action_handler import get_all_pods, get_problematic_pods
from actions.restarter import restart_pod, delete_pod, restart_deployment, bulk_restart_pods, bulk_delete_pods
from actions.scaler import scale_deployment, scale_deployment_by_percentage, bulk_scale_deployments
from actions.reconfigurer import update_pod_resources, apply_hpa


class AutonomousAgent:
    """AI Agent that can diagnose and automatically fix Kubernetes issues"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.execution_log = []
        self.safety_manager = SafetyManager()
        self.ai_analyzer = KubernetesAIAnalyzer()
        self.local_ai = LocalAIEngine()  # Local AI instead of Gemini
        self.available_actions = {
            'restart_pod': restart_pod,
            'delete_pod': delete_pod,
            'restart_deployment': restart_deployment,
            'scale_deployment': scale_deployment,
            'scale_deployment_by_percentage': scale_deployment_by_percentage,
            'bulk_restart_pods': bulk_restart_pods,
            'bulk_delete_pods': bulk_delete_pods,
            'bulk_scale_deployments': bulk_scale_deployments,
            'update_pod_resources': update_pod_resources,
            'apply_hpa': apply_hpa
        }
    
    def analyze_and_fix(self, user_prompt: str = None) -> Dict[str, Any]:
        """Main method: Analyze cluster and automatically apply fixes"""
        try:
            # Step 1: Get cluster state
            cluster_info = get_cluster_summary()
            pod_info = get_problematic_pods()  # Focus on problematic pods
            
            # Step 2: Advanced AI Analysis
            ai_analysis = self.ai_analyzer.analyze_cluster_health()
            
            # Step 3: AI Diagnosis with autonomous capabilities
            diagnosis = self._get_ai_diagnosis(cluster_info, pod_info, user_prompt, ai_analysis)
            
            # Step 4: Extract action plan from AI response
            action_plan = self._extract_action_plan(diagnosis['ai_response'])
            
            # Step 5: Execute actions (if not dry run)
            execution_results = self._execute_action_plan(action_plan)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cluster_snapshot': cluster_info,
                'ai_analysis': ai_analysis,
                'ai_diagnosis': diagnosis['ai_response'],
                'action_plan': action_plan,
                'execution_results': execution_results,
                'dry_run': self.dry_run
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'dry_run': self.dry_run
            }
    
    def _get_ai_diagnosis(self, cluster_info: str, pod_info: List[Dict], user_prompt: str = None, ai_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get AI diagnosis using local AI engine instead of external API"""
        
        try:
            # Use local AI engine for analysis
            ai_response = self.local_ai.analyze_and_recommend(
                cluster_info=cluster_info,
                pod_info=pod_info,
                user_prompt=user_prompt
            )
            
            return {
                "prompt": user_prompt or "Autonomous cluster analysis",
                "ai_response": ai_response,
                "source": "local_ai_engine"
            }
            
        except Exception as e:
            # Fallback to basic analysis if local AI fails
            fallback_response = self._generate_fallback_response(cluster_info, pod_info, ai_analysis)
            return {
                "prompt": user_prompt or "Fallback analysis",
                "ai_response": fallback_response,
                "source": "fallback_analysis",
                "error": str(e)
            }
    
    def _generate_fallback_response(self, cluster_info: str, pod_info: List[Dict], ai_analysis: Dict = None) -> str:
        """Generate fallback response when AI engine fails"""
        
        # Basic cluster assessment
        total_pods = len(pod_info) if pod_info else 0
        problematic_pods = len([p for p in pod_info if p.get('status', '').lower() != 'running']) if pod_info else 0
        
        health_percentage = ((total_pods - problematic_pods) / total_pods * 100) if total_pods > 0 else 100
        
        response = f"""## 🤖 AUTONOMOUS CLUSTER ANALYSIS

**📊 Cluster Health**: {health_percentage:.1f}%
- Total Pods: {total_pods}
- Problematic Pods: {problematic_pods}
- Running Pods: {total_pods - problematic_pods}

## 🛠️ AUTONOMOUS ACTION PLAN
"""
        
        # Generate actions based on issues
        action_count = 0
        
        if problematic_pods > 0:
            if problematic_pods <= 3:
                action_count += 1
                response += f"""
ACTION_{action_count}:
  action: restart_pod
  reasoning: {problematic_pods} pods are not running properly
  priority: high"""
            else:
                action_count += 1
                response += f"""
ACTION_{action_count}:
  action: bulk_restart_pods
  reasoning: Multiple pods ({problematic_pods}) need restart
  priority: high"""
        
        # Add optimization actions based on AI analysis
        if ai_analysis:
            recommendations = ai_analysis.get('recommendations', [])
            for rec in recommendations[:2]:  # Add up to 2 more actions
                if action_count >= 3:
                    break
                
                rec_actions = rec.get('actions', ['investigate'])
                for action in rec_actions[:1]:
                    action_count += 1
                    response += f"""
ACTION_{action_count}:
  action: {action}
  reasoning: {rec.get('message', 'Optimization recommended')}
  priority: {rec.get('priority', 'medium')}"""
        
        # Default monitoring action if no issues
        if action_count == 0:
            response += """
ACTION_1:
  action: monitor_cluster
  reasoning: Cluster appears healthy, continue monitoring
  priority: low"""
        
        return response
    
    def _extract_action_plan(self, ai_response: str) -> List[Dict[str, Any]]:
        """Extract structured action plan from local AI response"""
        
        # Use local AI engine's action extraction
        actions = extract_local_actions(ai_response)
        
        # If local extraction fails, use pattern matching fallback
        if not actions:
            actions = self._extract_actions_fallback(ai_response)
        
        return actions
    
    def _extract_actions_fallback(self, ai_response: str) -> List[Dict[str, Any]]:
        """Fallback action extraction using pattern matching"""
        actions = []
        
        # Look for ACTION_N blocks in the AI response
        action_pattern = r'ACTION_(\d+):\s*\n\s*action:\s*(\w+).*?\n\s*(?:namespace:\s*(\w+).*?\n\s*)?reasoning:\s*([^\n]+).*?\n\s*priority:\s*(\w+)'
        matches = re.findall(action_pattern, ai_response, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            action_id, action, namespace, reasoning, priority = match
            
            actions.append({
                'action': action.strip(),
                'namespace': namespace.strip() if namespace else 'default',
                'reasoning': reasoning.strip(),
                'reason': reasoning.strip(),  # Add 'reason' alias for consistency
                'priority': priority.strip(),
                'confidence': 0.8,
                'source': 'local_ai',
                'parameters': {}  # Add empty parameters dict
            })
        
        # Look for simple action mentions if no structured format found
        if not actions:
            simple_patterns = [
                (r'restart.*(pod|deployment)', 'restart_pod'),
                (r'delete.*pod', 'delete_pod'),
                (r'scale.*deployment', 'scale_deployment'),
                (r'bulk.*restart', 'bulk_restart_pods'),
                (r'apply.*hpa', 'apply_hpa')
            ]
            
            for pattern, action in simple_patterns:
                if re.search(pattern, ai_response, re.IGNORECASE):
                    actions.append({
                        'action': action,
                        'namespace': 'default',
                        'reasoning': f'Local AI detected need for {action}',
                        'reason': f'Local AI detected need for {action}',  # Add 'reason' alias
                        'priority': 'medium',
                        'confidence': 0.6,
                        'source': 'pattern_match',
                        'parameters': {}  # Add empty parameters dict
                    })
                    break  # Only add one action to avoid duplicates
        
        return actions
    
    def _execute_action_plan(self, action_plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute the action plan with safety validation"""
        results = []
        
        for action_item in action_plan:
            action_name = action_item['action']
            params = action_item.get('parameters', {})
            reason = action_item.get('reason', action_item.get('reasoning', 'No reason provided'))
            
            result = {
                'action': action_name,
                'parameters': params,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'dry_run': self.dry_run
            }
            
            # Safety validation
            is_safe, safety_reason = self.safety_manager.validate_action(action_item)
            if not is_safe:
                result['status'] = 'blocked'
                result['message'] = f"Blocked by safety manager: {safety_reason}"
                results.append(result)
                continue
            
            if self.dry_run:
                result['status'] = 'simulated'
                result['message'] = f"Would execute {action_name} with params: {params}"
                result['safety_check'] = 'passed'
            else:
                try:
                    # Execute the actual action
                    action_func = self.available_actions[action_name]
                    
                    # Call the function with parameters
                    if params:
                        action_result = action_func(**params)
                    else:
                        action_result = action_func()
                    
                    result['status'] = 'success'
                    result['result'] = action_result
                    result['message'] = f"Successfully executed {action_name}"
                    result['safety_check'] = 'passed'
                    
                    # Log successful action
                    self.safety_manager.log_action(action_item, result)
                    
                except Exception as e:
                    result['status'] = 'failed'
                    result['error'] = str(e)
                    result['message'] = f"Failed to execute {action_name}: {e}"
                    
                    # Log failed action
                    self.safety_manager.log_action(action_item, result)
            
            results.append(result)
            self.execution_log.append(result)
        
        return results
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of all autonomous actions taken"""
        return self.execution_log
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status and constraints"""
        return self.safety_manager.get_safety_status()
    
    def clear_execution_history(self):
        """Clear the execution history"""
        self.execution_log = []
    
    def run_advanced_analysis(self) -> Dict[str, Any]:
        """Run advanced AI-powered cluster analysis"""
        try:
            return self.ai_analyzer.analyze_cluster_health()
        except Exception as e:
            return {
                'error': f'Advanced analysis failed: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_predictive_insights(self) -> Dict[str, Any]:
        """Get predictive insights for cluster management"""
        try:
            return self.ai_analyzer.get_predictive_insights()
        except Exception as e:
            return {
                'error': f'Predictive analysis failed: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def run_advanced_analysis(self) -> Dict[str, Any]:
        """Run advanced AI-powered cluster analysis"""
        try:
            return self.ai_analyzer.analyze_cluster_health()
        except Exception as e:
            return {
                'error': f'Advanced analysis failed: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_predictive_insights(self) -> Dict[str, Any]:
        """Get predictive insights for cluster management"""
        try:
            return self.ai_analyzer.get_predictive_insights()
        except Exception as e:
            return {
                'error': f'Predictive analysis failed: {e}',
                'timestamp': datetime.now().isoformat()
            }


def run_autonomous_diagnosis(user_prompt: str = None, dry_run: bool = True) -> Dict[str, Any]:
    """
    Run autonomous cluster diagnosis and fixes
    
    Args:
        user_prompt: Optional user-specific prompt
        dry_run: If True, only simulate actions without executing them
    
    Returns:
        Dictionary with diagnosis results and execution log
    """
    agent = AutonomousAgent(dry_run=dry_run)
    return agent.analyze_and_fix(user_prompt)


def run_continuous_monitoring(interval_minutes: int = 5, max_iterations: int = 10, dry_run: bool = True):
    """
    Run continuous autonomous monitoring and fixing
    
    Args:
        interval_minutes: How often to check the cluster
        max_iterations: Maximum number of monitoring cycles
        dry_run: If True, only simulate actions
    """
    agent = AutonomousAgent(dry_run=dry_run)
    
    print(f"🤖 Starting autonomous monitoring (dry_run={dry_run})")
    print(f"📊 Checking every {interval_minutes} minutes for {max_iterations} cycles")
    
    for i in range(max_iterations):
        print(f"\n🔍 Monitoring cycle {i+1}/{max_iterations}")
        
        result = agent.analyze_and_fix()
        
        if result.get('action_plan'):
            print(f"🛠️  Found {len(result['action_plan'])} actions to take")
            for action in result['execution_results']:
                print(f"   • {action['action']}: {action['status']} - {action['message']}")
        else:
            print("✅ No issues detected, cluster is healthy")
        
        if i < max_iterations - 1:
            print(f"😴 Sleeping for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)
    
    print(f"\n📋 Total autonomous actions taken: {len(agent.execution_log)}")
    return agent.get_execution_history()
