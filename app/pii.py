from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
<<<<<<< HEAD
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}", # Matches 090 123 4567, 090.123.4567, etc.
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # TODO: Add more patterns (e.g., Passport, Vietnamese address keywords)
=======
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "cccd": r"\b\d{12}\b",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}",
    "passport": r"\b[A-Z]\d{7,8}\b",
    "vn_address": r"(?:số\s+\d+|đường\s+\S+|phường\s+\S+|quận\s+\S+|huyện\s+\S+|tỉnh\s+\S+|thành phố\s+\S+)",
>>>>>>> ba19a49 (feat(pii): implement PII scrubbing 6 regex patterns - Vu Hoang Minh (2A202600440))
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
