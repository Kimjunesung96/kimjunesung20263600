# 1. 설정 및 변수 준비
log_file = 'Mars_Base_Inventory_List.csv'
output_csv = 'Mars_Base_Inventory_danger.csv'
all_items = []

try:
    # 2. 파일 읽기 및 리스트 저장
    with open(log_file, 'r', encoding='utf-8') as f:
        header = f.readline()  # 첫 줄은 제목이니 따로 보관
        for line in f:
            line = line.strip()
            if line:
                all_items.append(line.split(','))

    # 3. 인화성(마지막 열) 기준으로 정렬 (가장 높은게 위로)
    # float(x[-1])은 마지막 칸의 문자를 숫자로 바꿔서 비교하겠다는 뜻입니다.
    all_items.sort(key=lambda x: float(x[-1]), reverse=True)

    # 4. 화면 출력 및 위험 물질(0.7 이상) 파일 저장
    print('--- 인화성 0.7 이상 위험 물질 목록 ---')
    
    with open(output_csv, 'w', encoding='utf-8') as f_out:
        f_out.write(header)  # 새 파일에도 제목 줄을 넣어줍니다.
        
        for item in all_items:
            # 마지막 칸의 숫자가 0.7 이상인지 확인
            if float(item[-1]) >= 0.7:
                # 화면에 출력
                print(item)
                # 파일에 쓰기 (리스트를 다시 콤마로 연결해서 저장)
                f_out.write(','.join(item) + '\n')

    print(f'\n작업 완료! {output_csv} 파일을 확인하세요.')

except Exception as e:
    print(f'오류가 발생했습니다: {e}')
