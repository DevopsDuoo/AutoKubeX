# ai_engine/learner.py
import os
import json
import joblib
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from k8s_connector.kube_api import get_pod_summary
from ai_engine.feedback_db import fetch_feedback_data

MODEL_PATH = "ai_engine/models/k8s_diagnosis_model.pkl"


def extract_features():
    """Extract simplified features from cluster summary"""
    summary = get_pod_summary()
    data = []
    for item in summary:
        pod_name = item['name']
        namespace = item['namespace']
        restarts = item.get('restartCount', 0)
        status = item.get('status', 'Unknown')
        data.append({
            "namespace": namespace,
            "pod_name": pod_name,
            "restarts": restarts,
            "is_healthy": int(status.lower() == 'running' and restarts < 2)
        })
    return pd.DataFrame(data)


def train_model():
    df = extract_features()
    if df.empty:
        print("[!] No data found for training.")
        return

    X = df[["restarts"]]  # Simple feature: restart count
    y = df["is_healthy"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    clf = LogisticRegression()
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("[+] Classification Report:")
    print(classification_report(y_test, y_pred))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"[+] Model saved to {MODEL_PATH}")


def predict_restart_issue(restart_count):
    if not os.path.exists(MODEL_PATH):
        print("[!] Model not trained yet.")
        return None
    clf = joblib.load(MODEL_PATH)
    return clf.predict([[restart_count]])[0]


def retrain_from_feedback():
    print("[+] Retraining from user feedback...")
    feedback_data = fetch_feedback_data()
    if feedback_data.empty:
        print("[!] No feedback data found.")
        return

    X = feedback_data[["restarts"]]
    y = feedback_data["label"]
    clf = LogisticRegression()
    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)
    print("[+] Model updated with feedback data.")
