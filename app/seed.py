"""
Seed sample conversation logs for demo dashboard.
Writes directly to LOG_PATH (append mode).
"""
from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timedelta, timezone

from .logging_config import LOG_PATH
from .pii import scrub_text

_SAMPLES: list[tuple[str, str, str]] = [
    # (user_query_preview, issue_type, event)
    ("Camera bị lỗi đăng nhập, báo 'Invalid credentials'",   "BUG",              "response_sent"),
    ("Giá camera 4K PTZ zoom 30x là bao nhiêu?",              "QUESTION",         "response_sent"),
    ("Hướng dẫn cấu hình NVR 16 kênh cho văn phòng",         "QUESTION",         "response_sent"),
    ("Camera mất kết nối WiFi liên tục sau 10 phút",          "BUG",              "response_sent"),
    ("Muốn thêm tính năng nhận diện biển số xe",              "FEATURE_REQUEST",  "response_sent"),
    ("Firmware v3.2 có hỗ trợ AI detection không?",           "QUESTION",         "response_sent"),
    ("Switch PoE 8 cổng không cấp nguồn cho camera",          "BUG",              "response_sent"),
    ("Xem camera từ xa qua Android không được, lỗi gì?",      "BUG",              "response_sent"),
    ("Chính sách bảo hành NVR bao lâu?",                      "QUESTION",         "response_sent"),
    ("Tích hợp camera vào Home Assistant qua ONVIF",          "QUESTION",         "response_sent"),
    ("Muốn thêm cảnh báo qua SMS khi phát hiện xâm nhập",    "FEATURE_REQUEST",  "response_sent"),
    ("Đầu ghi không nhận ổ cứng Seagate SkyHawk 4TB",         "BUG",              "response_sent"),
    ("Báo giá switch PoE 8 cổng cho văn phòng 10 người",      "QUESTION",         "response_sent"),
    ("Camera hồng ngoại bị mờ vào ban đêm",                   "BUG",              "response_sent"),
    ("Hỏi về gói lắp đặt trọn gói 10 camera IP 5MP",         "QUESTION",         "response_sent"),
    ("Cổng RTSP mặc định của camera IP là bao nhiêu?",        "QUESTION",         "response_sent"),
    ("Muốn tính năng ghi âm kèm video 2 chiều",               "FEATURE_REQUEST",  "response_sent"),
    ("NVR không ghi video khi phát hiện chuyển động",         "BUG",              "response_sent"),
    ("So sánh định dạng H.264 và H.265+ về chất lượng",      "QUESTION",         "response_sent"),
    ("Camera ngoài trời bị đọng sương trong sau cơn mưa",    "BUG",              "response_sent"),
]

_ANSWERS = {
    "BUG": (
        "Đã tiếp nhận báo cáo lỗi. Vui lòng thử: 1) Khởi động lại thiết bị. "
        "2) Cập nhật firmware mới nhất. 3) Liên hệ kỹ thuật nếu vẫn còn lỗi."
    ),
    "FEATURE_REQUEST": (
        "Cảm ơn đề xuất! Yêu cầu đã được ghi nhận và chuyển đến team sản phẩm."
    ),
    "QUESTION": (
        "Cảm ơn câu hỏi! Chúng tôi hỗ trợ đầy đủ tính năng này. "
        "Liên hệ sales@ipstore.vn để biết thêm chi tiết."
    ),
}


def _sentiment(quality: float) -> str:
    if quality >= 0.85:
        return "positive"
    if quality >= 0.65:
        return "neutral"
    return "negative"


def seed(n: int = 20, reset: bool = False) -> int:
    """
    Append n sample log records to LOG_PATH.
    If reset=True, clears existing logs first.
    Returns the number of records written.
    """
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if reset:
        LOG_PATH.write_text("", encoding="utf-8")

    now    = datetime.now(timezone.utc)
    sample = (_SAMPLES * 3)[:n]  # repeat if n > len(_SAMPLES)
    records: list[dict] = []

    for i, (query, issue_type, event) in enumerate(sample):
        # Spread timestamps over the last 2 hours, newest first
        offset_sec  = int(i * (7200 / n)) + random.randint(0, 30)
        ts          = (now - timedelta(seconds=offset_sec)).isoformat()
        corr_id     = f"req-{uuid.uuid4().hex[:8]}"
        session_id  = f"s-seed-{i:02d}"
        latency_ms  = random.randint(120, 800)
        tokens_in   = random.randint(40, 120)
        tokens_out  = random.randint(80, 220)
        cost_usd    = round((tokens_in / 1_000_000) * 0.15 + (tokens_out / 1_000_000) * 0.60, 6)
        quality     = round(random.uniform(0.70, 0.95), 2)
        feature     = random.choice(["qa", "qa", "summary"])

        records.append({
            "ts":             ts,
            "level":          "info",
            "service":        "api",
            "event":          event,
            "correlation_id": corr_id,
            "env":            "dev",
            "user_id_hash":   f"seed{i:02d}hash",
            "session_id":     session_id,
            "feature":        feature,
            "model":          "mock-smart",
            "model_used":     "mock-smart",
            "latency_ms":     latency_ms,
            "tokens_in":      tokens_in,
            "tokens_out":     tokens_out,
            "cost_usd":       cost_usd,
            "issue_type":     issue_type,
            "payload": {
                "answer_preview": scrub_text(_ANSWERS[issue_type])[:80] + "…",
                "metadata": {
                    "latency_ms":    latency_ms,
                    "tokens":        tokens_in + tokens_out,
                    "sentiment":     _sentiment(quality),
                    "quality_score": quality,
                    "query_preview": query[:60],
                },
            },
        })

    with LOG_PATH.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return len(records)
