from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client, observe

    class _LangfuseContext:
        def __init__(self) -> None:
            self._client = get_client()

        def update_current_trace(self, **kwargs: Any) -> None:
            self._client.update_current_trace(**kwargs)

        def update_current_observation(self, **kwargs: Any) -> None:
            metadata = kwargs.get("metadata")
            usage_details = kwargs.get("usage_details")
            merged_metadata = dict(metadata) if isinstance(metadata, dict) else {}
            if usage_details is not None:
                merged_metadata["usage_details"] = usage_details
            self._client.update_current_span(metadata=merged_metadata or None)

        def flush(self) -> None:
            self._client.flush()

    langfuse_context = _LangfuseContext()
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

        def flush(self) -> None:
            return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
