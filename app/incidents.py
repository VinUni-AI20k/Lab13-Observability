from __future__ import annotations

STATE = {
    # Original incidents
    "rag_slow": False,
    "tool_fail": False,
    "cost_spike": False,
    
    # Banking-specific incidents (Member D)
    "account_lookup_slow": False,        # Account lookup service slow (2-3s delay)
    "credit_check_fail": False,          # Credit check service down
    "rate_limiter_triggered": False,     # Rate limiter kicks in (429 errors)
    "high_token_usage": False,           # Queries use 2x tokens (verbose responses)
    "core_banking_fail": False,          # Core banking system unavailable
    "random_10_percent_error": False,    # Giả lập lỗi 10%
}


def enable(name: str) -> None:
    if name not in STATE:
        raise KeyError(f"Unknown incident: {name}")
    STATE[name] = True



def disable(name: str) -> None:
    if name not in STATE:
        raise KeyError(f"Unknown incident: {name}")
    STATE[name] = False



def status() -> dict[str, bool]:
    return dict(STATE)
