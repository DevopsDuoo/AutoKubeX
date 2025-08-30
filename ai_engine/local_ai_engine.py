# ai_engine/local_ai_engine.py
"""
Local AI Engine - Self-contained autonomous AI without external APIs
Replaces Gemini API with intelligent local analysis
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

from .k8s_ai_analyzer import KubernetesAIAnalyzer


class LocalAIEngine:
    """
    Local AI engine that provides intelligent analysis without external API calls
    Uses advanced ML libraries and rule-based intelligence
    """
    
    def __init__(self):
        self.ai_analyzer = KubernetesAIAnalyzer()
        self.analysis_templates = {
            'health_assessment': self._health_assessment_template,
            'issue_diagnosis': self._issue_diagnosis_template,
            'action_planning': self._action_planning_template,
            'optimization_suggestions': self._optimization_template
        }
    
    def analyze_and_recommend(self, cluster_info: Dict, pod_info: List[Dict], user_prompt: str = None) -> str:
        """
        Main AI analysis method that provides intelligent recommendations
        without external API dependencies
        """
        # Run advanced AI analysis
        ai_analysis = self.ai_analyzer.analyze_cluster_health()
        
        # Generate intelligent response based on analysis
        response = self._generate_intelligent_response(cluster_info, pod_info, ai_analysis, user_prompt)
        
        return response
    
    def _generate_intelligent_response(self, cluster_info: Dict, pod_info: List[Dict], 
                                     ai_analysis: Dict, user_prompt: str = None) -> str:
        """Generate intelligent response using local AI logic"""
        
        # Extract key metrics
        health_score = ai_analysis.get('health_score', {}).get('overall', 100)
        critical_issues = ai_analysis.get('critical_issues', [])
        recommendations = ai_analysis.get('recommendations', [])
        anomalies = ai_analysis.get('anomalies', [])
        
        # Start building response
        response_parts = []
        
        # 1. Health Assessment
        response_parts.append(self._health_assessment_template(health_score, ai_analysis))
        
        # 2. Critical Issues Analysis
        if critical_issues:
            response_parts.append(self._issue_diagnosis_template(critical_issues, pod_info))
        
        # 3. Anomaly Analysis
        if anomalies:
            response_parts.append(self._anomaly_analysis_template(anomalies))
        
        # 4. Action Planning
        response_parts.append(self._action_planning_template(critical_issues, recommendations, health_score))
        
        # 5. User-specific response
        if user_prompt:
            response_parts.append(self._user_specific_analysis(user_prompt, ai_analysis))
        
        # 6. Optimization suggestions
        response_parts.append(self._optimization_template(ai_analysis))
        
        return "\n\n".join(response_parts)
    
    def _health_assessment_template(self, health_score: float, ai_analysis: Dict) -> str:
        """Generate health assessment section"""
        grade = ai_analysis.get('health_score', {}).get('grade', 'N/A')
        status = ai_analysis.get('health_score', {}).get('status', 'Unknown')
        
        if health_score >= 90:
            assessment = f"🟢 EXCELLENT CLUSTER HEALTH ({health_score:.1f}% - Grade {grade})"
            details = "Your cluster is running optimally with minimal issues detected."
        elif health_score >= 80:
            assessment = f"🟡 GOOD CLUSTER HEALTH ({health_score:.1f}% - Grade {grade})"
            details = "Your cluster is generally healthy with some minor optimization opportunities."
        elif health_score >= 70:
            assessment = f"🟠 FAIR CLUSTER HEALTH ({health_score:.1f}% - Grade {grade})"
            details = "Your cluster has moderate issues that should be addressed soon."
        elif health_score >= 60:
            assessment = f"🔴 POOR CLUSTER HEALTH ({health_score:.1f}% - Grade {grade})"
            details = "Your cluster has significant issues requiring immediate attention."
        else:
            assessment = f"🚨 CRITICAL CLUSTER HEALTH ({health_score:.1f}% - Grade {grade})"
            details = "Your cluster is in critical condition and requires urgent intervention."
        
        component_health = ai_analysis.get('health_score', {})
        
        return f"""## {assessment}

{details}

