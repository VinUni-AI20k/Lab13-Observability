"""
Smart Mock LLM engine.
Returns realistic tech-support responses based on keyword matching.
Simulates realistic thinking delay proportional to response length.
"""
from __future__ import annotations

import random
import time

from .incidents import STATE

# ── Response bank ──────────────────────────────────────────────────────────────
# Each entry: keywords (any match) → issue_type + list of reply variants
_BANK: list[dict] = [
    {
        "keywords": ["đăng nhập", "login", "invalid credential", "mật khẩu", "password",
                     "authentication", "xác thực", "tài khoản", "account"],
        "issue_type": "BUG",
        "replies": [
            (
                "Lỗi 'Invalid credentials' thường do 3 nguyên nhân:\n"
                "1. Mật khẩu đã bị thay đổi — thử đặt lại về mặc định (admin/admin hoặc admin/12345).\n"
                "2. Tài khoản bị khóa sau nhiều lần đăng nhập sai — đợi 5 phút rồi thử lại.\n"
                "3. Firmware cũ có lỗi xác thực — nâng cấp lên v3.2+.\n\n"
                "Nếu quên mật khẩu hoàn toàn: giữ nút **Reset** trên thân máy 10 giây để khôi phục "
                "cài đặt gốc (lưu ý: toàn bộ cấu hình sẽ bị xóa).\n"
                "Anh/chị đang đăng nhập qua trình duyệt hay ứng dụng mobile?"
            ),
            (
                "Để xử lý lỗi đăng nhập:\n"
                "• Username mặc định: **admin** (phân biệt chữ hoa/thường)\n"
                "• Password mặc định: **admin** hoặc **12345** tùy model\n"
                "• Nếu đã đổi mật khẩu và quên: Reset nhà máy (giữ nút Reset 10s)\n"
                "• Kiểm tra IP camera có đúng không: mở CMD → `ping <IP camera>`\n\n"
                "Cho tôi biết model camera để hỗ trợ chính xác hơn."
            ),
        ],
    },
    {
        "keywords": ["wifi", "kết nối", "mất kết nối", "disconnect", "offline",
                     "connection lost", "không kết nối", "mạng"],
        "issue_type": "BUG",
        "replies": [
            (
                "Để khắc phục mất kết nối WiFi:\n"
                "1. **Kiểm tra khoảng cách**: camera nên trong bán kính 10m so với router.\n"
                "2. **Băng tần**: thiết bị chỉ hỗ trợ **2.4GHz**, không hỗ trợ 5GHz.\n"
                "3. **Đổi kênh WiFi** trên router sang kênh 1, 6 hoặc 11 để tránh nhiễu.\n"
                "4. **Kiểm tra mật khẩu WiFi** không có ký tự đặc biệt (một số model không hỗ trợ).\n"
                "5. Nếu vẫn lỗi: reset camera, cấu hình lại WiFi từ ứng dụng iCSee.\n\n"
                "Anh/chị dùng router băng tần đơn hay kép (dual-band)?"
            ),
        ],
    },
    {
        "keywords": ["firmware", "update", "nâng cấp", "phiên bản", "version", "cập nhật"],
        "issue_type": "QUESTION",
        "replies": [
            (
                "Hướng dẫn nâng cấp firmware:\n"
                "1. Tải file firmware mới nhất tại trang hỗ trợ (ghi rõ model trên tem dán).\n"
                "2. Vào **Cài đặt → Hệ thống → Cập nhật firmware**.\n"
                "3. Upload file `.bin` và đợi 3-5 phút — **tuyệt đối không tắt nguồn**.\n"
                "4. Camera tự khởi động lại sau khi hoàn thành.\n\n"
                "**Firmware v3.2+** hỗ trợ: AI detection, dual-channel RTSP, H.265+.\n"
                "Anh/chị đang dùng firmware phiên bản nào? (Cài đặt → Thông tin hệ thống)"
            ),
        ],
    },
    {
        "keywords": ["giá", "price", "bao nhiêu", "chi phí", "cost", "mua", "buy",
                     "báo giá", "quote", "tiền"],
        "issue_type": "QUESTION",
        "replies": [
            (
                "**Bảng giá tham khảo** (đã bao gồm VAT):\n\n"
                "| Sản phẩm | Giá |\n"
                "|---|---|\n"
                "| Camera IP 2MP trong nhà | 800k – 1.2 triệu |\n"
                "| Camera IP 5MP AI ngoài trời | 2 – 4 triệu |\n"
                "| Camera PTZ 4K zoom 30x | 6 – 12 triệu |\n"
                "| NVR 8 kênh H.265 | 2.5 – 5 triệu |\n"
                "| NVR 16 kênh H.265 | 5 – 10 triệu |\n"
                "| Switch PoE 8 cổng | 1.5 – 3 triệu |\n\n"
                "Liên hệ **sales@ipstore.vn** để nhận báo giá sỉ cho đơn từ 10 thiết bị trở lên."
            ),
        ],
    },
    {
        "keywords": ["server", "cấu hình", "config", "thiết lập", "setup", "cài đặt",
                     "ip address", "địa chỉ ip", "lan"],
        "issue_type": "QUESTION",
        "replies": [
            (
                "Hướng dẫn cấu hình NVR/server:\n"
                "1. Kết nối NVR vào mạng LAN qua cáp **CAT6**.\n"
                "2. Truy cập giao diện web tại IP mặc định **192.168.1.64** (hoặc dùng tool tìm IP).\n"
                "3. Vào **Cài đặt → Mạng** → đặt IP tĩnh phù hợp dải mạng của anh/chị.\n"
                "4. Thêm camera: **Cài đặt → Camera → Tự động tìm kiếm** (cùng mạng LAN).\n"
                "5. Mở cổng trên router nếu cần xem từ xa: **TCP 8000, 8001 / UDP 37008**.\n\n"
                "Cần hỗ trợ từ xa? Cho tôi biết địa chỉ IP public để hỗ trợ qua TeamViewer."
            ),
        ],
    },
    {
        "keywords": ["nvr", "dvr", "đầu ghi", "recording", "ghi hình", "lưu trữ",
                     "hdd", "ổ cứng", "storage"],
        "issue_type": "QUESTION",
        "replies": [
            (
                "Hệ thống NVR của chúng tôi hỗ trợ:\n"
                "• Tối đa **16 kênh** camera IP đồng thời.\n"
                "• Định dạng ghi: **H.265+** (tiết kiệm 50% dung lượng so với H.264).\n"
                "• HDD tương thích: Seagate SkyHawk hoặc WD Purple, tối đa **8TB/ổ**.\n"
                "• Ghi liên tục 24/7, theo lịch, hoặc khi phát hiện chuyển động.\n\n"
                "**Tính toán dung lượng**: 1 camera 2MP, ghi 24/7, H.265 ≈ **20GB/ngày**.\n"
                "Anh/chị cần lưu bao nhiêu ngày để tôi tư vấn số ổ HDD phù hợp?"
            ),
        ],
    },
    {
        "keywords": ["poe", "switch", "nguồn", "không lên nguồn", "not powering",
                     "power supply", "cấp nguồn"],
        "issue_type": "BUG",
        "replies": [
            (
                "Xử lý sự cố nguồn PoE:\n"
                "1. **Kiểm tra chuẩn PoE**: camera yêu cầu IEEE 802.3af (15.4W) hay 802.3at (30W)?\n"
                "2. **PoE budget**: tổng công suất switch có đủ không? (VD: 8 cổng × 15W = 120W)\n"
                "3. Thử cắm camera vào **cổng PoE khác** trên switch.\n"
                "4. Dùng **PoE tester** để kiểm tra cáp CAT6 (chập mạch, đứt lõi).\n"
                "5. Test camera bằng nguồn DC trực tiếp để loại trừ lỗi camera.\n\n"
                "Camera của anh/chị yêu cầu bao nhiêu watt? (thường ghi trên tem sản phẩm)"
            ),
        ],
    },
    {
        "keywords": ["mobile", "app", "điện thoại", "iphone", "android",
                     "xem từ xa", "remote view", "icsee", "ứng dụng"],
        "issue_type": "BUG",
        "replies": [
            (
                "Hướng dẫn xem camera từ xa qua điện thoại:\n"
                "1. Tải **iCSee** (iOS/Android) — miễn phí trên App Store/CH Play.\n"
                "2. Đăng ký tài khoản → Thêm thiết bị → Quét **mã QR** trên thân camera.\n"
                "3. Khi lần đầu cài đặt: điện thoại và camera phải cùng mạng WiFi.\n\n"
                "**Không xem được qua 4G/LTE?** Cần mở cổng trên router:\n"
                "• TCP: 8000, 8001, 80 | UDP: 37008\n"
                "• Hoặc dùng dịch vụ DDNS nếu IP nhà mạng thay đổi.\n\n"
                "Anh/chị đang dùng iOS hay Android? Báo lỗi cụ thể trên app là gì?"
            ),
        ],
    },
    {
        "keywords": ["bảo hành", "warranty", "sửa chữa", "repair", "hỏng",
                     "broken", "damaged"],
        "issue_type": "QUESTION",
        "replies": [
            (
                "**Chính sách bảo hành:**\n"
                "• Camera IP: **12 tháng** từ ngày mua.\n"
                "• NVR/DVR: **24 tháng**.\n"
                "• Switch PoE: **12 tháng**.\n\n"
                "**Quy trình bảo hành:**\n"
                "1. Mang thiết bị + hóa đơn đến cửa hàng, hoặc gửi bưu điện.\n"
                "2. Chi phí vận chuyển 2 chiều miễn phí trong thời hạn bảo hành.\n"
                "3. Thời gian xử lý: 3-7 ngày làm việc.\n\n"
                "**Không bảo hành:** hư hỏng do sét đánh, nước vào, tự ý tháo máy.\n"
                "Gửi ảnh chụp sản phẩm và hóa đơn về **warranty@ipstore.vn** để kiểm tra trước."
            ),
        ],
    },
    {
        "keywords": ["zoom", "ai", "nhận diện", "detection", "face recognition",
                     "biển số", "lpr", "tính năng mới", "feature request",
                     "muốn thêm", "đề xuất", "yêu cầu tính năng"],
        "issue_type": "FEATURE_REQUEST",
        "replies": [
            (
                "Cảm ơn anh/chị đã góp ý — yêu cầu này đã được ghi nhận!\n\n"
                "**Tính năng AI hiện có** trên dòng cao cấp:\n"
                "• Nhận diện khuôn mặt (Face Detection & Recognition)\n"
                "• Đọc biển số xe (LPR — License Plate Recognition)\n"
                "• Phân tích hành vi bất thường (Behavior Analytics)\n"
                "• Đếm người qua vùng (People Counting)\n"
                "• Zoom quang học 30x (dòng PTZ Pro)\n\n"
                "Yêu cầu của anh/chị đã được chuyển đến team sản phẩm. "
                "Chúng tôi sẽ thông báo khi tính năng có trong lộ trình phát hành tiếp theo."
            ),
        ],
    },
    {
        "keywords": ["cảnh báo", "alert", "thông báo", "notification", "email alert",
                     "sms", "push notification", "tin nhắn"],
        "issue_type": "FEATURE_REQUEST",
        "replies": [
            (
                "**Cảnh báo hiện có:**\n"
                "• Push notification qua app iCSee (khi phát hiện chuyển động)\n"
                "• Email alert — cấu hình SMTP tại: Cài đặt → Sự kiện → Email\n"
                "• Ghi âm thanh báo động khi có xâm nhập\n\n"
                "**SMS alert** đang trong lộ trình phát triển **Q3/2025**.\n"
                "Tôi đã ghi nhận yêu cầu của anh/chị. "
                "Đăng ký email để nhận thông báo khi tính năng ra mắt: update@ipstore.vn"
            ),
        ],
    },
    {
        "keywords": ["onvif", "rtsp", "protocol", "tích hợp", "integration",
                     "third party", "home assistant", "milestone", "blue iris"],
        "issue_type": "QUESTION",
        "replies": [
            (
                "Tích hợp ONVIF/RTSP:\n"
                "• Tất cả camera IP hỗ trợ **ONVIF Profile S & T**.\n"
                "• RTSP stream URL: `rtsp://<user>:<pass>@<IP>:554/stream1`\n"
                "• Substream (độ phân giải thấp): `rtsp://.../stream2`\n\n"
                "Test stream trước khi tích hợp:\n"
                "```\nvlc rtsp://admin:admin@192.168.1.100:554/stream1\n```\n\n"
                "Tương thích với: **Home Assistant, Milestone, Genetec, Blue Iris, Shinobi**.\n"
                "Anh/chị đang tích hợp với hệ thống nào? Tôi có thể hỗ trợ cấu hình chi tiết."
            ),
        ],
    },
    {
        "keywords": ["hồng ngoại", "night vision", "infrared", "ban đêm", "tối",
                     "mờ", "blurry", "không rõ"],
        "issue_type": "BUG",
        "replies": [
            (
                "Xử lý hình ảnh mờ/kém chất lượng ban đêm:\n"
                "1. **Vệ sinh lens**: dùng khăn mềm lau sạch bụi trên kính.\n"
                "2. **IR Cut filter**: vào Cài đặt → Hình ảnh → Chế độ đêm → Auto.\n"
                "3. **Phản xạ IR**: đảm bảo không có vật cản trong vùng phát tia hồng ngoại.\n"
                "4. **Đọng sương**: dùng chất chống đọng sương hoặc lắp che mưa.\n"
                "5. **Khoảng cách IR**: đèn hồng ngoại có giới hạn (thường 20-30m).\n\n"
                "Gửi ảnh chụp màn hình để tôi chẩn đoán chính xác hơn."
            ),
        ],
    },
]

