# ai_engine/k8s_ai_analyzer.py
"""
Advanced Kubernetes AI Analyzer
Uses specialized ML libraries for cluster intelligence
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

try:
    from prometheus_client.parser import text_string_to_metric_families
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from k8s_connector.kube_api import get_cluster_summary
from actions.action_handler import get_all_pods, get_all_deployments, get_problematic_pods


class KubernetesAIAnalyzer:
    """Advanced AI analyzer for Kubernetes clusters using ML libraries"""
    
    def __init__(self):
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42) if SKLEARN_AVAILABLE else None
        self.cluster_graph = nx.DiGraph() if NETWORKX_AVAILABLE else None
        
    def analyze_cluster_health(self) -> Dict[str, Any]:
        """Comprehensive cluster health analysis using AI/ML"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': 'unknown',
            'critical_issues': [],
            'recommendations': [],
            'anomalies': [],
            'resource_efficiency': {},
            'predictive_insights': {}
        }
        
        try:
            # Get cluster data
            pods = get_all_pods()
            deployments = get_all_deployments()
            problematic_pods = get_problematic_pods()
            
            # 1. Anomaly Detection
            if SKLEARN_AVAILABLE and pods:
                anomalies = self._detect_anomalies(pods)
                analysis['anomalies'] = anomalies
            
            # 2. Resource Efficiency Analysis
            analysis['resource_efficiency'] = self._analyze_resource_efficiency(pods, deployments)
            
            # 3. Cluster Topology Analysis
            if NETWORKX_AVAILABLE:
                analysis['topology_insights'] = self._analyze_cluster_topology(pods, deployments)
            
            # 4. Predictive Health Scoring
            analysis['health_score'] = self._calculate_health_score(pods, deployments, problematic_pods)
            
            # 5. Critical Issue Detection
            analysis['critical_issues'] = self._detect_critical_issues(pods, deployments, problematic_pods)
            
            # 6. AI Recommendations
            analysis['recommendations'] = self._generate_ai_recommendations(analysis)
            
            # 7. Overall health assessment
            analysis['overall_health'] = self._assess_overall_health(analysis)
            
        except Exception as e:
            analysis['error'] = str(e)
            analysis['overall_health'] = 'error'
        
        return analysis
    
    def _detect_anomalies(self, pods: List[Dict]) -> List[Dict[str, Any]]:
        """Use ML to detect anomalous pod behavior"""
        if not pods or not SKLEARN_AVAILABLE:
            return []
        
        try:
            # Create feature matrix
            features = []
            pod_info = []
            
            for pod in pods:
                if isinstance(pod, dict):
                    features.append([
                        pod.get('restarts', 0),
                        1 if pod.get('status', '').lower() == 'running' else 0,
                        len(pod.get('name', '')),  # Name length as a feature
                        hash(pod.get('namespace', '')) % 1000,  # Namespace hash
                    ])
                    pod_info.append({
                        'name': pod.get('name', 'unknown'),
                        'namespace': pod.get('namespace', 'unknown'),
                        'status': pod.get('status', 'unknown')
                    })
            
            if len(features) < 2:
                return []
            
            # Detect anomalies
            features_scaled = self.scaler.fit_transform(features)
            anomaly_scores = self.anomaly_detector.fit_predict(features_scaled)
            
            # Return anomalous pods
            anomalies = []
            for i, score in enumerate(anomaly_scores):
                if score == -1:  # Anomaly detected
                    anomalies.append({
                        'pod': pod_info[i],
                        'anomaly_score': score,
                        'features': features[i],
                        'type': 'ml_anomaly'
                    })
            
            return anomalies
            
        except Exception as e:
            return [{'error': f'Anomaly detection failed: {e}'}]
    
    def _analyze_resource_efficiency(self, pods: List[Dict], deployments: List[Dict]) -> Dict[str, Any]:
        """Analyze resource utilization efficiency"""
        efficiency = {
            'cpu_efficiency': 0.0,
            'memory_efficiency': 0.0,
            'replica_efficiency': 0.0,
            'namespace_distribution': {},
            'recommendations': []
        }
        
        try:
            if deployments:
                # Calculate replica efficiency
                total_desired = sum(d.get('desired_replicas', d.get('replicas', 0)) for d in deployments)
                total_ready = sum(d.get('ready_replicas', d.get('replicas', 0)) for d in deployments)
                
                if total_desired > 0:
                    efficiency['replica_efficiency'] = (total_ready / total_desired) * 100
                
                # Namespace distribution analysis
                ns_counts = {}
                for dep in deployments:
                    ns = dep.get('namespace', 'unknown')
                    ns_counts[ns] = ns_counts.get(ns, 0) + 1
                
                efficiency['namespace_distribution'] = ns_counts
                
                # Generate efficiency recommendations
                if efficiency['replica_efficiency'] < 80:
                    efficiency['recommendations'].append({
                        'type': 'replica_efficiency',
                        'message': 'Low replica efficiency detected - some deployments may need scaling',
                        'action': 'investigate_scaling'
                    })
            
            if pods:
                # Analyze pod distribution
                running_pods = len([p for p in pods if p.get('status', '').lower() == 'running'])
                total_pods = len(pods)
                
                if total_pods > 0:
                    efficiency['pod_health_ratio'] = (running_pods / total_pods) * 100
                
                # High restart analysis
                high_restart_pods = [p for p in pods if p.get('restarts', 0) > 3]
                if high_restart_pods:
                    efficiency['recommendations'].append({
                        'type': 'restart_optimization',
                        'message': f'{len(high_restart_pods)} pods have high restart counts',
                        'action': 'investigate_restarts',
                        'affected_pods': len(high_restart_pods)
                    })
        
        except Exception as e:
            efficiency['error'] = str(e)
        
        return efficiency
    
    def _analyze_cluster_topology(self, pods: List[Dict], deployments: List[Dict]) -> Dict[str, Any]:
        """Analyze cluster topology and relationships"""
        if not NETWORKX_AVAILABLE:
            return {'error': 'NetworkX not available'}
        
        try:
            # Build cluster graph
            G = nx.DiGraph()
            
            # Add nodes for namespaces, deployments, and pods
            namespaces = set()
            
            for dep in deployments:
                ns = dep.get('namespace', 'unknown')
                dep_name = dep.get('name', 'unknown')
                namespaces.add(ns)
                
                G.add_node(f"ns:{ns}", type='namespace')
                G.add_node(f"dep:{ns}/{dep_name}", type='deployment')
                G.add_edge(f"ns:{ns}", f"dep:{ns}/{dep_name}")
            
            for pod in pods:
                ns = pod.get('namespace', 'unknown')
                pod_name = pod.get('name', 'unknown')
                namespaces.add(ns)
                
                G.add_node(f"pod:{ns}/{pod_name}", type='pod')
                G.add_edge(f"ns:{ns}", f"pod:{ns}/{pod_name}")
            
            # Calculate topology metrics
            analysis = {
                'total_nodes': G.number_of_nodes(),
                'total_edges': G.number_of_edges(),
                'namespaces': len(namespaces),
                'density': nx.density(G),
                'connected_components': nx.number_weakly_connected_components(G)
            }
            
            # Identify central namespaces (hubs)
            namespace_centrality = {}
            for ns in namespaces:
                ns_node = f"ns:{ns}"
                if G.has_node(ns_node):
                    namespace_centrality[ns] = G.out_degree(ns_node)
            
            analysis['namespace_centrality'] = namespace_centrality
            
            # Find potential bottlenecks
            if namespace_centrality:
                max_centrality = max(namespace_centrality.values())
                bottleneck_namespaces = [
                    ns for ns, centrality in namespace_centrality.items() 
                    if centrality > max_centrality * 0.7
                ]
                analysis['potential_bottlenecks'] = bottleneck_namespaces
            
            return analysis
            
        except Exception as e:
            return {'error': f'Topology analysis failed: {e}'}
    
    def _calculate_health_score(self, pods: List[Dict], deployments: List[Dict], problematic_pods: List[Dict]) -> Dict[str, Any]:
        """Calculate overall cluster health score using multiple metrics"""
        try:
            # Initialize scores
            scores = {
                'pod_health': 100.0,
                'deployment_health': 100.0,
                'restart_health': 100.0,
                'availability_health': 100.0,
                'overall': 100.0
            }
            
            # Pod health score
            if pods:
                running_pods = len([p for p in pods if p.get('status', '').lower() == 'running'])
                scores['pod_health'] = (running_pods / len(pods)) * 100
            
            # Deployment health score
            if deployments:
                healthy_deployments = len([
                    d for d in deployments 
                    if d.get('ready_replicas', 0) == d.get('desired_replicas', d.get('replicas', 0))
                ])
                scores['deployment_health'] = (healthy_deployments / len(deployments)) * 100
            
            # Restart health score (penalize high restarts)
            if pods:
                total_restarts = sum(p.get('restarts', 0) for p in pods)
                restart_penalty = min(total_restarts * 2, 50)  # Max 50% penalty
                scores['restart_health'] = max(100 - restart_penalty, 0)
            
            # Availability health score
            if deployments:
                zero_replica_deployments = len([d for d in deployments if d.get('replicas', 0) == 0])
                if zero_replica_deployments > 0:
                    availability_penalty = (zero_replica_deployments / len(deployments)) * 100
                    scores['availability_health'] = max(100 - availability_penalty, 0)
            
            # Calculate overall score (weighted average)
            weights = {
                'pod_health': 0.3,
                'deployment_health': 0.3,
                'restart_health': 0.2,
                'availability_health': 0.2
            }
            
            overall = sum(scores[metric] * weight for metric, weight in weights.items())
            scores['overall'] = round(overall, 1)
            
            # Add health grade
            if scores['overall'] >= 90:
                scores['grade'] = 'A'
                scores['status'] = 'Excellent'
            elif scores['overall'] >= 80:
                scores['grade'] = 'B'
                scores['status'] = 'Good'
            elif scores['overall'] >= 70:
                scores['grade'] = 'C'
                scores['status'] = 'Fair'
            elif scores['overall'] >= 60:
                scores['grade'] = 'D'
                scores['status'] = 'Poor'
            else:
                scores['grade'] = 'F'
                scores['status'] = 'Critical'
            
            return scores
            
        except Exception as e:
            return {'error': f'Health scoring failed: {e}', 'overall': 0}
    
    def _detect_critical_issues(self, pods: List[Dict], deployments: List[Dict], problematic_pods: List[Dict]) -> List[Dict[str, Any]]:
        """Advanced critical issue detection using AI patterns"""
        issues = []
        
        try:
            # Issue 1: Cascade failure pattern
            if problematic_pods:
                namespace_failures = {}
                for pod in problematic_pods:
                    ns = pod.get('namespace', 'unknown')
                    namespace_failures[ns] = namespace_failures.get(ns, 0) + 1
                
                for ns, count in namespace_failures.items():
                    if count >= 3:  # 3+ failures in same namespace
                        issues.append({
                            'type': 'cascade_failure',
                            'severity': 'critical',
                            'namespace': ns,
                            'affected_pods': count,
                            'message': f'Cascade failure detected in {ns}: {count} failed pods',
                            'recommended_action': 'bulk_restart_pods'
                        })
            
            # Issue 2: Resource starvation pattern
            if deployments:
                zero_replica_deployments = [d for d in deployments if d.get('replicas', 0) == 0]
                if zero_replica_deployments:
                    for dep in zero_replica_deployments:
                        issues.append({
                            'type': 'service_unavailable',
                            'severity': 'critical',
                            'namespace': dep.get('namespace'),
                            'deployment': dep.get('name'),
                            'message': f'Service down: {dep.get("name")} has 0 replicas',
                            'recommended_action': 'scale_deployment'
                        })
            
            # Issue 3: Restart spiral pattern
            if pods:
                restart_spirals = [
                    p for p in pods 
                    if p.get('restarts', 0) > 10 and p.get('status', '').lower() != 'running'
                ]
                
                for pod in restart_spirals:
                    issues.append({
                        'type': 'restart_spiral',
                        'severity': 'high',
                        'namespace': pod.get('namespace'),
                        'pod': pod.get('name'),
                        'restarts': pod.get('restarts'),
                        'message': f'Restart spiral: {pod.get("name")} has {pod.get("restarts")} restarts',
                        'recommended_action': 'delete_pod'
                    })
            
            # Issue 4: Scaling inefficiency
            if deployments:
                inefficient_deployments = []
                for dep in deployments:
                    desired = dep.get('desired_replicas', dep.get('replicas', 0))
                    ready = dep.get('ready_replicas', dep.get('replicas', 0))
                    
                    if desired > 0 and ready < desired * 0.5:  # Less than 50% ready
                        inefficient_deployments.append(dep)
                
                if inefficient_deployments:
                    issues.append({
                        'type': 'scaling_inefficiency',
                        'severity': 'medium',
                        'affected_deployments': len(inefficient_deployments),
                        'message': f'Scaling inefficiency: {len(inefficient_deployments)} deployments under-scaled',
                        'recommended_action': 'bulk_scale_deployments'
                    })
            
            # Sort by severity
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            issues.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
            
        except Exception as e:
            issues.append({'type': 'analysis_error', 'severity': 'medium', 'message': str(e)})
        
        return issues
    
    def _generate_ai_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent recommendations based on analysis"""
        recommendations = []
        
        try:
            health_score = analysis.get('health_score', {}).get('overall', 100)
            critical_issues = analysis.get('critical_issues', [])
            resource_efficiency = analysis.get('resource_efficiency', {})
            
            # Health-based recommendations
            if health_score < 70:
                recommendations.append({
                    'type': 'health_improvement',
                    'priority': 'high',
                    'message': f'Cluster health is {health_score:.1f}% - immediate attention required',
                    'actions': ['run_autonomous_diagnosis', 'investigate_critical_issues']
                })
            
            # Issue-based recommendations
            if critical_issues:
                critical_count = len([i for i in critical_issues if i.get('severity') == 'critical'])
                if critical_count > 0:
                    recommendations.append({
                        'type': 'critical_issues',
                        'priority': 'critical',
                        'message': f'{critical_count} critical issues detected requiring immediate action',
                        'actions': [issue.get('recommended_action') for issue in critical_issues[:3]]
                    })
            
            # Efficiency recommendations
            replica_efficiency = resource_efficiency.get('replica_efficiency', 100)
            if replica_efficiency < 90:
                recommendations.append({
                    'type': 'efficiency_optimization',
                    'priority': 'medium',
                    'message': f'Replica efficiency is {replica_efficiency:.1f}% - consider optimization',
                    'actions': ['bulk_scale_deployments', 'apply_hpa']
                })
            
            # Proactive recommendations
            if health_score > 90 and not critical_issues:
                recommendations.append({
                    'type': 'proactive_optimization',
                    'priority': 'low',
                    'message': 'Cluster is healthy - consider proactive optimizations',
                    'actions': ['apply_hpa', 'update_pod_resources']
                })
        
        except Exception as e:
            recommendations.append({
                'type': 'error',
                'priority': 'medium',
                'message': f'Recommendation generation failed: {e}'
            })
        
        return recommendations
    
    def _assess_overall_health(self, analysis: Dict[str, Any]) -> str:
        """Assess overall cluster health"""
        try:
            health_score = analysis.get('health_score', {}).get('overall', 0)
            critical_issues = len([i for i in analysis.get('critical_issues', []) if i.get('severity') == 'critical'])
            
            if critical_issues > 0:
                return 'critical'
            elif health_score >= 90:
                return 'excellent'
            elif health_score >= 80:
                return 'good'
            elif health_score >= 70:
                return 'fair'
            elif health_score >= 60:
                return 'poor'
            else:
                return 'critical'
                
        except:
            return 'unknown'
    
    def get_predictive_insights(self, historical_data: List[Dict] = None) -> Dict[str, Any]:
        """Generate predictive insights for cluster management"""
        insights = {
            'predicted_issues': [],
            'scaling_recommendations': [],
            'maintenance_windows': [],
            'resource_trends': {}
        }
        
        try:
            # Current analysis for baseline
            current_analysis = self.analyze_cluster_health()
            
            # Predict potential issues based on current state
            current_issues = current_analysis.get('critical_issues', [])
            for issue in current_issues:
                if issue.get('type') == 'restart_spiral':
                    insights['predicted_issues'].append({
                        'type': 'imminent_failure',
                        'confidence': 0.85,
                        'timeline': '15-30 minutes',
                        'resource': f"{issue.get('namespace')}/{issue.get('pod')}",
                        'action': 'delete_pod'
                    })
            
            # Resource trend predictions
            health_score = current_analysis.get('health_score', {}).get('overall', 100)
            if health_score < 80:
                insights['scaling_recommendations'].append({
                    'type': 'proactive_scaling',
                    'confidence': 0.7,
                    'recommendation': 'Scale up critical services before peak hours',
                    'action': 'bulk_scale_deployments'
                })
            
        except Exception as e:
            insights['error'] = str(e)
        
        return insights


def create_ai_analyzer() -> KubernetesAIAnalyzer:
    """Factory function to create AI analyzer"""
    return KubernetesAIAnalyzer()


def run_advanced_cluster_analysis() -> Dict[str, Any]:
    """Run comprehensive AI-powered cluster analysis"""
    analyzer = create_ai_analyzer()
    return analyzer.analyze_cluster_health()
