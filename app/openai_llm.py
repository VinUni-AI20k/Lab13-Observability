from __future__ import annotations

import os
import re
from collections import defaultdict
from dataclasses import dataclass

import dotenv
dotenv.load_dotenv()

from .incidents import STATE
from .prompts import get_system_prompt

try:
    from openai import OpenAI as _OpenAI
    from openai import AuthenticationError, NotFoundError
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AuthenticationError = NotFoundError = Exception


@dataclass
class LLMUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class LLMResponse:
    text: str
    usage: LLMUsage
    model: str
    issue_type: str  # BUG | FEATURE_REQUEST | QUESTION | UNKNOWN


# Per-session conversation history (excludes system prompt)
_history: dict[str, list[dict]] = defaultdict(list)
MAX_TURNS = 10


def _parse_type(text: str) -> tuple[str, str]:
    m = re.match(r"\[TYPE:\s*(BUG|FEATURE_REQUEST|QUESTION)\]", text.strip(), re.IGNORECASE)
    if m:
        return m.group(1).upper(), text[m.end():].strip()
    return "UNKNOWN", text.strip()


class OpenAILLM:
    """
    Hybrid LLM: tries real OpenAI API first, auto-falls back to Smart Mock
    after 2 consecutive failures (auth error, model not found, network, etc.)
    """
    _FAIL_LIMIT = 2

    def __init__(self, model: str = "gpt-5.4-nano") -> None:
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY", "")
        if _AVAILABLE and api_key:
            self._client = _OpenAI(api_key=api_key)
            self._has_key = True
        else:
            self._client = None
            self._has_key = False

        self._mode    = "live" if self._has_key else "demo"
        self._failures = 0

    # ── Public interface ──────────────────────────────────────────────────────

    @property
    def enabled(self) -> bool:
        return self._has_key

    @property
    def mode(self) -> str:
        """'live' = using real OpenAI  |  'demo' = using Smart Mock"""
        return self._mode

    def generate(
        self,
        prompt: str,
        session_id: str = "default",
        persona: str = "default",
    ) -> LLMResponse:
        # ── Always use Smart Mock if no key or already in demo mode ──
        if self._mode == "demo" or not self._has_key:
            return self._smart_mock(prompt)

        # ── Try real OpenAI call ──
        history = _history[session_id]
        history.append({"role": "user", "content": prompt})
        if len(history) > MAX_TURNS * 2:
            history[:] = history[-MAX_TURNS * 2:]

        system = get_system_prompt(persona)
        if STATE["cost_spike"]:
            system += "\n\nQUAN TRỌNG: Giải thích cực kỳ chi tiết với nhiều ví dụ thực tế."

        messages = [{"role": "system", "content": system}] + list(history)

        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=600 if STATE["cost_spike"] else 400,
            )
            raw = resp.choices[0].message.content or ""
            history.append({"role": "assistant", "content": raw})
            self._failures = 0
            self._mode = "live"
            issue_type, clean = _parse_type(raw)
            return LLMResponse(
                text=clean,
                usage=LLMUsage(resp.usage.prompt_tokens, resp.usage.completion_tokens),
                model=resp.model,
                issue_type=issue_type,
            )

        except (AuthenticationError, NotFoundError) as exc:
            # Invalid key or model doesn't exist → switch to demo permanently
            history.pop()
            self._failures = self._FAIL_LIMIT  # trigger immediately
            self._mode = "demo"
            import logging
            logging.getLogger(__name__).warning(
                "OpenAI auth/model error (%s) — switching to Smart Mock permanently.", exc
            )
            return self._smart_mock(prompt)

        except Exception as exc:
            # Network error, rate limit, etc. → try smart mock, may recover later
            history.pop()
            self._failures += 1
            if self._failures >= self._FAIL_LIMIT:
                self._mode = "demo"
            import logging
            logging.getLogger(__name__).warning(
                "OpenAI call failed (%s) — falling back to Smart Mock (failures: %d).",
                exc, self._failures,
            )
            return self._smart_mock(prompt)

    def clear_history(self, session_id: str) -> None:
        _history.pop(session_id, None)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _smart_mock(self, prompt: str) -> LLMResponse:
        from . import smart_mock
        return smart_mock.generate(prompt)
