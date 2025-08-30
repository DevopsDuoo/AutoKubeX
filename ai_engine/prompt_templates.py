BASE_DIAGNOSIS_TEMPLATE = """
Analyze the following Kubernetes cluster status and list any critical issues or recommendations:

{cluster_state}
"""

AUTONOMOUS_DIAGNOSIS_TEMPLATE = """
You are an autonomous Kubernetes cluster management AI. Your job is to:
1. Analyze the cluster state for issues
2. Provide specific actionable fixes
3. Format fixes as executable actions

CLUSTER INFORMATION:
{cluster_summary}

POD DETAILS:
{pod_details}

AVAILABLE AUTONOMOUS ACTIONS:
{available_actions}

CURRENT TIME: {current_time}

INSTRUCTIONS:
- Analyze the cluster for critical issues (failing pods, resource problems, scaling issues)
- For each issue found, provide specific fixes using the available actions
- Format each action exactly like this:

ACTION: action_name
PARAMS: {{"param1": "value1", "param2": "value2"}}
REASON: Brief explanation of why this action is needed

PRIORITY ISSUES TO LOOK FOR:
1. Pods with high restart counts (>5) - suggest restart_pod or delete_pod
2. Failed/CrashLoopBackOff pods - suggest delete_pod to force recreation
3. Deployments with 0 replicas - suggest scale_deployment
4. Resource-starved namespaces - suggest scaling actions
5. Stuck pending pods - suggest resource updates or scaling

EXAMPLE OUTPUT FORMAT:
DIAGNOSIS: Found 3 critical issues requiring immediate attention

ISSUE 1: Pod nginx-deployment-abc123 has 15 restarts in default namespace
ACTION: restart_pod
PARAMS: {{"namespace": "default", "pod_name": "nginx-deployment-abc123"}}
REASON: High restart count indicates instability, restart to clear state

ISSUE 2: Deployment web-app has 0 replicas in production namespace  
ACTION: scale_deployment
PARAMS: {{"namespace": "production", "deployment": "web-app", "replicas": 2}}
REASON: Zero replicas means service is down, scale to restore availability

Be specific with namespaces and resource names. Only suggest actions for real issues you detect.
"""

EXECUTION_PLAN_TEMPLATE = """
Based on the cluster analysis, create an execution plan for the following issues:

DETECTED ISSUES:
{issues}

AVAILABLE ACTIONS:
{available_actions}

Create a step-by-step execution plan with specific Kubernetes actions to resolve each issue.
Format each action as:

ACTION: action_name
PARAMS: {{"param1": "value1", "param2": "value2"}}
REASON: Why this action solves the issue

Prioritize actions by:
1. Safety (non-destructive first)  
2. Impact (fix critical issues first)
3. Dependencies (prerequisites before dependent actions)
"""