import json
import tempfile
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.agent import AgentResult
from app.main import app
from app.pii import hash_user_id


def test_chat_logs_include_enrichment_fields(monkeypatch) -> None:
    log_path = Path(tempfile.gettempdir()) / f"test_chat_enrichment_logs_{uuid.uuid4().hex}.jsonl"
    monkeypatch.setattr("app.logging_config.LOG_PATH", log_path)
    monkeypatch.setattr(
        "app.main.agent.run",
        lambda **kwargs: AgentResult(
            answer="Da Nang itinerary answer",
            latency_ms=210,
            tokens_in=111,
            tokens_out=222,
            cost_usd=0.0037,
            quality_score=0.9,
        ),
    )
    monkeypatch.setattr("app.main.langfuse_context.flush", lambda: None)

    client = TestClient(app)
    response = client.post(
        "/chat",
        json={
            "user_id": "traveler-01",
            "session_id": "s-danang",
            "feature": "qa",
            "message": "Plan a Da Nang beach trip for me",
        },
    )

    assert response.status_code == 200

    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    api_records = [record for record in records if record.get("service") == "api"]

    assert [record["event"] for record in api_records] == ["request_received", "response_sent"]
    for record in api_records:
        assert record["user_id_hash"] == hash_user_id("traveler-01")
        assert record["session_id"] == "s-danang"
        assert record["feature"] == "qa"
        assert record["model"] == "claude-sonnet-4-5"
        assert record["env"] == "dev"
