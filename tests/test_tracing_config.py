from app.tracing import tracing_enabled


def test_tracing_enabled_when_langfuse_keys_present(monkeypatch) -> None:
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")

    assert tracing_enabled() is True


def test_tracing_disabled_when_langfuse_keys_missing(monkeypatch) -> None:
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)

    assert tracing_enabled() is False
