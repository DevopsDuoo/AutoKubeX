# ai_engine/planner.py
import requests
import yaml
from ai_engine.prompt_templates import BASE_DIAGNOSIS_TEMPLATE
from k8s_connector.kube_api import get_cluster_summary

with open("config/default.yaml") as f:
    config = yaml.safe_load(f)
    GEMINI_API_KEY = config["gemini_api_key"]

def diagnose_cluster():
    cluster_info = get_cluster_summary()
    prompt = BASE_DIAGNOSIS_TEMPLATE.format(cluster_state=cluster_info)

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        json=payload
    )
    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]
