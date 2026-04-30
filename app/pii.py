from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    # CCCD must come before phone_vn — both can start with 0; longer match takes priority
    "cccd": r"\b\d{12}\b",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}", # Matches 090 123 4567, 090.123.4567, etc.
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # Vietnamese passport: 1 uppercase letter followed by 7-8 digits (e.g., B1234567, C12345678)
    "passport_vn": r"\b[A-Z]\d{7,8}\b",
    # Vietnamese address fragments with location keywords + following name/number
    "address_vn": r"\b(?:\d+\s+)?(?:đường|phường|quận|huyện|tỉnh|xã|thành phố|tp\.?)\s+[\w\sÀ-ỹ]{2,40}",
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