_FALLBACK = {
    "issue_type": "QUESTION",
    "replies": [
        (
            "Cảm ơn anh/chị đã liên hệ hỗ trợ kỹ thuật!\n\n"
            "Để hỗ trợ chính xác, vui lòng cung cấp thêm:\n"
            "• **Model sản phẩm** (tên/mã in trên tem dán)\n"
            "• **Mô tả vấn đề** cụ thể đang gặp\n"
            "• **Từ khi nào** bắt đầu xuất hiện lỗi?\n"
            "• **Đã thử** các bước khắc phục nào chưa?\n\n"
            "Hotline hỗ trợ kỹ thuật: **1800-xxxx** (8:00 – 20:00, T2–T7)\n"
            "Email: **support@ipstore.vn**"
        ),
        (
            "Xin chào! Tôi là AI Tech Support của cửa hàng thiết bị IP.\n\n"
            "Tôi có thể hỗ trợ về:\n"
            "🔧 Lỗi kỹ thuật — kết nối, đăng nhập, cấu hình\n"
            "📦 Thông tin sản phẩm — tính năng, tương thích\n"
            "💰 Báo giá — camera, NVR, switch PoE\n"
            "🔁 Bảo hành & sửa chữa\n\n"
            "Anh/chị cần hỗ trợ vấn đề gì?"
        ),
    ],
}


