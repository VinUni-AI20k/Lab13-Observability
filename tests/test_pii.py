from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out

def test_scrub_phone() -> None:
    out = scrub_text("My phone is 0901234567")
    assert "0901234567" not in out
    assert "REDACTED_PHONE_VN" in out

def test_scrub_passport() -> None:
    out = scrub_text("Passport: B1234567")
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT" in out

def test_scrub_address() -> None:
    out = scrub_text("I live in Hà Nội today.")
    assert "Hà Nội" not in out
    assert "REDACTED_ADDRESS_VN" in out

def test_scrub_deep_defense() -> None:
    out = scrub_text("Bé Nguyễn Văn A nộp học phí 10.000.000 VND vào stk 123456789. Mã học sinh VINS-2023 truy cập từ 192.168.1.1")
    assert "Nguyễn Văn A" not in out
    assert "10.000.000" not in out
    assert "123456789" not in out
    assert "VINS-2023" not in out
    assert "192.168.1.1" not in out
    assert "REDACTED_STUDENT_NAME" in out
    assert "REDACTED_CURRENCY_VN" in out
    assert "REDACTED_BANK_ACCOUNT" in out
    assert "REDACTED_STUDENT_ID" in out
    assert "REDACTED_IP_ADDRESS" in out
