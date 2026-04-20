from __future__ import annotations

import time

from .incidents import STATE
from .tracing import observe

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, traces localize them, logs explain root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
    # Banking-specific corpus (Member D)
    "vay": ["Lãi suất vay mua nhà từ 6.5%/năm, vay mua xe từ 7.5%/năm, vay tín chấp từ 12%/năm. Thời gian vay tối đa 20 năm."],
    "loan": ["Loan interest rates: Home loan 6.5%/year, car loan 7.5%/year, personal loan 12%/year. Maximum term 20 years."],
    "credit": ["Credit card limit depends on income. Minimum income 8M VND/month. Annual fee 500k-2M VND."],
    "thẻ": ["Hạn mức thẻ tín dụng phụ thuộc thu nhập. Thu nhập tối thiểu 8 triệu/tháng. Phí thường niên 500k-2M."],
    "account": ["Account balance can be checked via mobile app, internet banking, or ATM. No fee for balance inquiry."],
    "tài khoản": ["Số dư tài khoản có thể kiểm tra qua app, internet banking, hoặc ATM. Không mất phí tra cứu."],
    "payment": ["Payment schedule can be changed once per year. Late payment fee is 5% of overdue amount."],
    "trả nợ": ["Lịch trả nợ có thể thay đổi 1 lần/năm. Phí trả chậm là 5% số tiền quá hạn."],
}


@observe(name="rag-retrieve")
def retrieve(message: str) -> list[str]:
    # Original incidents
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    
    # Banking-specific incidents (Member D)
    if STATE["account_lookup_slow"]:
        time.sleep(2.5)  # Simulate slow account lookup
    
    if STATE["core_banking_fail"]:
        raise RuntimeError("Core banking system unavailable")
    
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            return docs
    return ["No domain document matched. Use general fallback answer."]