def _user_text(prompt: str) -> str:
    """Extract only the user-question portion of the prompt for keyword matching."""
    # Prompt format: "Câu hỏi của khách hàng: {msg}\n\nTài liệu tham khảo:\n..."
    for sep in ["\n\nTài liệu", "\n\nNgữ cảnh", "\n\nContext"]:
        if sep in prompt:
            return prompt.split(sep)[0].lower()
    return prompt.split("\n\n")[0].lower()


def generate(prompt: str) -> "LLMResponse":  # noqa: F821 - forward ref
    from .openai_llm import LLMResponse, LLMUsage  # local import avoids circular

    # Match only against the user question, not retrieved docs
    lower = _user_text(prompt)

    # Find best matching category
    matched = None
    for entry in _BANK:
        if any(kw in lower for kw in entry["keywords"]):
            matched = entry
            break

    bucket = matched if matched else _FALLBACK
    reply  = random.choice(bucket["replies"])

    # Simulate thinking time: faster for short answers, slower for long ones
    base_delay = 0.25
    length_factor = len(reply) / 1800  # ~0.2-0.7 extra seconds
    if STATE["cost_spike"]:
        length_factor *= 3  # much slower when cost spike active
    time.sleep(base_delay + length_factor)

    input_tokens  = max(20, len(prompt) // 4)
    output_tokens = max(30, len(reply) // 4)
    if STATE["cost_spike"]:
        output_tokens *= 4

    return LLMResponse(
        text=reply,
        usage=LLMUsage(input_tokens=input_tokens, output_tokens=output_tokens),
        model="mock-smart",
        issue_type=bucket["issue_type"],
    )
