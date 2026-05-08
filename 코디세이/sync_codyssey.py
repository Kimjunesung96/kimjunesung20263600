import os
import subprocess
import shutil
import tempfile
import datetime

# ================= 설정 구간 =================
# 1. 내 컴퓨터의 원본 소스 경로 (코디세이 폴더)
SOURCE_DIR = r"C:\Users\skrkt\Desktop\코디세이"

# 2. 깃허브 저장소 정보
REPO_URL = "https://github.com/Kimjunesung96/kimjunesung20263600.git"

# 3. 저장소 내에서 파일을 넣을 대상 폴더
TARGET_SUBFOLDER = "코디세이"
# =============================================

def run_command(cmd, cwd=None):
    """터미널 명령어를 실행하고 결과를 출력합니다. (한글 깨짐 방지 utf-8 적용)"""
    try:
        # encoding='utf-8' 옵션을 추가하여 윈도우 cp949 에러를 완벽 차단!
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ 에러 발생: {e.stderr}")
        raise

def main():
    # 1. 임시 작업 폴더 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📂 1. 임시 작업소 생성: {temp_dir}")

        # 2. 깃허브에서 기존 데이터 클론 (고급인공지능 등 전체 기록 보존)
        print("📥 2. 깃허브에서 기존 데이터를 안전하게 복제 중...")
        run_command(f"git clone {REPO_URL} .", cwd=temp_dir)

        # 3. 대상 폴더 경로 설정 (코디세이)
        target_path = os.path.join(temp_dir, TARGET_SUBFOLDER)
        
        # 깃허브에 코디세이 폴더가 없으면 생성
        os.makedirs(target_path, exist_ok=True)

        # 4. 파일 복사 (__pycache__, 바로가기 등 불필요한 파일 제외)
        print("📦 3. 로컬 코디세이 파일 복사 중 (찌꺼기 제거)...")
        ignore_patterns = shutil.ignore_patterns(
            "node_modules", ".git", "__pycache__", ".vscode", "*.pyc", "*.lnk"
        )
        
        for item in os.listdir(SOURCE_DIR):
            s = os.path.join(SOURCE_DIR, item)
            d = os.path.join(target_path, item)
            
            if any(x in item for x in ["node_modules", ".git"]):
                continue

            if os.path.isdir(s):
                shutil.copytree(s, d, ignore=ignore_patterns, dirs_exist_ok=True)
            else:
                # .lnk (바로가기) 파일은 깃허브에 올릴 필요가 없으므로 무시
                if not item.endswith('.lnk'):
                    shutil.copy2(s, d)

        # 5. 깃허브 업로드 진행 (Add -> Commit -> Push)
        print("📤 4. 변경사항을 깃허브로 안전하게 전송 중...")
        try:
            run_command("git add .", cwd=temp_dir)
            
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"[코디세이] 로컬 파일 동기화 ({now})"
            
            run_command(f'git commit -m "{commit_msg}"', cwd=temp_dir)
            run_command("git push origin main", cwd=temp_dir)
            
            print("\n✅ 모든 작업이 성공적으로 완료되었습니다!")
            print(f"🔗 확인: {REPO_URL}")
            
        except subprocess.CalledProcessError:
            print("\nℹ️ 변경된 내용이 없거나 업로드에 실패했습니다.")

if __name__ == "__main__":
    main()
    input("\n계속하려면 엔터를 누르세요...")