**Component Health Breakdown:**
- Pod Health: {component_health.get('pod_health', 0):.1f}%
- Deployment Health: {component_health.get('deployment_health', 0):.1f}%
- Restart Health: {component_health.get('restart_health', 0):.1f}%
- Availability Health: {component_health.get('availability_health', 0):.1f}%"""
    
    def _issue_diagnosis_template(self, critical_issues: List[Dict], pod_info: List[Dict]) -> str:
        """Generate issue diagnosis section"""
        
        diagnosis = ["## 🔍 CRITICAL ISSUE DIAGNOSIS"]
        
        for i, issue in enumerate(critical_issues[:5], 1):
            severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
            emoji = severity_emoji.get(issue.get('severity', 'low'), '🔵')
            
            issue_type = issue.get('type', 'unknown_issue')
            message = issue.get('message', 'No details available')
            recommended_action = issue.get('recommended_action', 'manual_investigation')
            
            diagnosis.append(f"""
**{emoji} Issue #{i}: {issue_type.replace('_', ' ').title()}**
- **Severity**: {issue.get('severity', 'unknown').upper()}
- **Description**: {message}
- **Recommended Action**: {recommended_action}
- **Namespace**: {issue.get('namespace', 'unknown')}
- **Affected Resources**: {issue.get('affected_pods', 'unknown')}""")
        
        return "\n".join(diagnosis)
    
    def _anomaly_analysis_template(self, anomalies: List[Dict]) -> str:
        """Generate anomaly analysis section"""
        
        analysis = ["## 🎯 ML-DETECTED ANOMALIES"]
        
        if not anomalies:
            return "## 🎯 ML-DETECTED ANOMALIES\n\n✅ No significant anomalies detected by machine learning algorithms."
        
        analysis.append(f"\n🤖 Machine learning algorithms detected {len(anomalies)} anomalous pods:")
        
        for i, anomaly in enumerate(anomalies[:3], 1):
            pod_info = anomaly.get('pod', {})
            pod_name = pod_info.get('name', 'unknown')
            namespace = pod_info.get('namespace', 'unknown')
            status = pod_info.get('status', 'unknown')
            
            analysis.append(f"""
**🎯 Anomaly #{i}: {pod_name}**
- **Pod**: {namespace}/{pod_name}
- **Status**: {status}
- **Anomaly Type**: {anomaly.get('type', 'unknown')}
- **Detection**: Machine learning algorithm flagged unusual behavior patterns""")
        
        return "\n".join(analysis)
    
    def _action_planning_template(self, critical_issues: List[Dict], 
                                recommendations: List[Dict], health_score: float) -> str:
        """Generate action planning section"""
        
        planning = ["## 🛠️ AUTONOMOUS ACTION PLAN"]
        
        # Determine urgency based on health score
        if health_score < 60:
            urgency = "IMMEDIATE"
            urgency_emoji = "🚨"
        elif health_score < 80:
            urgency = "HIGH"
            urgency_emoji = "🟠"
        else:
            urgency = "NORMAL"
            urgency_emoji = "🟡"
        
        planning.append(f"\n**{urgency_emoji} Priority Level**: {urgency}")
        
        # Generate actions based on critical issues
        action_count = 0
        if critical_issues:
            planning.append("\n**🎯 Immediate Actions Required:**")
            
            for issue in critical_issues[:5]:
                action_count += 1
                action = issue.get('recommended_action', 'manual_investigation')
                namespace = issue.get('namespace', 'unknown')
                
                planning.append(f"""
ACTION_{action_count}:
  action: {action}
  namespace: {namespace}
  reasoning: {issue.get('message', 'Critical issue detected')}
  priority: {issue.get('severity', 'medium')}""")
        
        # Generate actions based on recommendations
        if recommendations and action_count < 5:
            planning.append("\n**💡 Optimization Actions:**")
            
            for rec in recommendations[:3]:
                if action_count >= 5:
                    break
                
                rec_actions = rec.get('actions', ['investigate'])
                for action in rec_actions[:1]:  # Take first action
                    action_count += 1
                    planning.append(f"""
ACTION_{action_count}:
  action: {action}
  reasoning: {rec.get('message', 'Optimization opportunity')}
  priority: {rec.get('priority', 'medium')}""")
        
        # Default actions if no specific issues
        if action_count == 0:
            planning.append(f"""
