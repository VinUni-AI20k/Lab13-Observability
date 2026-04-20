from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_vietnamese_phone_and_credit_card() -> None:
    out = scrub_text("Call 090 123 4567 and do not store card 4111 1111 1111 1111")
    assert "090 123 4567" not in out
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport_number() -> None:
    out = scrub_text("Passport C1234567 should not appear in logs")
    assert "C1234567" not in out
    assert "REDACTED_PASSPORT" in out
