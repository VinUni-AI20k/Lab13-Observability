from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .incidents import STATE


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


from .tracing import langfuse_context, observe


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    @observe(as_type="generation", name="llm-generation")
    def generate(self, prompt: str) -> FakeResponse:
        langfuse_context.update_current_observation(
            model=self.model,
            input=prompt,
        )
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4
        answer = (
            "Starter answer. Teams should improve this output logic and add better quality checks. "
            "Use retrieved context and keep responses concise."
        )
        response = FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)
        langfuse_context.update_current_observation(
            output=response.text,
            usage_details={"input": input_tokens, "output": output_tokens},
        )
        return response