ACTION_1:
  action: monitor_cluster
  reasoning: Cluster appears healthy, continue monitoring
  priority: low""")
        
        return "\n".join(planning)
    
    def _user_specific_analysis(self, user_prompt: str, ai_analysis: Dict) -> str:
        """Generate user-specific analysis based on their prompt"""
        
        analysis = ["## 🎯 USER-SPECIFIC ANALYSIS"]
        
        # Parse user intent from prompt
        prompt_lower = user_prompt.lower()
        
        if any(word in prompt_lower for word in ['scale', 'scaling', 'replicas']):
            analysis.append(self._scaling_specific_analysis(ai_analysis))
        elif any(word in prompt_lower for word in ['restart', 'reboot', 'crash']):
            analysis.append(self._restart_specific_analysis(ai_analysis))
        elif any(word in prompt_lower for word in ['performance', 'slow', 'latency']):
            analysis.append(self._performance_specific_analysis(ai_analysis))
        elif any(word in prompt_lower for word in ['error', 'fail', 'problem']):
            analysis.append(self._error_specific_analysis(ai_analysis))
        else:
            analysis.append(self._general_analysis(user_prompt, ai_analysis))
        
        return "\n".join(analysis)
    
    def _scaling_specific_analysis(self, ai_analysis: Dict) -> str:
        """Scaling-focused analysis"""
        efficiency = ai_analysis.get('resource_efficiency', {})
        replica_efficiency = efficiency.get('replica_efficiency', 100)
        
        if replica_efficiency < 90:
            return f"""
**🔍 Scaling Analysis**: Detected replica efficiency at {replica_efficiency:.1f}%
**🎯 Recommendation**: Some deployments are under-scaled
**🛠️ Suggested Action**: bulk_scale_deployments with 20% increase"""
        else:
            return f"""
**🔍 Scaling Analysis**: Replica efficiency is good at {replica_efficiency:.1f}%
**🎯 Recommendation**: Current scaling appears optimal
**🛠️ Suggested Action**: apply_hpa for automatic scaling"""
    
    def _restart_specific_analysis(self, ai_analysis: Dict) -> str:
        """Restart-focused analysis"""
        issues = ai_analysis.get('critical_issues', [])
        restart_issues = [i for i in issues if 'restart' in i.get('type', '').lower()]
        
        if restart_issues:
            return f"""
**🔍 Restart Analysis**: Found {len(restart_issues)} restart-related issues
**🎯 Recommendation**: Multiple pods showing restart problems
**🛠️ Suggested Action**: bulk_restart_pods for problematic pods"""
        else:
            return f"""
**🔍 Restart Analysis**: No significant restart issues detected
**🎯 Recommendation**: Cluster restart behavior is normal
**🛠️ Suggested Action**: Continue monitoring"""
    
    def _performance_specific_analysis(self, ai_analysis: Dict) -> str:
        """Performance-focused analysis"""
        health = ai_analysis.get('health_score', {})
        overall_health = health.get('overall', 100)
        
        if overall_health < 80:
            return f"""
**🔍 Performance Analysis**: Overall health at {overall_health:.1f}% indicates performance issues
**🎯 Recommendation**: Performance degradation detected
**🛠️ Suggested Action**: restart_deployment for underperforming services"""
        else:
            return f"""
**🔍 Performance Analysis**: Performance metrics look healthy ({overall_health:.1f}%)
**🎯 Recommendation**: No immediate performance concerns
**🛠️ Suggested Action**: update_pod_resources for optimization"""
    
    def _error_specific_analysis(self, ai_analysis: Dict) -> str:
        """Error-focused analysis"""
        critical_issues = ai_analysis.get('critical_issues', [])
        critical_count = len([i for i in critical_issues if i.get('severity') == 'critical'])
        
        if critical_count > 0:
            return f"""
**🔍 Error Analysis**: {critical_count} critical errors detected
**🎯 Recommendation**: Immediate intervention required
**🛠️ Suggested Action**: delete_pod for failing pods, then restart_deployment"""
        else:
            return f"""
