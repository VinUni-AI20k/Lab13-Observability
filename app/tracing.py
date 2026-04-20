from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import observe, get_client as _get_client

    class _LangfuseContext:
        """Compatibility shim mapping the v2 langfuse_context API to the v3 get_client() API."""

        def update_current_trace(self, **kwargs: Any) -> None:
            _get_client().update_current_trace(**kwargs)

        def update_current_observation(self, **kwargs: Any) -> None:
            # update_current_generation is a superset of update_current_span,
            # accepting all span params (input/output/metadata) plus generation-
            # specific ones (model/usage_details), so it works for both call sites.
            _get_client().update_current_generation(**kwargs)

    langfuse_context = _LangfuseContext()

except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):  # type: ignore[misc]
        def decorator(func):
            return func
        return decorator

    class _DummyContext:  # type: ignore[no-redef]
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
