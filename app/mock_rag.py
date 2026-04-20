from __future__ import annotations

import time

from .incidents import STATE
from .pii import summarize_text
from .tracing import langfuse_context, observe

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, traces localize them, logs explain root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


@observe()
def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    matched_key = None
    for key, docs in CORPUS.items():
        if key in lowered:
            matched_key = key
            langfuse_context.update_current_observation(
                input=summarize_text(message),
                output=f"{len(docs)} docs",
                metadata={"matched_key": matched_key, "doc_count": len(docs), "rag_slow": STATE["rag_slow"]},
            )
            return docs
    fallback_docs = ["No domain document matched. Use general fallback answer."]
    langfuse_context.update_current_observation(
        input=summarize_text(message),
        output="fallback docs",
        metadata={"matched_key": matched_key, "doc_count": len(fallback_docs), "rag_slow": STATE["rag_slow"]},
    )
    return fallback_docs
