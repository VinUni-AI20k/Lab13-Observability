from __future__ import annotations

from pathlib import Path


DASHBOARD_PATH = Path(__file__).with_name("dashboard.html")


def render_dashboard_html() -> str:
    return DASHBOARD_PATH.read_text(encoding="utf-8")
