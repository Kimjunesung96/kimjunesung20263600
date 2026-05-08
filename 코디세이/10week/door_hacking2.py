import zipfile
import time
import sys
import zlib
#python door_hacking.py 4 1 <<나눌획수 맡을구역
def unlock_zip():
    # 설정 값
    file_name = 'emergency_storage_key.zip'
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    
    # 1. 시작 시간 기록 및 출력 (요구사항)
    current_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    start_time = time.time()
    print('=== 화성 기지 해킹 작전 개시 ===')
    print(f'[시작 시간]: {current_time_str}')

    attempts = 0

    # 2. 수동 분산 처리를 위한 인자 확인 (보너스 과제: 알고리즘)
    # 실행 방법: python door_hacking.py [총일꾼수] [내번호]
    if len(sys.argv) == 3:
        total_workers = int(sys.argv[1])
        my_id = int(sys.argv[2])
    else:
        total_workers = 1
        my_id = 1

    # 첫 3자리를 기준으로 구역 나누기 (전체 46,656개 조합 분할)
    chunks = [c1 + c2 + c3 for c1 in chars for c2 in chars for c3 in chars]
    chunk_size = len(chunks) // total_workers
    start_idx = (my_id - 1) * chunk_size
    end_idx = len(chunks) if my_id == total_workers else my_id * chunk_size
    
    my_chunks = chunks[start_idx:end_idx]
    all_chunks = chunks  # 뒤 3자리를 위한 전체 리스트

    print(f'[정보] 일꾼 {my_id}번 투입 (구역: {start_idx} ~ {end_idx})')

    try:
        # 파일 핸들링 예외 처리 시작
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            # zip 파일 내의 첫 번째 파일 이름 획득
            target_file = zip_ref.namelist()[0]
            
            for p1 in my_chunks:
                for p2 in all_chunks:
                    password = p1 + p2
                    attempts += 1
                    
                    try:
                        # 3. 암호 시도 (데이터 읽기 시도)
                        zip_ref.read(target_file, pwd=password.encode('utf-8'))
                        
                        # 성공 시 결과 저장 및 출력
                        elapsed = time.time() - start_time
                        with open('password.txt', 'w') as f:
                            f.write(password)
                            
                        print(f'\n🎉 성공! 암호 발견: {password}')
                        print(f'반복 회수: {attempts}회')
                        print(f'진행 시간: {elapsed:.2f}초')
                        return
                    
                    # 4. 구체적인 예외 처리 (RuntimeError, BadZipFile, zlib.error)
                    # 암호가 틀리면 zlib.error나 RuntimeError가 발생함
                    except (RuntimeError, zipfile.BadZipFile, zlib.error):
                        # 100만 번마다 진행 상황 보고
                        if attempts % 1000000 == 0:
                            elapsed = time.time() - start_time
                            print(f'🕒 {my_id}번 보고: {attempts}회 시도 중... ({elapsed:.1f}초 경과)')
                        continue

    # 5. 파일 처리 관련 예외 처리 (FileNotFound 등)
    except FileNotFoundError:
        print(f'[오류] {file_name} 파일을 찾을 수 없습니다.')
    except zipfile.LargeZipFile:
        print('[오류] 지원하지 않는 대용량 zip 파일입니다.')
    except Exception as e:
        print(f'[비상] 예기치 못한 오류 발생: {e}')

if __name__ == '__main__':
    unlock_zip()