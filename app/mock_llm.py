from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path

from .incidents import STATE
from .tracing import observe

EXPECTED_ANSWERS_PATH = Path("data/expected_answers.jsonl")


def _load_expected() -> list[dict]:
    if not EXPECTED_ANSWERS_PATH.exists():
        return []
    out = []
    for line in EXPECTED_ANSWERS_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                raw = json.loads(line)
                if not isinstance(raw, dict):
                    continue
                question = raw.get("question")
                if not isinstance(question, str) or not question.strip():
                    continue
                must_include = raw.get("must_include", [])
                if not isinstance(must_include, list):
                    must_include = []
                must_include = [str(x) for x in must_include if isinstance(x, (str, int, float))]
                out.append({"question": question, "must_include": must_include})
            except json.JSONDecodeError:
                pass
    return out


_EXPECTED: list[dict] = _load_expected()


def _match_answer(question: str) -> str | None:
    q_lower = question.lower()
    best: tuple[int, str | None] = (0, None)
    for entry in _EXPECTED:
        eq = entry.get("question")
        if not isinstance(eq, str):
            continue
        eq_lower = eq.lower()
        score = sum(1 for kw in eq_lower.split() if kw in q_lower)
        if score > best[0]:
            must_include = entry.get("must_include", [])
            if not isinstance(must_include, list):
                must_include = []
            best = (score, ". ".join(str(x) for x in must_include if str(x).strip()))
    return best[1] if best[0] > 0 else None


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    @observe(name="llm_generate")
    def generate(self, prompt: str) -> FakeResponse:
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4

        question_line = next(
            (line for line in prompt.splitlines() if line.startswith("Question=")), ""
        )
        question = question_line.removeprefix("Question=").strip()
        matched = _match_answer(question) if question else None

        if matched:
            answer = f"ShopSage VN: {matched}."
        else:
            answer = (
                "Thank you for contacting ShopSage VN support. "
                "Please provide more details so we can assist you with your order."
            )

        return FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)
