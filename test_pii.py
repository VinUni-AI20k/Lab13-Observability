from app.pii import scrub_text

test_texts = [
    "Khách hàng Nguyễn Văn A, SĐT 0901234567, email nguyenvana@gmail.com",
    "Đây là CCCD của tôi: 012345678912",
    "Địa chỉ nhà tôi ở Số 10, Ngõ 5, Đường Trần Duy Hưng, Thành phố Hà Nội",
    "Passport của tôi là B1234567",
]

print("--- KIỂM TRA PII SCRUBBER ---")
for text in test_texts:
    print(f"GỐC : {text}")
    print(f"SẠCH: {scrub_text(text)}")
    print("-" * 30)
