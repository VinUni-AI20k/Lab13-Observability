"""
Mock responses for fallback mode — realistic tech support answers.
Organized by question pattern for smart matching.
"""
from __future__ import annotations

import random


MOCK_RESPONSES: dict[str, list[str]] = {
    "login": [
        "[TYPE: BUG] Lỗi đăng nhập thường do cookie hết hạn. Xóa cookie trình duyệt và thử lại. Nếu vẫn không được, reset mật khẩu qua link 'Quên mật khẩu'.",
        "[TYPE: QUESTION] Kiểm tra xem bạn nhập đúng email/username chưa. Tài khoản phân biệt chữ hoa/thường.",
        "[TYPE: BUG] Nếu bị khóa sau 5 lần nhập sai, chờ 15 phút rồi thử lại.",
    ],
    "config": [
        "[TYPE: QUESTION] Cấu hình server: Settings > Server Config, nhập IP và port (mặc định 8080).",
        "[TYPE: BUG] Nếu server không kết nối, kiểm tra firewall và đảm bảo port không bị chặn.",
        "[TYPE: QUESTION] Cần cấu hình SSL? Tải chứng chỉ từ trang support.",
    ],
    "pricing": [
        "[TYPE: QUESTION] Gói Starter: $9.99/tháng · Pro: $19.99/tháng · Enterprise: liên hệ sales.",
        "[TYPE: QUESTION] Có trial miễn phí 14 ngày cho tất cả gói. Không cần thẻ tín dụng.",
        "[TYPE: FEATURE_REQUEST] Nhiều khách hàng muốn thanh toán hàng năm được giảm 20%.",
    ],
    "password": [
        "[TYPE: BUG] Không nhận email reset: kiểm tra thư mục Spam. Nếu không có, liên hệ support.",
        "[TYPE: QUESTION] Mật khẩu phải ≥8 ký tự, chứa chữ hoa/thường/số.",
        "[TYPE: FEATURE_REQUEST] Nên hỗ trợ đăng nhập qua Google/GitHub.",
    ],
    "performance": [
        "[TYPE: QUESTION] Tốc độ bình thường: <500ms response time. Nếu chậm, kiểm tra kết nối mạng.",
        "[TYPE: BUG] Nếu thấy lag, thử clear cache và disable extension trình duyệt.",
        "[TYPE: FEATURE_REQUEST] Người dùng muốn có offline mode.",
    ],
    "billing": [
        "[TYPE: QUESTION] Hoá đơn gửi qua email. Nếu không nhận, kiểm tra Spam folder.",
        "[TYPE: QUESTION] Có thể hủy subscription bất kỳ lúc nào, không mất phí.",
        "[TYPE: BUG] Nếu bị charge lại, liên hệ billing@company.com ngay.",
    ],
    "features": [
        "[TYPE: QUESTION] Tính năng 2FA: Settings > Security > Enable 2FA via Authenticator app.",
        "[TYPE: QUESTION] Export dữ liệu: Tools > Export as CSV/JSON.",
        "[TYPE: FEATURE_REQUEST] Người dùng muốn API public để tích hợp với tool khác.",
    ],
    "default": [
        "[TYPE: QUESTION] Có thể giúp gì? Tôi là chuyên gia hỗ trợ kỹ thuật với kiến thức sâu về hệ thống.",
        "[TYPE: QUESTION] Bạn có thể mô tả vấn đề chi tiết hơn một chút không?",
        "[TYPE: QUESTION] Liên hệ support@company.com nếu cần hỗ trợ nhanh.",
    ],
}


def get_mock_response(question: str) -> tuple[str, int, int, str]:
    """
    Get realistic mock response based on question pattern.
    Returns (response_text, input_tokens, output_tokens, issue_type).
    """
    q_lower = question.lower()

    # Keyword matching — priority order
    category = "default"
    for keyword in ["đăng nhập", "login", "password", "quên mật", "không thể", "fail", "error"]:
        if keyword in q_lower:
            if "mật khẩu" in q_lower or "password" in q_lower:
                category = "password"
            else:
                category = "login"
            break

    if category == "default":
        for keyword in ["config", "cấu hình", "setting", "setup", "server"]:
            if keyword in q_lower:
                category = "config"
                break

    if category == "default":
        for keyword in ["giá", "price", "cost", "subscription", "gói", "plan", "billing", "charge"]:
            if keyword in q_lower:
                category = "pricing" if "billing" not in q_lower else "billing"
                break

    if category == "default":
        for keyword in ["nhanh", "chậm", "lag", "performance", "tốc độ", "slow"]:
            if keyword in q_lower:
                category = "performance"
                break

    if category == "default":
        for keyword in ["tính năng", "feature", "export", "api", "security", "2fa"]:
            if keyword in q_lower:
                category = "features"
                break

    responses = MOCK_RESPONSES.get(category, MOCK_RESPONSES["default"])
    response = random.choice(responses)

    # Extract issue_type from [TYPE: ...] prefix
    import re
    m = re.search(r"\[TYPE:\s*(BUG|FEATURE_REQUEST|QUESTION)\]", response)
    issue_type = m.group(1) if m else "UNKNOWN"

    # Realistic token estimation (4 chars ≈ 1 token)
    input_tokens = max(20, len(question) // 4)
    output_tokens = max(80, len(response) // 4)

    return response, input_tokens, output_tokens, issue_type
