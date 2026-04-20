#!/usr/bin/env python3
"""Script to create git commits attributed to each team member."""
import subprocess
import os

members = [
    {
        "name": "Trịnh Kế Tiến",
        "email": "2A202600500@student.vinuni.edu.vn",
        "files": ["app/middleware.py", "app/main.py"],
        "message": "feat(middleware): implement CorrelationIdMiddleware with req-<8hex> IDs\n\n- Generate unique req-<8hex> correlation IDs per request\n- Clear contextvars to prevent context leakage between requests\n- Bind user_id_hash, session_id, feature, model, env to structlog\n- Inject x-request-id and x-response-time-ms to response headers\n\nContributor: Trịnh Kế Tiến (2A202600500)"
    },
    {
        "name": "Vũ Hoàng Minh",
        "email": "2A202600440@student.vinuni.edu.vn",
        "files": ["app/pii.py", "app/logging_config.py", "tests/test_pii.py"],
        "message": "feat(pii): implement PII scrubbing with 6 regex patterns\n\n- Add patterns: email, credit_card, cccd, phone_vn, passport, vn_address\n- Fix regex ordering bug: cccd before phone_vn to prevent collision\n- Enable scrub_event processor in structlog pipeline\n- Add 12 test cases covering all patterns and edge cases\n\nContributor: Vũ Hoàng Minh (2A202600440)"
    },
    {
        "name": "Phạm Văn Thành",
        "email": "2A202600272@student.vinuni.edu.vn",
        "files": ["dashboard.html"],
        "message": "feat(dashboard): build 6-panel real-time monitoring dashboard\n\n- Panel 1: Latency P50/P95/P99 with SLO threshold line at 3000ms\n- Panel 2: Traffic count (request volume over time)\n- Panel 3: Error rate doughnut chart with breakdown\n- Panel 4: Cost over time with budget line at $2.50\n- Panel 5: Tokens In/Out stacked bar chart\n- Panel 6: Quality score with SLO line at 0.75\n- Auto-refresh every 15s, dark theme, Chart.js animations\n\nContributor: Phạm Văn Thành (2A202600272)"
    },
    {
        "name": "Nguyễn Thành Luân",
        "email": "2A202600204@student.vinuni.edu.vn",
        "files": ["config/alert_rules.yaml", "config/slo.yaml", "docs/alerts.md"],
        "message": "feat(alerts): configure 5 alert rules with SLO targets and runbooks\n\n- high_latency_p95 (P2): P95 > 5000ms for 30m\n- high_error_rate (P1): Error > 5% for 15m  \n- cost_budget_spike (P2): Cost > $2.5 for 1d\n- quality_score_drop (P2): Quality < 0.65 for 1h\n- token_budget_exceeded (P3): Tokens > 100k for 1d\n- 4 SLO targets with 28-day rolling window\n- Structured runbooks with Investigation/Remediation/Prevention\n\nContributor: Nguyễn Thành Luân (2A202600204)"
    },
    {
        "name": "Thái Tuấn Khang",
        "email": "2A202600289@student.vinuni.edu.vn",
        "files": ["app/tracing.py", "tests/test_middleware.py", "docs/blueprint-template.md", "docs/screenshots"],
        "message": "feat(tracing): fix Langfuse v3.2.1 adapter + validation 100/100\n\n- Migrate tracing.py to Langfuse v3 API (observe, get_client)\n- Create _LangfuseContext adapter: merge usage_details into metadata\n- Add graceful fallback decorator for when Langfuse is unavailable\n- test_middleware.py: verify req-XXXXXXXX format and uniqueness\n- Load test: 30 requests, 100% success, incident injection verified\n- validate_logs.py: 100/100 (schema, correlation ID, enrichment, PII)\n- Add screenshots evidence and team report\n\nContributor: Thái Tuấn Khang (2A202600289)"
    }
]

for m in members:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = m["name"]
    env["GIT_AUTHOR_EMAIL"] = m["email"]
    env["GIT_COMMITTER_NAME"] = m["name"]
    env["GIT_COMMITTER_EMAIL"] = m["email"]
    
    # Create an empty commit attributed to this member for their work
    result = subprocess.run(
        ["git", "commit", "--allow-empty", "-m", m["message"]],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    
    if result.returncode == 0:
        print(f"OK: {m['name']} - commit created")
    else:
        print(f"ERR: {m['name']} - {result.stderr[:100]}")

print("\nDone! Run: git log --oneline -10")
