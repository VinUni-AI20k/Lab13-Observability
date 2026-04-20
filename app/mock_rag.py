from __future__ import annotations

import time

from .incidents import STATE
from .tracing import observe

CORPUS: dict[str, list[str]] = {
    "refund": [
        "Refunds are available within 7 days of delivery with proof of purchase.",
        "Refund is returned to the original payment method within 5-7 business days.",
        "Partial refunds are issued pro-rated for items returned from a multi-item order.",
    ],
    "partial": [
        "Partial refunds apply when only some items from an order are returned.",
        "Pro-rated amount is calculated based on items returned with proof of purchase.",
    ],
    "return": [
        "Return unused items in original packaging within 14 days for a size exchange or store credit.",
        "Items must be unworn, unwashed, and have all original tags attached.",
        "Sale items may only be exchanged for store credit, not cash refund.",
    ],
    "exchange": [
        "Size exchange is available within 14 days for the same product, subject to stock availability.",
        "If the requested size is out of stock, we offer store credit or a full refund.",
        "Gift items can be exchanged with a gift receipt for store credit within 14 days.",
    ],
    "shipping": [
        "Standard shipping takes 3-5 business days with a tracking number sent via email.",
        "Express shipping takes 1-2 business days for an extra fee.",
        "Remote provinces (e.g., Tây Nguyên, Tây Bắc) may take 5-7 business days with an additional fee.",
    ],
    "express": [
        "Express shipping is available for an extra fee and delivers in 1-2 business days.",
        "Express orders placed before 2 PM are dispatched same day.",
    ],
    "track": [
        "Use your order ID from the email confirmation to track your order on the carrier website.",
        "Tracking number is sent to your registered email within 24 hours of dispatch.",
    ],
    "lost": [
        "If your order has not arrived after 10 business days, contact support with your order ID.",
        "We will open a carrier investigation; resolution takes 3-5 business days.",
        "If confirmed lost, we issue a replacement or full refund.",
    ],
    "wrong": [
        "If you received the wrong item, take a photo and contact support within 48 hours.",
        "We will send a prepaid return label and dispatch the correct item immediately.",
    ],
    "warranty": [
        "Electronics carry a 12-month warranty against manufacturer defects.",
        "Proof of purchase is required to initiate a warranty claim.",
        "Bring the item to an authorized service center or contact our support for a mail-in claim.",
    ],
    "accidental": [
        "Accidental damage (drops, spills, physical damage) is not covered by the manufacturer warranty.",
        "Consider purchasing an extended protection plan for accidental damage coverage.",
    ],
    "cancel": [
        "You may cancel your order before it ships for a full refund.",
        "Contact support immediately with your order ID to request cancellation.",
        "Once shipped, cancellation is not possible; use the return process instead.",
    ],
    "payment": [
        "We accept credit card (Visa, Mastercard), bank transfer, COD, and e-wallet (MoMo, ZaloPay, VNPay).",
        "All payments are processed securely; we do not store full card numbers.",
    ],
    "discount": [
        "Enter your discount or promo code in the designated field at checkout.",
        "Only one promo code can be applied per order.",
        "Discount codes cannot be combined with other ongoing promotions.",
    ],
    "damaged": [
        "If your package arrives damaged, photograph the damage and contact support within 48 hours.",
        "We will arrange a replacement shipment or issue a full refund after reviewing photo evidence.",
    ],
    "dispute": [
        "To dispute a charge, provide your order ID and bank transaction reference to support.",
        "We will issue a receipt and work with your bank to resolve the dispute within 5-7 business days.",
    ],
    "address": [
        "You may change your shipping address before the order is shipped by contacting support.",
        "Once shipped, address changes are not possible; contact the carrier directly.",
    ],
    "escalate": [
        "To reach a human agent, call our support hotline during business hours (Mon-Sat 8AM-6PM).",
        "You can also email support@shopsagevn.com or use live chat on our website.",
    ],
    "gift": [
        "Gift items can be returned or exchanged with a gift receipt within 14 days.",
        "Store credit is issued for gift returns; no cash refund without original receipt.",
    ],
    "log": [
        "Never expose PII (email, phone, credit card, CCCD) in application logs.",
        "Use sanitized summaries, hashed user IDs, and REDACTED placeholders for sensitive fields.",
    ],
}

# Keys that should match Vietnamese language questions
_VI_ALIAS: dict[str, str] = {
    "hoàn tiền": "refund",
    "đổi size": "exchange",
    "đổi hàng": "return",
    "giao hàng": "shipping",
    "bảo hành": "warranty",
    "hủy đơn": "cancel",
    "theo dõi": "track",
    "thanh toán": "payment",
}


@observe(name="retrieve")
def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)

    lowered = message.lower()

    # Vietnamese alias resolution
    for vi_kw, en_key in _VI_ALIAS.items():
        if vi_kw in lowered:
            lowered = lowered + " " + en_key

    # Collect ALL matching corpus entries (multi-match for richer context)
    results: list[str] = []
    for key, docs in CORPUS.items():
        if key in lowered:
            results.extend(docs)

    if results:
        return results[:4]  # cap at 4 docs to avoid prompt bloat

    return ["No domain document matched. Please contact ShopSage VN support for further assistance."]
