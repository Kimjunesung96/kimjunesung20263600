@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo 🧹 [1단계] 기존 dist 폴더 삭제 중...
cd news-app

:: dist 폴더가 있으면 강제 삭제 (s:하위폴더포함, q:묻지않음)
if exist dist (
    rmdir /s /q dist
    echo ✅ dist 폴더가 삭제되었습니다.
) else (
    echo ⚠️ dist 폴더가 없어서 바로 빌드로 넘어갑니다.
)

echo 📦 [2단계] npm run build 실행 중...
call npm run build

echo.
echo ========================================================
echo ✅ 빌드가 완료되었습니다.
echo ========================================================
pause