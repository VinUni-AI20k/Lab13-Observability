from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client, observe

    class _LangfuseContextAdapter:
        def _client(self):
            # Resolve lazily so .env can be loaded before first trace call.
            return get_client()

        def update_current_trace(self, **kwargs: Any) -> None:
            client = self._client()
            if hasattr(client, "update_current_trace"):
                client.update_current_trace(**kwargs)
                return

            # Langfuse v4 removed update_current_trace; keep trace context as span metadata.
            metadata = {"trace_context": kwargs} if kwargs else None
            client.update_current_span(metadata=metadata)

        def update_current_observation(self, **kwargs: Any) -> None:
            # In Langfuse v3, generations carry model usage and metadata.
            self._client().update_current_generation(**kwargs)

    langfuse_context = _LangfuseContextAdapter()
    _LANGFUSE_IMPORT_OK = True
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()
    _LANGFUSE_IMPORT_OK = False


def tracing_enabled() -> bool:
    return bool(
        _LANGFUSE_IMPORT_OK
        and os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
    )
