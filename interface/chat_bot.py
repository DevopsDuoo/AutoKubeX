import os
import slack_sdk
from slack_sdk.webhook import WebhookClient
from ai_engine.planner import diagnose_cluster

slack_url = os.getenv("SLACK_WEBHOOK_URL")
webhook = WebhookClient(slack_url)

def send_diagnosis():
    message = diagnose_cluster()
    response = webhook.send(text=f"AutoKubeX Diagnosis:\n{message}")
    print("[Bot] Message sent:", response.status_code)