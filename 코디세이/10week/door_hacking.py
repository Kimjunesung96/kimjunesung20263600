import zipfile
import time
#실행후 21 14 3분에2아님 실질적으로 13/21
def unlock_zip():
    file_name = 'emergency_storage_key.zip'
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    
    # 1. 라이브러리 없이 분산 처리하는 대화형 입력 (UX 최적화)
    print("=== 화성 기지 해킹 시스템 ===")
    user_input = input("투입할 총 일꾼 수와 내 번호를 입력하세요 (예: 4 1) / 단일 모드는 엔터: ").strip()
    
    if user_input:
        parts = user_input.split()
        total_workers = int(parts[0])
        my_id = int(parts[1])
    else:
        total_workers = 1
        my_id = 1

    # 2. 시작 시간 기록 및 출력
    current_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    start_time = time.time()
    print('\n=== 작전 개시 ===')
    print(f'[시작 시간]: {current_time_str}')

    # 첫 3자리를 기준으로 구역 분할
    chunks = [c1 + c2 + c3 for c1 in chars for c2 in chars for c3 in chars]
    chunk_size = len(chunks) // total_workers
    start_idx = (my_id - 1) * chunk_size 
    end_idx = len(chunks) if my_id == total_workers else my_id * chunk_size
    
    my_chunks = chunks[start_idx:end_idx]
    all_chunks = chunks

    print(f'[정보] 일꾼 {my_id}번 투입 (담당 구역: {start_idx} ~ {end_idx})')
    attempts = 0

    try:
        # 파일 열기
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            target_file = zip_ref.namelist()[0]
            
            for p1 in my_chunks:
                for p2 in all_chunks:
                    password = p1 + p2
                    attempts += 1
                    
                    try:
                        # 암호 대입
                        zip_ref.read(target_file, pwd=password.encode('utf-8'))
                        
                        # 성공 시 결과 저장
                        elapsed = time.time() - start_time
                        with open('password.txt', 'w') as f:
                            f.write(password)
                            
                        print(f'\n🎉 성공! 암호 발견: {password}')
                        print(f'반복 회수: {attempts}회')
                        print(f'진행 시간: {elapsed:.2f}초')
                        return
                    
                    # zlib 라이브러리마저 제거했으므로, 암호 틀림 에러는 포괄적 예외로 넘김
                    except Exception:
                        if attempts % 1000000 == 0:
                            elapsed = time.time() - start_time
                            print(f'🕒 {my_id}번 보고: {attempts}회 시도 중... ({elapsed:.1f}초 경과)')
                        continue

    # 전체 시스템 예외 처리
    except FileNotFoundError:
        print(f'[오류] {file_name} 파일을 찾을 수 없습니다.')
    except Exception as e:
        print(f'[비상] 예기치 못한 오류 발생: {e}')

if __name__ == '__main__':
    unlock_zip()