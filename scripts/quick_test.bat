@echo off
REM Quick test script for Member D
REM Test basic functionality

echo ==========================================
echo MEMBER D: Quick Test
echo ==========================================
echo.

REM Test 1: Check if app is running
echo [Test 1] Checking if app is running...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] App is running
) else (
    echo [FAIL] App is not running
    echo Please start: uvicorn app.main:app --reload
    exit /b 1
)
echo.

REM Test 2: Run simple load test
echo [Test 2] Running simple load test (1 request)...
python scripts/load_test.py --concurrency 1
if %errorlevel% equ 0 (
    echo [PASS] Load test works
) else (
    echo [FAIL] Load test failed
    exit /b 1
)
echo.

REM Test 3: Check metrics endpoint
echo [Test 3] Checking metrics endpoint...
curl -s http://127.0.0.1:8000/metrics >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Metrics endpoint works
) else (
    echo [FAIL] Metrics endpoint failed
    exit /b 1
)
echo.

REM Test 4: Check incidents endpoint
echo [Test 4] Checking incidents endpoint...
curl -s http://127.0.0.1:8000/incidents/status >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Incidents endpoint works
) else (
    echo [FAIL] Incidents endpoint failed
    exit /b 1
)
echo.

REM Test 5: Enable incident
echo [Test 5] Testing incident enable...
curl -s -X POST http://127.0.0.1:8000/incidents/account_lookup_slow/enable >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Incident enable works
) else (
    echo [FAIL] Incident enable failed
    exit /b 1
)
echo.

REM Test 6: Disable incident
echo [Test 6] Testing incident disable...
curl -s -X POST http://127.0.0.1:8000/incidents/account_lookup_slow/disable >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Incident disable works
) else (
    echo [FAIL] Incident disable failed
    exit /b 1
)
echo.

echo ==========================================
echo [SUCCESS] All tests passed!
echo ==========================================
echo.
echo You are ready to:
echo 1. Run full demo: scripts\demo_member_d.bat
echo 2. Run load tests: python scripts/load_test.py --concurrency 5
echo 3. Check report: docs\load_test_report.md
echo.
pause
