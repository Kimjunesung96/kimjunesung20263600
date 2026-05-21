# 파일 이름 설정
log_file = 'Mars_Base_Inventory_List.csv'
output_csv = 'Mars_Base_Inventory_danger.csv'
output_bin = 'Mars_Base_Inventory_List.bin'

inventory_list = []

try:
    # --- [1단계] 파일 읽기 ---
    with open(log_file, 'r', encoding='utf-8') as f:
        header = f.readline()  # 첫 줄(제목)은 데이터 처리에서 제외하기 위해 따로 읽음
        lines = f.readlines()  # 나머지 모든 줄을 리스트로 읽어옴

    # --- [2단계] 데이터를 리스트 객체로 변환 ---
    for line in lines:
        line = line.strip()
        if line:
            # 쉼표를 기준으로 잘라서 리스트에 추가
            inventory_list.append(line.split(','))

    # --- [3단계] 인화성 기준 내림차순 정렬 ---
    # x[-1]은 각 줄의 마지막 항목(인화성)을 뜻하며, float로 바꿔서 숫자 크기를 비교함
    inventory_list.sort(key=lambda x: float(x[-1]), reverse=True)

    # --- [4단계] 0.7 이상 위험 물질 출력 및 CSV 저장 ---
    print('=== 인화성 0.7 이상 위험 물질 목록 ===')
    with open(output_csv, 'w', encoding='utf-8') as f_out:
        f_out.write(header)  # 새 파일에도 제목 줄 추가
        for item in inventory_list:
            flammability = float(item[-1])
            if flammability >= 0.7:
                print(item)  # 화면 출력
                f_out.write(','.join(item) + '\n')  # 파일 저장

    # --- [보너스 1] 이진(Binary) 파일로 저장 ---
    # 'wb'는 Write Binary의 약자로, 텍스트가 아닌 데이터 그 자체로 저장함
    with open(output_bin, 'wb') as f_bin:
        for item in inventory_list:
            data = ','.join(item) + '\n'
            # 문자열을 바이트(bytes) 형태로 변환해서 저장해야 함
            f_bin.write(data.encode('utf-8'))

    # --- [보너스 2] 이진 파일 다시 읽어서 출력 ---
    print('\n=== 이진 파일(.bin)에서 복구된 내용 ===')
    with open(output_bin, 'rb') as f_bin_read:
        content = f_bin_read.read()
        # 바이트 데이터를 다시 우리가 읽을 수 있는 문자로 변환(decode)
        print(content.decode('utf-8'))

except Exception as e:
    print(f'오류 발생: {e}')
