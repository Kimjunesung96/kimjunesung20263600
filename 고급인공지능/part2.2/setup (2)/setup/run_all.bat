@echo off
chcp 65001 > nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8 

:: 8000번 포트 감지
set "PID="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do set PID=%%a

if not "%PID%"=="" goto TURN_OFF

:TURN_ON
echo [AI 뉴스 큐레이터 시스템 전체 가동 시작 - NPM 없는 배포 모드]
start "News_Engine" cmd /k "python main_engine.py"
start "API_Server" cmd /k "uvicorn api_server:app --reload"
start "Floating_Bot" cmd /k "python floating_bot.py"

echo 서버 켜는 중... 잠시만 기다려주세요 (3초 대기)
timeout /t 3 > nul

:: 💡 npm 없이 FastAPI(8000)가 서빙하는 빵(dist) 화면으로 자동 접속!
start http://localhost:8000

echo 모든 시스템이 켜졌습니다.
goto :EOF

:TURN_OFF
echo [시스템 종료 중...]
taskkill /F /PID %PID% > NUL 2>&1
taskkill /F /T /FI "WINDOWTITLE eq News_Engine*" > NUL 2>&1
taskkill /F /T /FI "WINDOWTITLE eq API_Server*" > NUL 2>&1
taskkill /F /T /FI "WINDOWTITLE eq Floating_Bot*" > NUL 2>&1
wmic process where "name='python.exe' and commandline like '%%main_engine.py%%'" delete > NUL 2>&1
wmic process where "name='python.exe' and commandline like '%%floating_bot.py%%'" delete > NUL 2>&1
echo 모든 프로세스가 정리되었습니다.
pause
goto :EOF