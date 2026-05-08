def caesar_cipher_commander_logic(target_text):
    print('=== 카이사르 암호 해독: 누적 +1 톱니바퀴 방식 ===\n')
    
    # 1. 리스트 변환 및 대소문자 기억
    num_list = []
    is_upper_list = []
    
    for char in target_text:
        if 'a' <= char <= 'z':
            num_list.append(ord(char) - ord('a'))
            is_upper_list.append(False)
        elif 'A' <= char <= 'Z':
            num_list.append(ord(char) - ord('A'))
            is_upper_list.append(True)
        else:
            num_list.append(char)
            is_upper_list.append(None)

    # 각 회차별 결과를 담아둘 창고 (저장 시 혼선 방지)
    decoded_results = {}

    # 2. 26번 누적하며 출력
    # 톱니바퀴를 돌릴 때마다 리스트의 상태가 변하므로 이를 각 회차별로 저장합니다.
    current_nums = list(num_list) 
    for shift in range(1, 27):
        decoded_text = ''
        for i in range(len(current_nums)):
            if isinstance(current_nums[i], int):
                # 1씩 더해서 톱니바퀴를 굴립니다.
                current_nums[i] = (current_nums[i] + 1) % 26
                
                if is_upper_list[i]:
                    decoded_text += chr(current_nums[i] + ord('A'))
                else:
                    decoded_text += chr(current_nums[i] + ord('a'))
            else:
                decoded_text += current_nums[i]
        
        decoded_results[shift] = decoded_text
        print(f'[{shift:2d}번 누적해서 굴림] 결과: {decoded_text}')

    print('\n' + '=' * 50)
    
    # 3. 정답 입력 및 예외 처리 (제약 사항 준수)
    try:
        user_choice = int(input('가장 말이 되는 문장의 [굴린 횟수]를 입력하세요: '))
        
        if user_choice in decoded_results:
            final_decoded = decoded_results[user_choice]
            
            # 4. 파일 저장 및 예외 처리 (제약 사항 준수)
            with open('result.txt', 'w') as f:
                f.write(final_decoded)
            print(f'\n🎉 완료! [{final_decoded}] 가 result.txt 에 저장되었습니다.')
        else:
            print('[오류] 1에서 26 사이의 숫자만 입력 가능합니다.')
            
    except ValueError:
        print('[오류] 정확한 숫자를 입력해 주세요.')
    except IOError as e:
        print(f'[오류] 파일 저장 중 문제가 발생했습니다: {e}')

def main():
    try:
        # password.txt 파일 읽기 및 예외 처리
        with open('password.txt', 'r') as f:
            target_text = f.read().strip()
            
        if not target_text:
            print('[오류] password.txt 파일이 비어 있습니다.')
            return
            
        caesar_cipher_commander_logic(target_text)
        
    except FileNotFoundError:
        print('[오류] password.txt 파일을 찾을 수 없습니다.')
    except Exception as e:
        print(f'[비상] 예기치 못한 오류 발생: {e}')

if __name__ == '__main__':
    main()