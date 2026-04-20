@echo off
REM Demo script for Member D: Load Test + Incident Injection
REM Banking Chatbot CSKH

echo ==========================================
echo MEMBER D DEMO: Load Test + Incident Injection
echo Banking Chatbot CSKH
echo ==========================================
echo.

REM Check if app is running
echo [1/10] Checking if app is running...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] App is running
) else (
    echo [ERROR] App is not running. Please start: uvicorn app.main:app --reload
    exit /b 1
)
echo.

REM Show current metrics
echo [2/10] Current metrics (before load test):
curl -s http://127.0.0.1:8000/metrics
echo.
echo.

REM Run normal load test
echo [3/10] Running normal load test (5 concurrent)...
python scripts/load_test.py --concurrency 5
echo.

REM Show metrics after normal load
echo [4/10] Metrics after normal load:
curl -s http://127.0.0.1:8000/metrics
echo.
echo.

REM Enable account_lookup_slow incident
echo [5/10] Enabling account_lookup_slow incident...
curl -s -X POST http://127.0.0.1:8000/incidents/account_lookup_slow/enable
echo.
echo.

REM Run load test with incident
echo [6/10] Running load test with account_lookup_slow incident (5 concurrent)...
echo [WARNING] Expect latency spike!
python scripts/load_test.py --concurrency 5
echo.

REM Show metrics with incident
echo [7/10] Metrics with incident (notice P95 latency spike):
curl -s http://127.0.0.1:8000/metrics
echo.
echo.

REM Disable incident
echo [8/10] Disabling account_lookup_slow incident...
curl -s -X POST http://127.0.0.1:8000/incidents/account_lookup_slow/disable
echo.
echo.

REM Run load test after recovery
echo [9/10] Running load test after recovery (5 concurrent)...
echo [OK] Expect latency to return to normal
python scripts/load_test.py --concurrency 5
echo.

REM Show final metrics
echo [10/10] Final metrics (after recovery):
curl -s http://127.0.0.1:8000/metrics
echo.
echo.

echo ==========================================
echo [OK] DEMO COMPLETE
echo ==========================================
echo.
echo Summary:
echo - Normal load: 5 concurrent, latency ~1800ms P95
echo - With incident: 5 concurrent, latency ~2800ms P95 (+55%%)
echo - After recovery: 5 concurrent, latency ~1800ms P95
echo.
echo Next steps:
echo 1. Try other incidents: credit_check_fail, high_token_usage
echo 2. Run peak load test: python scripts/load_test.py --concurrency 20
echo 3. Run stress test: python scripts/load_test.py --concurrency 50
echo 4. Check load test report: docs/load_test_report.md
echo.
pause
