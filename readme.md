# 🚀 화성 기지 비상 도어 개방 작전: 카이사르 암호 해독기

## 📌 프로젝트 개요
본 프로젝트는 화성 기지 엔지니어가 남긴 `password.txt` 파일 내의 카이사르 암호(Caesar Cipher)를 해독하여 `result.txt`로 출력하는 파이썬 프로그램입니다. 

단순한 1차원 문자열 덮어쓰기 연산을 지양하고, **26행 x N열 크기의 2차원 매트릭스(List of Lists) 구조**를 채택하여 데이터의 불변성(Immutability)을 유지하고 파이썬의 `List Comprehension` 및 문자열 처리 최적화 기법을 적용했습니다.

---

## ⚙️ 실행 환경 및 제약 조건 준수 사항
* **Language:** Python 3.x
* **Dependencies:** 오직 파이썬 기본 내장 라이브러리만 사용 (외부 패키지 사용 ❌)
* **Coding Convention:** PEP 8 스타일 가이드 준수 (문자열 홑따옴표 `' '` 사용, 연산자 공백 확보)
* **Exception Handling:** File I/O 및 사용자 입력 형변환(Casting) 예외 처리 완벽 적용

---

## 🧠 핵심 알고리즘: 블럭 단위 코드 해설

본 프로그램은 크게 5개의 논리적 블럭으로 구성되어 있습니다.

### [Block 1] 초기화 및 2D 매트릭스 데이터 구조 생성
```python
def caesar_cipher_decode(target_text):
    print('=== 카이사르 암호 해독: 2D 매트릭스 방식 ===\n')
    
    # 26행(Shift 경우의 수) x N열(암호문 길이) 크기의 2차원 빈 배열 생성
    matrix = [['' for _ in range(len(target_text))] for _ in range(26)]
    decoded_results = {}