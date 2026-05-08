@echo off
echo 📦 프로젝트 초기 설정을 시작합니다...
pip install -r requirements.txt
cd news-app && npm install
echo ✅ 모든 부품 설치 완료! 이제 run_all.bat을 실행하세요.
pause