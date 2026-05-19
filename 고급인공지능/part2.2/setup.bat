@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ========================================================
echo  AI 뉴스 큐레이터 - 최초 설치 스크립트
echo ========================================================
echo.

:: Python 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Python 이 설치되어 있지 않습니다.
    echo  https://www.python.org 에서 3.10 이상 설치 후 다시 실행해 주세요.
    pause
    exit /b 1
)

:: pip 최신화
echo [1/2] pip 최신 버전으로 업그레이드 중...
python -m pip install --upgrade pip --quiet

:: 패키지 설치
echo [2/2] 필요한 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [오류] 패키지 설치 중 문제가 발생했습니다.
    echo  인터넷 연결을 확인하고 다시 시도해 주세요.
    pause
    exit /b 1
)

:: dist 폴더 확인
echo.
if not exist "news-app\dist\index.html" (
    echo [경고] news-app\dist 폴더가 없습니다^^!
    echo  개발 PC에서 npm run build 후 dist 폴더를 통째로 복사해 오세요.
    echo  dist 없이는 브라우저 화면이 열리지 않습니다.
    echo.
) else (
    echo  dist 폴더 확인 완료^^!
)

echo ========================================================
echo  설치가 모두 끝났습니다^^!
echo  이 창을 닫고 run_all.bat 을 실행해 주세요.
echo ========================================================
pause