import os
import subprocess
import shutil

# 1. 설정 정보
REPO_URL = "https://github.com/Kimjunesung96/kimjunesung20263600.git"
TARGET_DIR = r"C:\Users\skrkt\Desktop\고급인공지능\part2"
NODE_MODULES = os.path.join(TARGET_DIR, "news-app", "node_modules")

def run_git(commands):
    for cmd in commands:
        print(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True, cwd=TARGET_DIR)

def main():
    # 💡 .gitignore 파일이 없다면 node_modules를 제외하도록 생성
    gitignore_path = os.path.join(TARGET_DIR, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("news-app/node_modules/\n.git/\n")

    print("🚀 깃허브 강제 업로드 시작...")

    # 💡 Git 명령어 세트
    commands = [
        "git init",
        f"git remote remove origin", # 기존 연결 제거 (혹시 모르니)
        f"git remote add origin {REPO_URL}",
        "git add .",
        'git commit -m "Automated update from Python script"',
        "git branch -M main",
        "git push -u origin main --force" # 💡 강제로 덮어씌우기
    ]

    try:
        run_git(commands)
        print("\n✅ 업로드 완료! 이제 깃허브를 확인해보세요.")
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")

    os.system("pause")

if __name__ == "__main__":
    main()