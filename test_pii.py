#!/usr/bin/env python3
"""Quick test to verify PII scrubbing works correctly"""

from app.pii import scrub_text

test_cases = [
    ("My email is john.doe@example.com", "My email is [REDACTED_EMAIL]"),
    ("Call me at 0901234567", "Call me at [REDACTED_PHONE_VN]"),
    ("My CCCD is 123456789012", "My CCCD is [REDACTED_CCCD]"),
    ("Credit card 4111 1111 1111 1111", "Credit card [REDACTED_CREDIT_CARD]"),
    ("Passport AB1234567", "Passport [REDACTED_PASSPORT]"),
    ("I live in Ha Noi, quan Hoan Kiem", "I live in [REDACTED_VIETNAMESE_ADDRESS]"),
]

print("Testing PII scrubbing:")
for input_text, expected in test_cases:
    result = scrub_text(input_text)
    status = "PASS" if result == expected else "FAIL"
    print(f"{status}: {input_text}")
    print(f"  -> {result}")
    print()
