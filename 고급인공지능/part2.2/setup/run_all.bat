@echo off
chcp 65001 > nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

:: ── 8000 포트 사용 중인 PID 감지 ──────────────────────────
set "PID="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING 2^>nul') do set PID=%%a

if not "%PID%"=="" goto TURN_OFF

:: ===========================================================
:TURN_ON
:: ===========================================================
echo.
echo ========================================================
echo  AI 뉴스 큐레이터 — 전체 시스템 시작
echo ========================================================
echo.

:: dist 없으면 경고만 하고 계속 진행
if not exist "news-app\dist\index.html" (
    echo [경고] news-app\dist 가 없습니다.
    echo  setup.bat 을 먼저 실행하거나, npm run build 를 해주세요.
    echo  5173 포트(Vite 개발 서버^)로 접속하려면 별도로 npm run dev 를 켜주세요.
    echo.
)

start "News_Engine"    cmd /k "python main_engine.py"
start "API_Server"     cmd /k "uvicorn api_server:app --reload --host 0.0.0.0 --port 8000"
start "Floating_Bot"   cmd /k "python floating_bot.py"

echo 서버 초기화 대기 중... (5초)
timeout /t 5 > nul

:: dist 있으면 8000, 없으면 5173 시도
if exist "news-app\dist\index.html" (
    echo 브라우저를 엽니다: http://localhost:8000
    start http://localhost:8000
) else (
    echo 브라우저를 엽니다: http://localhost:5173  ^(Vite 개발 서버^)
    start http://localhost:5173
)

echo.
echo ========================================================
echo  모든 시스템이 정상 가동됐습니다.
echo  종료하려면 run_all.bat 을 다시 실행하세요.
echo ========================================================
goto :EOF

:: ===========================================================
:TURN_OFF
:: ===========================================================
echo.
echo ========================================================
echo  AI 뉴스 큐레이터 — 전체 시스템 종료
echo ========================================================
echo.

echo [1/3] API 서버 종료 중... (PID: %PID%)
taskkill /F /PID %PID% > nul 2>&1

echo [2/3] 뉴스 엔진 / 플로팅 봇 종료 중...
taskkill /F /T /FI "WINDOWTITLE eq News_Engine*"  > nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq API_Server*"   > nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq Floating_Bot*" > nul 2>&1

echo [3/3] 남은 Python 프로세스 정리 중...
wmic process where "name='python.exe' and commandline like '%%main_engine.py%%'"   delete > nul 2>&1
wmic process where "name='python.exe' and commandline like '%%floating_bot.py%%'"  delete > nul 2>&1
wmic process where "name='python.exe' and commandline like '%%api_server%%'"       delete > nul 2>&1

echo.
echo 모든 프로세스가 정리됐습니다.
pause
goto :EOF