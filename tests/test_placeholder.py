import pytest
from ai_engine.learner import log_incident, get_recent_issues

def test_log_and_retrieve():
    log_incident("test-pod", "default", "CrashLoopBackOff", "2025-05-07T00:00:00Z")
    results = get_recent_issues()
    assert any("test-pod" in r for r in results)