# actions/ai_action_handler.py
"""
AI-Enhanced Action Handler for Kubernetes
Integrates advanced AI libraries for intelligent cluster management
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

try:
    from prometheus_client.parser import text_string_to_metric_families
    from prometheus_api_client import PrometheusConnect
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from prophet import Prophet
    import pandas as pd
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .action_handler import (
    get_all_pods, get_all_deployments
)
from .restarter import restart_pod, delete_pod
from .scaler import scale_deployment, bulk_scale_deployments


class AIActionHandler:
    """AI-enhanced action handler with predictive capabilities"""
    
    def __init__(self, prometheus_url: str = None):
        self.prometheus_url = prometheus_url or "http://localhost:9090"
        self.prometheus_client = None
        self.anomaly_detector = IsolationForest(contamination=0.1) if SKLEARN_AVAILABLE else None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        
        # Initialize Prometheus client if available
        if PROMETHEUS_AVAILABLE and prometheus_url:
            try:
                self.prometheus_client = PrometheusConnect(url=prometheus_url, disable_ssl=True)
            except:
                self.prometheus_client = None
    
    def intelligent_scale_decision(self, deployment_name: str, namespace: str = "default") -> Dict[str, Any]:
        """Make intelligent scaling decisions based on metrics and predictions"""
        result = {
            'action': 'intelligent_scaling',
            'deployment': f"{namespace}/{deployment_name}",
            'recommendation': {},
            'confidence': 0.0,
            'reasoning': []
        }
        
        try:
            # Get current deployment info
            deployments = get_all_deployments()
            target_dep = None
            
            for dep in deployments:
                if dep.get('name') == deployment_name and dep.get('namespace') == namespace:
                    target_dep = dep
                    break
            
            if not target_dep:
                result['error'] = f"Deployment {namespace}/{deployment_name} not found"
                return result
            
            current_replicas = target_dep.get('replicas', 1)
            ready_replicas = target_dep.get('ready_replicas', 0)
            
            # Basic health check
            if ready_replicas < current_replicas * 0.7:  # Less than 70% ready
                result['recommendation'] = {
                    'action': 'investigate_before_scaling',
                    'suggested_replicas': current_replicas,
                    'reason': 'Poor replica health - investigate before scaling'
                }
                result['confidence'] = 0.9
                result['reasoning'].append("Low ready replica ratio detected")
                return result
            
            # Prometheus-based analysis
            if self.prometheus_client:
                metrics_analysis = self._analyze_prometheus_metrics(deployment_name, namespace)
                if metrics_analysis:
                    result['recommendation'].update(metrics_analysis)
                    result['confidence'] = max(result['confidence'], 0.8)
                    result['reasoning'].append("Prometheus metrics analyzed")
            
            # Time-series prediction
            if PROPHET_AVAILABLE:
                prediction = self._predict_resource_needs(deployment_name, namespace)
                if prediction:
                    result['recommendation'].update(prediction)
                    result['confidence'] = max(result['confidence'], 0.7)
                    result['reasoning'].append("Time-series prediction applied")
            
            # Default recommendation if no other analysis available
            if not result['recommendation']:
                # Simple load-based scaling
                if ready_replicas == current_replicas:  # All replicas healthy
                    suggested_replicas = min(current_replicas + 1, 10)  # Scale up conservatively
                    result['recommendation'] = {
                        'action': 'scale_up',
                        'suggested_replicas': suggested_replicas,
                        'reason': 'Conservative scale-up for healthy deployment'
                    }
                else:
                    result['recommendation'] = {
                        'action': 'maintain',
                        'suggested_replicas': current_replicas,
                        'reason': 'Maintain current scale due to unhealthy replicas'
                    }
                
                result['confidence'] = 0.6
                result['reasoning'].append("Basic heuristic applied")
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _analyze_prometheus_metrics(self, deployment_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Analyze Prometheus metrics for scaling decisions"""
        if not self.prometheus_client:
            return None
        
        try:
            # Query CPU usage
            cpu_query = f'avg(rate(container_cpu_usage_seconds_total{{namespace="{namespace}", pod=~"{deployment_name}.*"}}[5m]))'
            cpu_result = self.prometheus_client.custom_query(query=cpu_query)
            
            # Query memory usage
            memory_query = f'avg(container_memory_working_set_bytes{{namespace="{namespace}", pod=~"{deployment_name}.*"}})'
            memory_result = self.prometheus_client.custom_query(query=memory_query)
            
            cpu_usage = 0.0
            memory_usage = 0.0
            
            if cpu_result and len(cpu_result) > 0:
                cpu_usage = float(cpu_result[0]['value'][1])
            
            if memory_result and len(memory_result) > 0:
                memory_usage = float(memory_result[0]['value'][1]) / (1024**3)  # Convert to GB
            
            # Make scaling recommendation based on metrics
            if cpu_usage > 0.8:  # High CPU usage
                return {
                    'action': 'scale_up',
                    'reason': f'High CPU usage: {cpu_usage:.2f}',
                    'metrics': {'cpu': cpu_usage, 'memory_gb': memory_usage}
                }
            elif cpu_usage < 0.2 and memory_usage < 1.0:  # Low resource usage
                return {
                    'action': 'scale_down',
                    'reason': f'Low resource usage: CPU {cpu_usage:.2f}, Memory {memory_usage:.1f}GB',
                    'metrics': {'cpu': cpu_usage, 'memory_gb': memory_usage}
                }
            else:
                return {
                    'action': 'maintain',
                    'reason': 'Resource usage within normal range',
                    'metrics': {'cpu': cpu_usage, 'memory_gb': memory_usage}
                }
        
        except Exception as e:
            return {'error': f'Prometheus analysis failed: {e}'}
    
    def _predict_resource_needs(self, deployment_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Use Prophet for time-series forecasting of resource needs"""
        if not PROPHET_AVAILABLE:
            return None
        
        try:
            # Generate synthetic historical data for demo (in real implementation, use actual metrics)
            dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='H')
            
            # Simulate load patterns (normally would come from Prometheus)
            np.random.seed(42)
            base_load = 0.5
            daily_pattern = 0.3 * np.sin(2 * np.pi * np.arange(len(dates)) / 24)
            noise = 0.1 * np.random.randn(len(dates))
            load_values = base_load + daily_pattern + noise
            
            # Create Prophet dataframe
            df = pd.DataFrame({
                'ds': dates,
                'y': load_values
            })
            
            # Fit Prophet model
            model = Prophet(daily_seasonality=True, weekly_seasonality=True)
            model.fit(df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=24, freq='H')  # Next 24 hours
            forecast = model.predict(future)
            
            # Get next hour prediction
            next_hour_load = forecast.iloc[-1]['yhat']
            
            # Make scaling recommendation based on prediction
            if next_hour_load > 0.8:
                return {
                    'action': 'preemptive_scale_up',
                    'reason': f'Predicted high load: {next_hour_load:.2f}',
                    'predicted_load': next_hour_load,
                    'timeline': 'next_hour'
                }
            elif next_hour_load < 0.3:
                return {
                    'action': 'preemptive_scale_down',
                    'reason': f'Predicted low load: {next_hour_load:.2f}',
                    'predicted_load': next_hour_load,
                    'timeline': 'next_hour'
                }
            else:
                return {
                    'action': 'maintain',
                    'reason': f'Predicted normal load: {next_hour_load:.2f}',
                    'predicted_load': next_hour_load,
                    'timeline': 'next_hour'
                }
        
        except Exception as e:
            return {'error': f'Time-series prediction failed: {e}'}
    
    def anomaly_based_action(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actions based on detected anomalies"""
        actions = []
        
        for anomaly in anomalies:
            if anomaly.get('type') == 'ml_anomaly':
                pod_info = anomaly.get('pod', {})
                pod_name = pod_info.get('name')
                namespace = pod_info.get('namespace')
                
                actions.append({
                    'action': 'restart_pod',
                    'parameters': {
                        'pod_name': pod_name,
                        'namespace': namespace
                    },
                    'reason': f'ML anomaly detected in pod {pod_name}',
                    'confidence': 0.7
                })
        
        return actions
    
    def resource_optimization_actions(self, efficiency_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actions based on resource efficiency analysis"""
        actions = []
        
        recommendations = efficiency_analysis.get('recommendations', [])
        
        for rec in recommendations:
            if rec.get('type') == 'restart_optimization':
                actions.append({
                    'action': 'bulk_restart_pods',
                    'parameters': {
                        'criteria': 'high_restarts',
                        'threshold': 5
                    },
                    'reason': 'Optimize pods with high restart counts',
                    'confidence': 0.8
                })
            
            elif rec.get('type') == 'efficiency_optimization':
                actions.append({
                    'action': 'bulk_scale_deployments',
                    'parameters': {
                        'scale_factor': 1.2,
                        'max_replicas': 10
                    },
                    'reason': 'Improve replica efficiency',
                    'confidence': 0.7
                })
        
        return actions


def create_ai_action_handler(prometheus_url: str = None) -> AIActionHandler:
    """Factory function to create AI action handler"""
    return AIActionHandler(prometheus_url)


def run_intelligent_scaling(deployment_name: str, namespace: str = "default", prometheus_url: str = None) -> Dict[str, Any]:
    """Run intelligent scaling analysis for a deployment"""
    handler = create_ai_action_handler(prometheus_url)
    return handler.intelligent_scale_decision(deployment_name, namespace)