**🔍 Error Analysis**: No critical errors detected
**🎯 Recommendation**: System errors are within normal range
**🛠️ Suggested Action**: Continue monitoring"""
    
    def _general_analysis(self, user_prompt: str, ai_analysis: Dict) -> str:
        """General analysis for unspecific prompts"""
        health = ai_analysis.get('health_score', {}).get('overall', 100)
        issues = len(ai_analysis.get('critical_issues', []))
        
        return f"""
**🔍 General Analysis**: Based on your request: "{user_prompt[:100]}..."
**🎯 Current State**: Health {health:.1f}%, {issues} critical issues
**🛠️ Suggested Action**: {'immediate_intervention' if health < 70 else 'optimization_actions'}"""
    
    def _optimization_template(self, ai_analysis: Dict) -> str:
        """Generate optimization suggestions"""
        
        optimization = ["## 🚀 OPTIMIZATION OPPORTUNITIES"]
        
        recommendations = ai_analysis.get('recommendations', [])
        resource_efficiency = ai_analysis.get('resource_efficiency', {})
        
        if recommendations:
            optimization.append("\n**💡 AI-Recommended Optimizations:**")
            for i, rec in enumerate(recommendations[:3], 1):
                priority = rec.get('priority', 'medium').upper()
                message = rec.get('message', 'No details')
                actions = rec.get('actions', ['investigate'])
                
                optimization.append(f"""
{i}. **{priority} Priority**: {rec.get('type', 'Unknown').replace('_', ' ').title()}
   - Issue: {message}
   - Actions: {', '.join(actions)}""")
        
        # Resource efficiency suggestions
        replica_efficiency = resource_efficiency.get('replica_efficiency', 100)
        if replica_efficiency < 95:
            optimization.append(f"""
**📊 Resource Efficiency**: {replica_efficiency:.1f}%
- Consider applying HPA (Horizontal Pod Autoscaler)
- Review resource requests and limits
- Optimize deployment scaling policies""")
        
        if not recommendations and replica_efficiency >= 95:
            optimization.append("\n✅ Your cluster is well-optimized! Consider proactive monitoring.")
        
        return "\n".join(optimization)
    
    def extract_actions(self, ai_response: str) -> List[Dict[str, Any]]:
        """Extract actionable items from AI response"""
        actions = []
        
        # Look for ACTION_ patterns in the response
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
                'confidence': 0.8,  # High confidence for local AI decisions
                'source': 'local_ai',
                'parameters': {}  # Add empty parameters dict
            })
        
        return actions
    
    def get_cluster_insights(self, cluster_info: Dict, pod_info: List[Dict]) -> Dict[str, Any]:
        """Get quick cluster insights without full analysis"""
        
        total_pods = len(pod_info) if pod_info else 0
        problematic_pods = len([p for p in pod_info if p.get('status', '').lower() != 'running']) if pod_info else 0
        
        # Calculate basic health
        health_ratio = ((total_pods - problematic_pods) / total_pods * 100) if total_pods > 0 else 100
        
        insights = {
            'quick_health': health_ratio,
            'total_pods': total_pods,
            'problematic_pods': problematic_pods,
            'recommendations': [],
            'urgency': 'normal'
        }
        
        # Add quick recommendations
        if problematic_pods > 0:
            insights['recommendations'].append({
                'action': 'restart_pod' if problematic_pods <= 3 else 'bulk_restart_pods',
                'reason': f'{problematic_pods} pods are not running properly',
                'confidence': 0.9
            })
        
        if health_ratio < 70:
            insights['urgency'] = 'high'
            insights['recommendations'].append({
                'action': 'immediate_investigation',
                'reason': 'Cluster health is below acceptable threshold',
                'confidence': 0.95
            })
        
        return insights


def create_local_ai_engine() -> LocalAIEngine:
    """Factory function to create local AI engine"""
    return LocalAIEngine()


def run_local_ai_analysis(cluster_info: Dict, pod_info: List[Dict], user_prompt: str = None) -> str:
    """Run local AI analysis without external APIs"""
    engine = create_local_ai_engine()
    return engine.analyze_and_recommend(cluster_info, pod_info, user_prompt)


def extract_local_actions(ai_response: str) -> List[Dict[str, Any]]:
    """Extract actions from local AI response"""
    engine = create_local_ai_engine()
    return engine.extract_actions(ai_response)
