from __future__ import annotations

import os
import time
from dataclasses import dataclass

from .incidents import status as incident_status
from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import observe, safe_score_current_observation, safe_update_current_observation


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe(name="agent-run")
    def run(self, user_id: str, feature: str, session_id: str, message: str, correlation_id: str | None = None) -> AgentResult:
        incidents = incident_status()
        safe_update_current_observation(
            user_id=hash_user_id(user_id),
            session_id=session_id,
            tags=["lab", feature, self.model],
            metadata={
                "correlation_id": correlation_id,
                "feature": feature,
                "model": self.model,
                "environment": os.getenv("APP_ENV", "dev"),
                "incident_rag_slow": incidents.get("rag_slow", False),
                "incident_tool_fail": incidents.get("tool_fail", False),
                "incident_cost_spike": incidents.get("cost_spike", False),
            },
            input={"message_preview": summarize_text(message)},
        )

        started = time.perf_counter()
        try:
            docs = retrieve(message)
            retrieval_hit = 1.0 if (len(docs) > 0 and "No domain document matched" not in docs[0]) else 0.0
            prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
            response = self.llm.generate(prompt)
            quality_score = self._heuristic_quality(message, response.text, docs)
            latency_ms = int((time.perf_counter() - started) * 1000)
            cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)

            safe_update_current_observation(
                output=summarize_text(response.text, max_len=240),
                metadata={
                    "doc_count": len(docs),
                    "retrieval_hit": bool(retrieval_hit),
                    "query_preview": summarize_text(message),
                },
            )

            safe_score_current_observation("quality_score", float(quality_score))
            safe_score_current_observation("retrieval_hit", float(retrieval_hit))
            safe_score_current_observation("response_helpful_heuristic", float(1.0 if quality_score >= 0.7 else 0.0))

            metrics.record_request(
                latency_ms=latency_ms,
                cost_usd=cost_usd,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                quality_score=quality_score,
            )

            return AgentResult(
                answer=response.text,
                latency_ms=latency_ms,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                cost_usd=cost_usd,
                quality_score=quality_score,
            )
        except Exception as exc:
            safe_update_current_observation(metadata={"error_type": type(exc).__name__}, tags=["error"])
            raise

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
