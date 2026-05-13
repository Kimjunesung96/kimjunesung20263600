def caesar_cipher_decode(target_text):
    print('=== 카이사르 암호 해독: 2D 매트릭스 방식 ===\n')
    
    # 1. 26행(Shift) x 원본길이(열) 크기의 2차원 리스트(행렬) 생성
    matrix = [['' for _ in range(len(target_text))] for _ in range(26)]
    
    decoded_results = {}

    # 2. 매트릭스에 해독된 토큰(글자)들을 채워 넣기
    for row in range(26):
        shift = row + 1
        for col, char in enumerate(target_text):
            if 'a' <= char <= 'z':
                matrix[row][col] = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                matrix[row][col] = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                matrix[row][col] = char
        
        # 3. 완성된 한 층(row)의 토큰들을 문자열로 결합
        decoded_text = ''.join(matrix[row])
        decoded_results[shift] = decoded_text
        print(f'[{shift:2d}번 굴림] 매트릭스 조립 결과: {decoded_text}')

    print('\n' + '=' * 50)
    
    # 4. 정답 입력 및 파일 저장 (예외 처리 포함)
    try:
        user_choice = int(input('가장 말이 되는 문장의 [굴린 횟수]를 입력하세요: '))
        
        if user_choice in decoded_results:
            final_decoded = decoded_results[user_choice]
            
            with open('result.txt', 'w') as f:
                f.write(final_decoded)
            print(f'\n🎉 작전 성공! [{final_decoded}] 가 result.txt 에 저장되었습니다.')
        else:
            print('[오류] 1에서 26 사이의 숫자만 입력 가능합니다.')
            
    except ValueError:
        print('[오류] 정확한 숫자를 입력해 주세요.')
    except IOError as e:
        print(f'[오류] 파일 저장 중 문제가 발생했습니다: {e}')

def main():
    try:
        with open('password.txt', 'r') as f:
            target_text = f.read().strip()
            
        if not target_text:
            print('[오류] password.txt 파일이 비어 있습니다.')
            return
            
        # 요구사항에 명시된 함수 이름으로 호출
        caesar_cipher_decode(target_text)
        
    except FileNotFoundError:
        print('[오류] password.txt 파일을 찾을 수 없습니다.')
    except Exception as e:
        print(f'[비상] 예기치 못한 오류 발생: {e}')

if __name__ == '__main__':
    main()