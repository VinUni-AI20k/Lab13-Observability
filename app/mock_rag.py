from __future__ import annotations

import time

from .incidents import STATE

CORPUS: dict[str, list[str]] = {
    # ── General store policies ──
    "refund":   ["Hoàn tiền trong vòng 7 ngày kể từ ngày mua kèm hóa đơn."],
    "policy":   ["Không lưu thông tin cá nhân (PII) vào log. Chỉ dùng bản tóm tắt đã ẩn danh."],
    "warranty": ["Bảo hành 12 tháng cho camera IP, 24 tháng cho NVR/DVR."],

    # ── Product knowledge ──
    "camera":   [
        "Camera IP hỗ trợ chuẩn ONVIF. Kết nối qua switch PoE, cổng mặc định 37008.",
        "Dòng camera 4K PTZ hỗ trợ zoom quang học 30x, tích hợp AI nhận diện biển số.",
    ],
    "wifi":     [
        "Đảm bảo camera trong bán kính 10m so với router. Kiểm tra cài đặt WPA2/WPA3.",
        "Nếu mất kết nối WiFi liên tục, reset camera về mặc định và cấu hình lại SSID.",
    ],
    "firmware": [
        "Tải firmware mới nhất tại trang hỗ trợ sản phẩm. Cần reset nhà máy sau khi nâng cấp.",
        "Firmware v3.2+ hỗ trợ tính năng AI detection và RTSP stream dual-channel.",
    ],
    "nvr":      [
        "NVR hỗ trợ tối đa 16 kênh. Dùng cáp CAT6 để đạt hiệu năng tốt nhất.",
        "Định dạng lưu trữ: H.265+ tiết kiệm 50% dung lượng so với H.264.",
    ],
    "price":    [
        "Camera IP phổ thông: 800k–2 triệu. Dòng 4K AI: 3–8 triệu. Liên hệ sales cho báo giá sỉ.",
    ],
    "poe":      [
        "Switch PoE 8 cổng cấp nguồn tối đa 15.4W/cổng (IEEE 802.3af) hoặc 30W (802.3at).",
    ],
    "onvif":    [
        "Giao thức ONVIF cho phép camera từ nhiều hãng khác nhau tích hợp vào cùng một NVR.",
    ],

    # ── Observability context ──
    "monitoring": ["Metrics phát hiện sự cố, traces định vị nguồn gốc, logs giải thích nguyên nhân gốc rễ."],
}


def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)

    lowered = message.lower()
    results: list[str] = []
    for keyword, docs in CORPUS.items():
        if keyword in lowered:
            results.extend(docs)
    return results if results else ["Không có tài liệu khớp. Sử dụng kiến thức chung để trả lời."]
