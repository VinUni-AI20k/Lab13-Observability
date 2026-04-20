from __future__ import annotations

import time

from .incidents import STATE

CORPUS = {
    "refund": [
        "Refund requests are accepted within 7 days of delivery with proof of purchase.",
        "Refunds are processed to the original payment method in 3-5 business days.",
    ],
    "shipping": [
        "City center delivery usually takes 1-2 business days; outer districts take 3-5 business days.",
        "Shipping fee depends on destination and order value; failed delivery is retried once.",
    ],
    "warranty": [
        "Most electronics include a 12-month warranty from the purchase date.",
        "Warranty excludes physical damage, liquid damage, and unauthorized repairs.",
    ],
    "payment": [
        "Supported payment methods are COD, bank transfer, and domestic card.",
        "VAT invoices are available on request during checkout or via support.",
    ],
    "order": [
        "Customers can track order status by order id from the order tracking page.",
        "Delivery address can be changed only before the order is marked as shipped.",
    ],
}


def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    keyword_groups = {
        "refund": ["refund", "return"],
        "shipping": ["shipping", "delivery", "ship"],
        "warranty": ["warranty", "claim", "covered"],
        "payment": ["payment", "cod", "bank", "invoice", "vat"],
        "order": ["order", "tracking", "status", "address"],
    }
    for category, keywords in keyword_groups.items():
        if any(token in lowered for token in keywords):
            return CORPUS[category]
    return ["No domain document matched. Use general fallback answer."]
