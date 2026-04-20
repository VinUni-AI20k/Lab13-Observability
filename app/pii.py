from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "passport": r"\b[A-Z]{1,2}\d{6,8}\b",
    "address_vn": r"\b(Hà Nội|TP\.HCM|Hồ Chí Minh|Đà Nẵng|Hải Phòng|Cần Thơ)\b",
    "bank_account": r"(?:stk|số tài khoản|tài khoản|bank account|acc)\s*[:=]?\s*\d{8,15}",
    "currency_vn": r"(?:học phí|tiền|chi phí)\s*[:=]?\s*\d{1,3}(?:[.,]\d{3})*(?:\s*VND|\s*VNĐ|\s*đồng)?",
    "student_id": r"\b(?:VS|VSC|VINS)[-|_]?\d{4,8}\b",
    "student_name": r"(?:bé|học sinh|con|cháu|phụ huynh|anh|chị)\s+[A-ZĐ][a-zàáâãèéêìíòóôõùúăđĩũơạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]*(?:\s+[A-ZĐ][a-zàáâãèéêìíòóôõùúăđĩũơạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]*)*",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe, flags=re.IGNORECASE)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
