from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_phone_vn() -> None:
    out = scrub_text("Gọi cho tôi số 0912 345 678 nhé")
    assert "0912" not in out
    assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd() -> None:
    out = scrub_text("CCCD của tôi là 001099012345")
    assert "001099012345" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card() -> None:
    out = scrub_text("Thẻ tín dụng: 4111-1111-1111-1111")
    assert "4111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport_vn() -> None:
    out = scrub_text("Hộ chiếu số B1234567 cấp ngày 01/01/2020")
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT_VN" in out


def test_scrub_passport_vn_8digits() -> None:
    out = scrub_text("Passport: C12345678")
    assert "C12345678" not in out
    assert "REDACTED_PASSPORT_VN" in out


def test_scrub_address_vn() -> None:
    out = scrub_text("Tôi sống ở đường Nguyễn Huệ quận 1 TP.HCM")
    assert "Nguyễn Huệ" not in out
    assert "REDACTED_ADDRESS_VN" in out


def test_scrub_address_vn_phuong() -> None:
    out = scrub_text("Địa chỉ: 10 phường Bến Nghé")
    assert "Bến Nghé" not in out
    assert "REDACTED_ADDRESS_VN" in out


def test_no_false_positive_short_number() -> None:
    out = scrub_text("Tôi có 5 con mèo và 123 cuốn sách")
    assert out == "Tôi có 5 con mèo và 123 cuốn sách"
