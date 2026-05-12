@echo off
chcp 65001 > nul

:: 1. 8000번 포트(API 서버)를 쓰고 있는 프로세스 번호(PID)를 직접 찾아냅니다.
set "PID="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do set PID=%%a

:: 2. 만약 프로세스 번호가 발견되면(이미 실행 중이면) 종료 모드로 점프!
if not "%PID%"=="" goto TURN_OFF

:TURN_ON
echo  AI 뉴스 큐레이터 시스템 전체 가동을 시작합니다!

echo 1. 뉴스 수집 엔진 가동 중...
start "News_Engine" cmd /k "python main_engine.py"

echo 2. API 서버 가동 중...
start "API_Server" cmd /k "uvicorn api_server:app --reload"

echo 3. 리액트 프론트엔드 가동 중...
start "React_App" cmd /k "cd news-app && npm run dev"

echo 4. 바탕화면 로봇 비서 가동 중...
start "Floating_Bot" cmd /k "python floating_bot.py"

echo  모든 시스템이 성공적으로 켜졌습니다!
goto :EOF

:TURN_OFF
echo  이미 시스템이 가동 중이거나 좀비 프로세스가 발견되었습니다.
echo  모든 관련 프로세스와 터미널을 강제 종료합니다...

:: 3. 8000번 포트를 잡고 있는 주범(PID)을 직접 사살
taskkill /F /PID %PID% > NUL 2>&1

:: 4. 창 제목을 기준으로 모든 터미널 창을 싹 닫아버림
taskkill /F /T /FI "WINDOWTITLE eq News_Engine*" > NUL 2>&1
taskkill /F /T /FI "WINDOWTITLE eq API_Server*" > NUL 2>&1
taskkill /F /T /FI "WINDOWTITLE eq React_App*" > NUL 2>&1
taskkill /F /T /FI "WINDOWTITLE eq Floating_Bot*" > NUL 2>&1

:: 5. [중요] 이름표 없이 숨어있는 파이썬 좀비들까지 확인 사살
wmic process where "name='python.exe' and commandline like '%%main_engine.py%%'" delete > NUL 2>&1
wmic process where "name='python.exe' and commandline like '%%floating_bot.py%%'" delete > NUL 2>&1
taskkill /F /IM node.exe > NUL 2>&1

echo  복제된 로봇과 터미널을 모두 정리했습니다! 퇴근하세요!
set PID=
pause
goto :EOF