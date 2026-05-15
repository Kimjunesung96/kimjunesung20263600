@echo off

echo ========================================================
echo [STEP 1] Checking and Installing Node.js...
echo ========================================================
taskkill /F /IM msiexec.exe > nul 2>&1
winget install OpenJS.NodeJS.LTS --source winget --accept-package-agreements --accept-source-agreements

echo.
echo ========================================================
echo [STEP 2] Installing Python Modules...
echo ========================================================
pip install -r requirements.txt
pip install finance-datareader bs4 pandas

echo.
echo ========================================================
echo [STEP 3] Installing React Modules (news-app)...
echo ========================================================
cd news-app
call npm install
cd ..

echo.
echo ========================================================
echo [COMPLETE] All setup finished perfectly!
echo Please close this window and run 'run_all.bat'.
echo ========================================================
pause