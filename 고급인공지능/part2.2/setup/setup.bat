@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo 📦 [1단계] 윈도우 방해물 제거 및 Node.js(웹 엔진) 설치 중...
echo ========================================================
taskkill /F /IM msiexec.exe > nul 2>&1
winget install OpenJS.NodeJS.LTS --source winget --accept-package-agreements --accept-source-agreements

echo.
echo ========================================================
echo 🐍 [2단계] 파이썬 하청업체(부품) 모두 고용 중...
echo ========================================================
pip install -r requirements.txt

echo.
echo ========================================================
echo ⚛️ [3단계] 리액트 웹 화면 부품 설치 중... (news-app)
echo ========================================================
cd news-app
call npm install
cd ..

echo.
echo ========================================================
echo ✅ 모든 부품(파이썬 + 리액트) 설치가 완벽하게 끝났습니다!
echo 🚨 이제 이 창을 닫고 'run_all.bat'을 켜주세요.
echo ========================================================
pause