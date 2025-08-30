# ai_engine/planner.py
"""
Local AI-powered cluster planner
Uses autonomous AI engine instead of external APIs
"""

import yaml
import time
from ai_engine.prompt_templates import BASE_DIAGNOSIS_TEMPLATE
from k8s_connector.kube_api import get_cluster_summary
from .local_ai_engine import LocalAIEngine, run_local_ai_analysis
#     else:
#         prompt = BASE_DIAGNOSIS_TEMPLATE.format(cluster_state=cluster_info)

#     payload = {
#         "contents": [
#             {"parts": [{"text": prompt}]}
#         ]
#     }

#     response = requests.post(
#         f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
#         json=payload
#     )

#     result = response.json()
#     return result["candidates"][0]["content"]["parts"][0]["text"]

# ai_engine/planner.py

import httpx
import yaml
import time
from ai_engine.prompt_templates import BASE_DIAGNOSIS_TEMPLATE
from k8s_connector.kube_api import get_cluster_summary

from .local_ai_engine import LocalAIEngine, run_local_ai_analysis

def diagnose_cluster(prompt_override: str = None):
    cluster_info = get_cluster_summary()
    
    # Get problematic pods for detailed analysis
    try:
        from actions.action_handler import get_problematic_pods
        pod_info = get_problematic_pods()
    except:
        pod_info = []
    
    try:
        # Use local AI engine instead of external API
        local_ai = LocalAIEngine()
        ai_response = local_ai.analyze_and_recommend(
            cluster_info=cluster_info,
            pod_info=pod_info,
            user_prompt=prompt_override
        )
        
        return {
            "prompt": prompt_override or "Local AI cluster diagnosis",
            "cluster_snapshot": cluster_info,
            "ai_response": ai_response,
            "source": "local_ai_engine"
        }
        
    except Exception as e:
        # Fallback to basic cluster summary
        fallback_response = f"""## 🤖 LOCAL AI CLUSTER DIAGNOSIS

**📊 Cluster Summary**: 
{cluster_info}

**🔍 Analysis**: Local AI analysis temporarily unavailable. 
**📋 Recommendation**: Use autonomous agent for detailed analysis.

**Error**: {e}"""
        
        return {
            "prompt": prompt_override or "Fallback diagnosis",
            "cluster_snapshot": cluster_info,
            "ai_response": fallback_response,
            "source": "fallback",
            "error": str(e)
        }

