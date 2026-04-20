from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import observe
    from opentelemetry import trace as otel_trace

    import json

    class _LangfuseContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            span = otel_trace.get_current_span()
            if span and span.is_recording():
                if "tags" in kwargs:
                    span.set_attribute("langfuse.trace.tags", kwargs["tags"])
                if "user_id" in kwargs:
                    span.set_attribute("user.id", kwargs["user_id"])
                if "session_id" in kwargs:
                    span.set_attribute("session.id", kwargs["session_id"])
                if "metadata" in kwargs:
                    for k, v in kwargs["metadata"].items():
                        span.set_attribute(f"langfuse.trace.metadata.{k}", self._serialize(v))

        def update_current_observation(self, **kwargs: Any) -> None:
            span = otel_trace.get_current_span()
            if span and span.is_recording():
                if "usage_details" in kwargs:
                    span.set_attribute("langfuse.observation.usage_details", self._serialize(kwargs["usage_details"]))
                if "cost_details" in kwargs:
                    span.set_attribute("langfuse.observation.cost_details", self._serialize(kwargs["cost_details"]))
                if "model" in kwargs:
                    span.set_attribute("langfuse.observation.model.name", kwargs["model"])
                if "metadata" in kwargs:
                    for k, v in kwargs["metadata"].items():
                        span.set_attribute(f"langfuse.observation.metadata.{k}", self._serialize(v))
                
                # Handle other arbitrary kwargs
                for k, v in kwargs.items():
                    if k not in ["usage_details", "cost_details", "model", "metadata"]:
                        span.set_attribute(f"langfuse.observation.{k}", self._serialize(v))

        def _serialize(self, obj: Any) -> str:
            if isinstance(obj, (str, int, float, bool)):
                return str(obj)
            return json.dumps(obj)

    langfuse_context = _LangfuseContext()

except ImportError:  # pragma: no cover
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


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
