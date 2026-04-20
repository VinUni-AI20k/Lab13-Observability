@echo off
setlocal

REM Working directory: switch to the repo root so relative imports and files resolve correctly.
cd /d "%~dp0"

set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  if exist "%CD%\..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%CD%\..\.venv\Scripts\python.exe"
  ) else (
    echo Local virtual environment not found at ".venv\Scripts\python.exe" or "..\.venv\Scripts\python.exe".
    echo Falling back to the Python executable available on PATH.
    set "PYTHON_EXE=python"
  )
)

set "PORT="
for %%P in (8001 8002 8003 8010 8080) do (
  netstat -ano | findstr /R /C:":%%P .*LISTENING" >nul
  if errorlevel 1 (
    set "PORT=%%P"
    goto :port_selected
  )
)

echo Could not find an available port in the default launcher list.
echo Try running: %PYTHON_EXE% -m uvicorn app.main:app --reload --port 8050
pause
exit /b 1

:port_selected
echo Starting Day 13 Observability Lab on http://127.0.0.1:%PORT%/dashboard
start "Day 13 Observability Lab" "%PYTHON_EXE%" -m uvicorn app.main:app --reload --port %PORT%
start "" powershell -NoProfile -WindowStyle Hidden -Command "for ($i = 0; $i -lt 30; $i++) { try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:%PORT%/dashboard' -TimeoutSec 1 -UseBasicParsing; if ($response.StatusCode -eq 200) { Start-Process 'http://127.0.0.1:%PORT%/dashboard'; break } } catch { Start-Sleep -Seconds 1 } }"
exit /b 0
