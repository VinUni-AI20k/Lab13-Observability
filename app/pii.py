from __future__ import annotations

import hashlib
import re
from typing import Any

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?(?:\d[ \.-]?){8,10}",  # Matches +84 90 123 4567, 090.123.4567, etc.
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # Common passport formats (incl. VN): B1234567, AB1234567, etc.
    "passport": r"\b[A-Z]{1,2}\d{6,8}\b",
    # Vietnamese address-ish phrases (keywords + short trailing segment)
    "address_vn": r"(?i)\b(?:(?:địa[ \t]*chỉ)|so|s[oố]|ngo|ngõ|hem|hẻm|duong|d[uư][oờ]ng|pho|phố|"
    r"phuong|ph[uư][oờ]ng|xa|xã|quan|q\.|huyen|huyện|tinh|tỉnh|"
    r"thi[ \t]*tran|thị[ \t]*trấn|thanh[ \t]*pho|thành[ \t]*phố|tp\.|"
    r"thon|thôn|ap|ấp|khu[ \t]*pho|khu[ \t]*phố)\b[\s:#\-]*[^,\n]{3,80}",
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def scrub_any(value: Any) -> Any:
    if isinstance(value, str):
        return scrub_text(value)
    if isinstance(value, dict):
        return {k: scrub_any(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub_any(v) for v in value]
    if isinstance(value, tuple):
        return tuple(scrub_any(v) for v in value)
    return value


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
