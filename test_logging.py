import os
from structlog.contextvars import bind_contextvars, clear_contextvars
from app.logging_config import configure_logging, get_logger
from app.pii import hash_user_id

# 1. Khởi tạo cấu hình log
os.environ["LOG_PATH"] = "data/test_logs.jsonl"
configure_logging()
log = get_logger()

print("--- KIỂM TRA LOGGING CONFIG & CONTEXT ---")

# 2. Xóa context cũ (bắt chước Middleware khởi tạo)
clear_contextvars()

# 3. Gắn Data (Context) như cách Main.py làm
bind_contextvars(
    correlation_id="req-123",
    user_id_hash=hash_user_id("user_test_01"),
    env="local_testing"
)

# 4. Ghi log thử hàng loạt các tình huống Ngân hàng
print("\n[TÌNH HUỐNG 1] Khách hàng rớt thẻ tín dụng:")
log.info(
    "khóa_thẻ_khẩn_cấp",
    service="banking_api",
    payload={"message": "Khóa ngay cho tôi thẻ credit 4111 2222 3333 4444. Số CVV mặt sau là 123"}
)

print("\n[TÌNH HUỐNG 2] Khách hàng mở sổ tiết kiệm với CCCD/Passport:")
log.info(
    "mở_sổ_tiết_kiệm",
    service="banking_api",
    payload={"message": "Passport của em là B1234567 tròn, CCCD của vợ em là 012345678912."}
)

print("\n[TÌNH HUỐNG 3] Yêu cầu chuyển phát thẻ về nhà:")
log.info(
    "chuyển_phát_thẻ",
    service="banking_api",
    payload={"message": "Ship thẻ cho mình về Số 10, Ngõ 5, Đường Trần Duy Hưng, Thành phố Hà Nội. Gọi vào sđt 0901234567 trước khi đến nhé."}
)

print("\n--- ĐỌC KẾT QUẢ TỪ FILE LOG ---")
# Đọc file ra xem thử 3 dòng cuối
with open("data/logs.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines[-3:]:
        import json
        data = json.loads(line)
        print(f"Sự kiện: {data.get('event')}")
        print(f"Payload an toàn: {data.get('payload')}\n")
