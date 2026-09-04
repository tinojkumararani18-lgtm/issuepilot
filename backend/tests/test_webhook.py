import hashlib
import hmac
import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings

def test_webhook_rejects_bad_signature():
    client = TestClient(app)
    response = client.post("/api/webhooks/github",
                           headers={"X-GitHub-Event": "ping", "X-Hub-Signature-256": "sha256=bad"},
                           content=b"{}")
    assert response.status_code == 401

def test_webhook_accepts_valid_signature():
    settings = get_settings()
    body = json.dumps({"zen": "Keep it logically awesome."}).encode()
    digest = hmac.new(settings.github_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    client = TestClient(app)
    response = client.post("/api/webhooks/github",
                           headers={"X-GitHub-Event": "ping", "X-Hub-Signature-256": f"sha256={digest}"},
                           content=body)
    assert response.status_code == 200
    assert response.json()["processed"] is False
