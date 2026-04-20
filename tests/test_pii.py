from app.pii import scrub_text, hash_user_id, summarize_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_phone_vn() -> None:
    out = scrub_text("Call me at 0987654321 please")
    assert "0987654321" not in out
    assert "REDACTED_PHONE_VN" in out


def test_scrub_phone_vn_intl() -> None:
    out = scrub_text("My number is +84 987 654 321")
    assert "987" not in out
    assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd() -> None:
    out = scrub_text("CCCD cua toi la 012345678901")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card() -> None:
    out = scrub_text("Card: 4111 1111 1111 1111")
    assert "4111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_credit_card_dashed() -> None:
    out = scrub_text("Card: 4111-1111-1111-1111")
    assert "4111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport() -> None:
    out = scrub_text("Passport number B12345678")
    assert "B12345678" not in out
    assert "REDACTED_PASSPORT" in out


def test_scrub_multiple_pii() -> None:
    text = "Email: admin@test.com, Phone: 0912345678, Card: 4111111111111111"
    out = scrub_text(text)
    assert "admin@" not in out
    assert "0912345678" not in out
    assert "4111" not in out


def test_scrub_clean_text() -> None:
    text = "This is a normal question about observability"
    out = scrub_text(text)
    assert out == text


def test_hash_user_id() -> None:
    h = hash_user_id("u01")
    assert len(h) == 12
    assert h == hash_user_id("u01")  # deterministic
    assert h != hash_user_id("u02")  # different for different users


def test_summarize_text_truncation() -> None:
    long_text = "A" * 200
    out = summarize_text(long_text, max_len=80)
    assert len(out) <= 83  # 80 + "..."
    assert out.endswith("...")


def test_summarize_scrubs_pii() -> None:
    out = summarize_text("Contact student@vinuni.edu.vn for details")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out
