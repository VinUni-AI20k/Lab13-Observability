from __future__ import annotations

import time
from dataclasses import dataclass, field

from . import metrics
from .mock_rag import retrieve
from .openai_llm import OpenAILLM
from .pii import hash_user_id, summarize_text
from .tracing import langfuse_context, observe


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float
    issue_type: str = "UNKNOWN"
    model_used: str = "gpt-5.4-nano"


class LabAgent:
    def __init__(self, model: str = "gpt-5.4-nano") -> None:
        self.model = model
        self.llm = OpenAILLM(model=model)

    @observe()
    def run(
        self,
        user_id: str,
        feature: str,
        session_id: str,
        message: str,
        persona: str = "default",
    ) -> AgentResult:
        started = time.perf_counter()
        docs = retrieve(message)
        prompt = self._build_prompt(feature, docs, message)
        response = self.llm.generate(prompt, session_id=session_id, persona=persona)
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)

        langfuse_context.update_current_trace(
            user_id=hash_user_id(user_id),
            session_id=session_id,
            tags=["lab", feature, response.model],
        )
        langfuse_context.update_current_observation(
            metadata={
                "doc_count": len(docs),
                "query_preview": summarize_text(message),
                "issue_type": response.issue_type,
            },
            usage_details={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            },
        )

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
            issue_type=response.issue_type,
            model_used=response.model,
        )

    def clear_session(self, session_id: str) -> None:
        self.llm.clear_history(session_id)

    def _build_prompt(self, feature: str, docs: list[str], message: str) -> str:
        ctx = "\n---\n".join(docs) if docs else "Không có tài liệu liên quan."
        if feature == "summary":
            return f"Tóm tắt yêu cầu của khách hàng:\n{message}\n\nNgữ cảnh:\n{ctx}"
        return f"Câu hỏi của khách hàng: {message}\n\nTài liệu tham khảo:\n{ctx}"

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        # gpt-4o-mini pricing: $0.150/M input, $0.600/M output
        return round((tokens_in / 1_000_000) * 0.15 + (tokens_out / 1_000_000) * 0.60, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if any(t in answer.lower() for t in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
