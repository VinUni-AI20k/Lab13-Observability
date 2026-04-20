from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "cccd": r"\b\d{12}\b",  # Must be before phone/bank to avoid partial matches
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "phone_vn": r"\b(?:\+84|0)\d{9,10}\b", # 0901234567, +84901234567
    "passport": r"\b[A-Z]{1,2}\d{7,8}\b", # A1234567, AB12345678
    "bank_account": r"\b\d{9,12}\b", # 9-12 consecutive digits (avoid 8-digit conflicts)
    "vn_address": r"(?:duong|pho|quan|huyen|tp|thanh\s*pho|so\s*nha|thon|xa|ap|to)\s+[^\s,]+", # Vietnamese address keywords
    "zip_code": r"\b\d{5,6}\b", # Zip/postal codes
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
