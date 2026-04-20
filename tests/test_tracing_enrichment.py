from types import SimpleNamespace

from app.agent import LabAgent
from app.pii import hash_user_id


class DummyLangfuseContext:
    def __init__(self) -> None:
        self.trace_updates: list[dict] = []
        self.observation_updates: list[dict] = []

    def update_current_trace(self, **kwargs) -> None:
        self.trace_updates.append(kwargs)

    def update_current_observation(self, **kwargs) -> None:
        self.observation_updates.append(kwargs)


def test_agent_tracing_metadata(monkeypatch) -> None:
    context = DummyLangfuseContext()
    monkeypatch.setattr("app.agent.langfuse_context", context)
    monkeypatch.setattr("app.agent.retrieve", lambda message: ["Da Nang itinerary context"])
    monkeypatch.setattr(
        "app.agent.FakeLLM.generate",
        lambda self, prompt: SimpleNamespace(
            text="Da Nang travel plan with beach stay and breakfast included.",
            usage=SimpleNamespace(input_tokens=120, output_tokens=180),
            model=self.model,
        ),
    )

    agent = LabAgent(model="claude-sonnet-4-5")
    agent.run(
        user_id="traveler-01",
        feature="qa",
        session_id="s-danang",
        message="Plan my Da Nang trip around My Khe beach",
    )

    assert context.trace_updates == [
        {
            "user_id": hash_user_id("traveler-01"),
            "session_id": "s-danang",
            "tags": [
                "lab",
                "danang-travel-planner",
                "feature:qa",
                "model:claude-sonnet-4-5",
            ],
        }
    ]
    assert context.observation_updates == [
        {
            "metadata": {
                "doc_count": 1,
                "query_preview": "Plan my Da Nang trip around My Khe beach",
                "domain": "danang-travel",
                "city": "da-nang",
            },
            "usage_details": {"input": 120, "output": 180},
        }
    ]
