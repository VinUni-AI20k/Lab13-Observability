from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# PII Patterns – Vietnamese Banking / Credit Card Context
# Compiled upfront for performance (chatbot calls scrub_text on every message)
# ---------------------------------------------------------------------------

@dataclass
class _PIIRule:
    """Bundles a compiled pattern with its display label."""
    pattern: re.Pattern[str]
    label: str


_RULES: list[_PIIRule] = [
    # ── Email ──────────────────────────────────────────────────────────────
    _PIIRule(
        re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.IGNORECASE),
        "EMAIL",
    ),

    # ── Vietnamese phone ───────────────────────────────────────────────────
    # Covers: +84-xxx-xxx-xxxx / 0xxx xxx xxxx / 0xxxxxxxxxx
    _PIIRule(
        re.compile(
            r"(?<!\d)(?:\+84|0)[ .\-]?\d{3}[ .\-]?\d{3}[ .\-]?\d{3,4}(?!\d)"
        ),
        "PHONE_VN",
    ),

    # ── Credit card ────────────────────────────────────────────────────────
    # Catches "4111 2222 3333 4444", "4111-2222-3333-4444", "4111222233334444"
    # Luhn-check would need code; regex alone catches the format.
    _PIIRule(
        re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b"),
        "CREDIT_CARD",
    ),

    # ── CCCD / CMND ────────────────────────────────────────────────────────
    # Priority 1: keyword + digits (high confidence, catches 9 & 12 digit forms)
    # Priority 2: bare 12-digit string (lower confidence but needed for raw input)
    _PIIRule(
        re.compile(
            r"(?i)"
            r"(?:CCCD|CMND|căn\s+cước|chứng\s+minh(?:\s+nhân?\s+dân)?)[\s:#]*\d{9,12}"
            r"|\b\d{12}\b",
            re.UNICODE,
        ),
        "CCCD",
    ),

    # ── Vietnamese Passport ────────────────────────────────────────────────
    # VN format: 1 uppercase letter + 7 digits  e.g. B1234567, C9876543
    # The image example "B12345" is likely truncated; real passports are 8 chars.
    _PIIRule(
        re.compile(r"\b[A-Za-z]\d{7}\b"),
        "PASSPORT",
    ),

    # ── Bank account number (context-aware) ───────────────────────────────
    _PIIRule(
        re.compile(
            r"(?i)(?:số\s+tài\s+khoản|STK|tài\s+khoản\s+(?:số|ngân\s+hàng))"
            r"[\s:#]*\d{6,16}",
            re.UNICODE,
        ),
        "BANK_ACCOUNT",
    ),

    # ── Date of birth ──────────────────────────────────────────────────────
    _PIIRule(
        re.compile(
            r"(?i)(?:ngày\s+sinh|sinh\s+ngày|DOB|ngày[/\-\.]tháng[/\-\.]năm\s+sinh)"
            r"[\s:]*\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4}",
            re.UNICODE,
        ),
        "DOB",
    ),

    # ── Vietnamese address (keyword-anchored, length-bounded) ──────────────
    # "Số" alone is too generic – require a digit right after (house number).
    # Other street/ward keywords are specific enough to match freely.
    _PIIRule(
        re.compile(
            r"(?i)"
            r"(?:\bSố\s+\d+[^,.\n]{0,50})"
            r"|(?:\b(?:Ngõ|Ngách|Hẻm|Xóm|Thôn|Ấp|Đường|Phố|Phường|Xã|Quận|Huyện"
            r"|Thành\s+phố|Tỉnh|Thị\s+xã|Thị\s+trấn)\s+[^,.\n]{1,60})",
            re.UNICODE,
        ),
        "ADDRESS_VN",
    ),

    # ── IPv4 address ───────────────────────────────────────────────────────
    _PIIRule(
        re.compile(
            r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
            r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
        ),
        "IP_ADDRESS",
    ),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrub_text(text: str) -> str:
    """Replace every detected PII token with [REDACTED_<TYPE>]."""
    safe = text
    for rule in _RULES:
        safe = rule.pattern.sub(f"[REDACTED_{rule.label}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    """Scrub PII then return a single-line preview of at most *max_len* chars."""
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    """Return a short, irreversible fingerprint for a user identifier."""
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Quick smoke-test  (run:  python pii_utils.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        # From the project brief
        'Tôi muốn khóa khẩn cấp thẻ credit mang số 4111 2222 3333 4444.',
        'Số passport mặt trước của tôi là B1234567.',
        # Other common cases
        'Email của tôi: nguyen.van.a@gmail.com, SĐT: 0912 345 678',
        'CCCD: 079202012345, sinh ngày 01/01/1990',
        'Số tài khoản: 1234567890, ngân hàng Vietcombank',
        'Địa chỉ: Đường Lê Lợi, Phường Bến Nghé, Quận 1',
    ]

    print("=== PII Scrubbing Demo ===\n")
    for s in samples:
        print(f"  IN : {s}")
        print(f"  OUT: {scrub_text(s)}")
        print()