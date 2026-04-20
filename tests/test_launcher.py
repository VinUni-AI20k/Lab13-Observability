from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "run-dashboard.bat"


def test_dashboard_launcher_exists_and_targets_dashboard_route() -> None:
    content = LAUNCHER.read_text(encoding="utf-8")

    assert ".venv\\Scripts\\python.exe" in content
    assert "uvicorn app.main:app --reload --port" in content
    assert "/dashboard" in content
    assert "Working directory" in content
