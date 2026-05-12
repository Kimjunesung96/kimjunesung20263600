import os
import glob

def convert_bat_to_ansi():
    # 1. 현재 폴더의 모든 .bat 파일 목록 가져오기
    bat_files = glob.glob("*.bat")
    
    if not bat_files:
        print("현재 폴더에 .bat 파일이 없습니다.")
        return

    print(f"--- 배치 파일 ANSI 변환 시작 (대상: {len(bat_files)}개) ---")

    for file_path in bat_files:
        try:
            # 2. 먼저 UTF-8로 읽어오기
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # 💡 핵심: CP949로 바꿀 수 없는 문자(이모지 등)는 무시하고 지워버리기
            clean_content = content.encode('cp949', errors='ignore').decode('cp949')

            # 3. 깨끗해진 내용을 ANSI(cp949)로 다시 저장
            with open(file_path, 'w', encoding='cp949') as f:
                f.write(clean_content)
            
            print(f"✅ 변환 완료: {file_path} (호환 안 되는 이모지 자동 제거됨)")

        except UnicodeDecodeError:
            print(f"⏩ 건너뜀: {file_path} (이미 ANSI이거나 인코딩이 다릅니다.)")
        except Exception as e:
            print(f"❌ 에러 발생 ({file_path}): {str(e)}")

    print("\n--- 모든 작업이 완료되었습니다! ---")

if __name__ == "__main__":
    convert_bat_to_ansi()