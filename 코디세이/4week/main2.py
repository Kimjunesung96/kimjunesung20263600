def solve_inventory_problem():
    log_file = 'Mars_Base_Inventory_List.csv'
    output_csv = 'Mars_Base_Inventory_danger.csv'
    output_bin = 'Mars_Base_Inventory_List.bin'
    
    inventory_list = []

    # 1. 파일 읽기 및 리스트 객체 변환 (예외 처리)
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            header = f.readline()
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                # 데이터 구조: [Substance, Weight, Gravity, Strength, Flammability]
                inventory_list.append(parts)
    except FileNotFoundError:
        print('에러: 파일을 찾을 수 없습니다.')
        return
    except Exception as e:
        print(f'파일 읽기 중 에러 발생: {e}')
        return

    # 2. 인화성(마지막 열) 기준 내림차순 정렬
    # 별도의 라이브러리 없이 기본 sort와 key 인자 사용
    inventory_list.sort(key=lambda x: float(x[-1]), reverse=True)

    # 3. 0.7 이상 추출 및 CSV 저장
    print('=== 인화성 지수 0.7 이상 위험 물질 목록 ===')
    try:
        with open(output_csv, 'w', encoding='utf-8') as f_out:
            f_out.write(header)
            for item in inventory_list:
                if float(item[-1]) >= 0.7:
                    print(item)
                    f_out.write(','.join(item) + '\n')
    except Exception as e:
        print(f'CSV 쓰기 에러: {e}')

    # [보너스 과제 1] 이진 파일(Binary) 형태로 직접 저장
    # pickle 없이 문자열을 utf-8 바이트로 인코딩하여 저장합니다.
    try:
        with open(output_bin, 'wb') as f_bin:
            for item in inventory_list:
                # 각 행을 문자열로 합친 뒤 줄바꿈을 붙여 바이트로 변환
                data_line = ','.join(item) + '\n'
                f_bin.write(data_line.encode('utf-8'))
        print(f'\n이진 파일 저장 완료: {output_bin}')
    except Exception as e:
        print(f'이진 파일 저장 에러: {e}')

    # [보너스 과제 2] 이진 파일 다시 읽기 및 출력
    try:
        print('\n=== 이진 파일(.bin)에서 복구된 내용 ===')
        with open(output_bin, 'rb') as f_bin_read:
            binary_content = f_bin_read.read()
            # 바이트를 다시 문자열로 디코딩하여 출력
            print(binary_content.decode('utf-8'))
    except Exception as e:
        print(f'이진 파일 읽기 에러: {e}')

if __name__ == '__main__':
    solve_inventory_problem()
