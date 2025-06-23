# # ai_engine/planner.py
# import requests
# import yaml
# from ai_engine.prompt_templates import BASE_DIAGNOSIS_TEMPLATE
# from k8s_connector.kube_api import get_cluster_summary

# with open("config/default.yaml") as f:
#     config = yaml.safe_load(f)
#     GEMINI_API_KEY = config["gemini_api_key"]

# def diagnose_cluster(prompt_override: str = None):
#     cluster_info = get_cluster_summary()

#     if prompt_override:
#         prompt = f"{prompt_override}\n\nHere's the current cluster status:\n{cluster_info}"
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

# Load Gemini API key from config
with open("config/default.yaml") as f:
    config = yaml.safe_load(f)
    GEMINI_API_KEY = config["gemini_api_key"]

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def diagnose_cluster(prompt_override: str = None):
    cluster_info = get_cluster_summary()

    if prompt_override:
        prompt = f"{prompt_override}\n\nHere's the current cluster status:\n{cluster_info}"
    else:
        prompt = BASE_DIAGNOSIS_TEMPLATE.format(cluster_state=cluster_info)

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(GEMINI_API_URL, json=payload)

            if response.status_code == 200:
                data = response.json()
                return {
                    "prompt": prompt,
                    "cluster_snapshot": cluster_info,
                    "ai_response": data["candidates"][0]["content"]["parts"][0]["text"]
                }

            elif response.status_code == 503:
                # Retry with exponential backoff
                time.sleep(2 ** attempt)
                continue
            else:
                response.raise_for_status()

        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"❌ Gemini API request failed after retries: {e}")

