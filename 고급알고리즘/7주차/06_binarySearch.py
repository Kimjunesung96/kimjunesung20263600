## 기본 라이브러리 임포트
from datetime import datetime
import os
## 추가 라이브러리
from bisect import bisect_left, bisect_right


## 실행 함수
def programStart():
    print(getCurrentTimeStr(), "programStart() is started...")
    ############################################################
    ## 여기에 코드를 작성하세요.

    # bSearch_example()

    # tteokCutting()

    # countNumber()

    ############################################################
    print(getCurrentTimeStr(), "programStart() is finished...")


def countNumber():
    n, x = map(
        int, input("데이터 배열의 크기와 찾으려는 데이터 값을 입력하세요: ").split()
    )  # 데이터의 개수 N, 찾고자 하는 값 x 입력받기
    array = list(
        map(int, input(f"전체 데이터(개수: {n})를 입력하세요: ").split())
    )  # 전체 데이터 입력받기

    # 값이 [x, x] 범위에 있는 데이터의 개수 계산
    right_index = bisect_right(array, x)
    left_index = bisect_left(array, x)

    count = right_index - left_index

    # 값이 x인 원소가 존재하지 않는다면
    if count == 0:
        print(-1)
    # 값이 x인 원소가 존재한다면
    else:
        print(f"데이터 {x}의 개수: {count}")


def tteokCutting():
    # 떡의 개수(N)와 요청한 떡의 길이(M)을 입력
    n, m = map(
        int, input("떡의 개수와 손님이 요청한 떡의 길이를 입력하세요: ").split(" ")
    )
    # 각 떡의 개별 높이 정보를 입력
    array = list(map(int, input(f"{n}개 떡의 각각의 길이를 입력하세요: ").split()))

    # 이진 탐색을 위한 시작점과 끝점 설정
    start = 0
    end = max(array)

    # 이진 탐색 수행 (반복적)
    cutPosition = 0
    total = 0
    while start <= end:
        total = 0
        mid = (start + end) // 2
        total = getCutTotal(mid, array)

        # 떡의 양이 부족한 경우 더 많이 잘라내기 (절단기 더 내리기, 왼쪽 부분 탐색)
        if total < m:
            end = mid - 1
        # 떡의 양이 충분한 경우 더 조금 잘라내기 (절단기 더 높이기, 오른쪽 부분 탐색)
        else:
            cutPosition = mid  # 최대한 덜 잘랐을 때가 정답이므로, 여기에서 result에 기록, 더 자를 수 있는 지점이 있다면 뒤에 업데이트 될 것
            start = mid + 1

    # 정답 출력
    total = getCutTotal(cutPosition, array)
    print(f"절단기의 설정 길이: {cutPosition}, 잘린 떡 길이 합: {total}")


# 잘랐을 때의 떡의 양 계산
def getCutTotal(pos, array):
    total = 0
    for x in array:
        # 잘랐을 때의 떡의 양 계산
        if x > pos:
            total += x - pos
    return total


def bSearch_example():
    # n(원소의 개수)과 target(찾고자 하는 값)을 입력 받기
    n, target = map(
        int, input("원소의 갯수와 찾고자 하는 값을 입력하세요: ").split()
    )

    # 전체 원소 입력 받기
    array = list(map(int, input(f"{n}개의 원소를 입력하세요: ").split()))

    # 이진 탐색 수행 결과 출력
    print("재귀 함수 방식의 이진 탐색을 시작합니다.")
    result = binary_search_recursive(array, target, 0, n - 1)

    # print("반복문 방식의 이진 탐색을 시작합니다.")
    # result = binary_search_loop(array, target, 0, n - 1)

    if result == None:
        print("원소가 존재하지 않습니다.")
    else:
        print(f"원소는 {result + 1}번째에 있습니다.")


# 이진 탐색 소스코드 구현 (재귀 함수)
def binary_search_recursive(array, target, start, end):
    if start > end:
        return None
    mid = (start + end) // 2
    # 찾은 경우 중간점 인덱스 반환
    if array[mid] == target:
        return mid
    # 중간점의 값보다 찾고자 하는 값이 작은 경우 왼쪽 확인
    elif array[mid] > target:
        return binary_search_recursive(array, target, start, mid - 1)
    # 중간점의 값보다 찾고자 하는 값이 큰 경우 오른쪽 확인
    else:
        return binary_search_recursive(array, target, mid + 1, end)


# 이진 탐색 소스코드 구현 (반복문)
def binary_search_loop(array, target, start, end):
    while start <= end:
        mid = (start + end) // 2
        # 찾은 경우 중간점 인덱스 반환
        if array[mid] == target:
            return mid
        # 중간점의 값보다 찾고자 하는 값이 작은 경우 왼쪽 확인
        elif array[mid] > target:
            end = mid - 1
        # 중간점의 값보다 찾고자 하는 값이 큰 경우 오른쪽 확인
        else:
            start = mid + 1
    return None


##############################################################################
## 시간 출력을 위한 함수
def getCurrentTimeStr():
    currentTimeStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return f"[{currentTimeStr}]"


##############################################################################
# DP 테이블 및 통계용 전역 변수
d = [0] * 100
count = 0


# ==============================================================================
# 1. 일반 재귀 피보나치 (Simple Recursion)
# - 특징: 기저 조건과 단순 점화식을 사용하지만, 중복 호출로 인해 시간복잡도가 O(2^N)으로 폭증함
# ==============================================================================
def fibo(x):
    global count
    count += 1  # [호출 카운트] 함수가 실행될 때마다 카운트

    # [기저 조건 (Base Case)]
    # 더 이상 재귀 호출을 하지 않는 종료 조건 (1번째, 2번째 피보나치 수는 1)
    if x == 1 or x == 2:
        return 1

    # [점화식 (Recurrence Relation)]
    # f(x) = f(x-1) + f(x-2) 의 형태
    return fibo(x - 1) + fibo(x - 2)


def fiboCall():
    global count
    count = 0  # 계산 시작 전 카운터 초기화

    try:
        user_input = input("피보나치 수를 구할 순서를 입력하세요 (예: 4): ")
        x = int(user_input)

        if x < 1:
            print("1 이상의 양의 정수를 입력해주세요.")
            return

        result = fibo(x)

        print(f"\n[일반 재귀] fibo({x}) = {result}")
        print(f"[통계] 총 계산(함수 호출) 횟수: {count}회\n")

    except ValueError:
        print("올바른 정수를 입력해주세요.")


# ==============================================================================
# 2. 탑다운 DP / 메모이제이션 (Top-Down Dynamic Programming)
# - 특징: 재귀 방식에 메모이제이션(Memoization)을 결합하여 중복 연산을 제거 (시간복잡도 O(N))
# ==============================================================================
def fiboTopdown(x):
    global count

    # [기저 조건] 1번째, 2번째 항목 처리 (카운트 X)
    if x == 1 or x == 2:
        return 1

    # [메모이제이션 읽기 (Memoization Read)]
    # 이미 계산된 값이 배열 d에 존재하면 즉시 반환 (중복 연산 방지)
    if d[x] != 0:
        return d[x]

    # [신규 연산 및 저장 (Memoization Write)]
    # 처음 계산하는 값일 때만 카운트를 올리고, 점화식 계산 결과를 배열 d에 저장 후 반환
    count += 1
    d[x] = fiboTopdown(x - 1) + fiboTopdown(x - 2)
    return d[x]


def fiboCall2():
    global count
    count = 0

    # 배열 d 초기화
    for i in range(len(d)):
        d[i] = 0

    try:
        user_input = input("피보나치 수를 구할 순서를 입력하세요 (예: 4): ")
        x = int(user_input)

        if x < 1:
            print("1 이상의 양의 정수를 입력해주세요.")
            return

        result = fiboTopdown(x)

        print(f"\n[탑다운 DP] fiboTopdown({x}) = {result}")
        print(f"[통계] 총 계산 횟수: {count}회\n")

    except ValueError:
        print("올바른 정수를 입력해주세요.")


# ==============================================================================
# 3. 바텀업 DP / 반복문 (Bottom-Up Dynamic Programming)
# - 특징: 반복문(Iteration)을 활용해 작은 문제부터 크기를 키워가며 DP 테이블을 채움
# ==============================================================================
def fiboBottomUp(x):
    global count

    # [초기값 설정 (Table Initialization)]
    # DP 테이블의 가장 작은 단위(기초 값)를 미리 채움
    d[1] = 1
    d[2] = 1

    # x가 1이나 2인 경우 반복문을 돌지 않고 바로 리턴
    if x == 1 or x == 2:
        return d[x]

    # [반복문을 통한 DP 테이블 작성 (Bottom-Up Iteration)]
    # 3부터 목표값 x까지 순차적으로 점화식을 적용하여 답을 쌓아 올림
    for i in range(3, x + 1):
        count += 1
        d[i] = d[i - 1] + d[i - 2]

    return d[x]


def fiboCall3():
    global count
    count = 0

    # 배열 d 초기화
    for i in range(len(d)):
        d[i] = 0

    try:
        user_input = input("피보나치 수를 구할 순서를 입력하세요 (예: 4): ")
        x = int(user_input)

        if x < 1:
            print("1 이상의 양의 정수를 입력해주세요.")
            return

        result = fiboBottomUp(x)

        print(f"\n[바텀업 DP] fiboBottomUp({x}) = {result}")
        print(f"[통계] 총 계산 횟수: {count}회\n")

    except ValueError:
        print("올바른 정수를 입력해주세요.")


# ==============================================================================
# 4. 개미 전사 문제 (Ant Warrior DP)
# - 특징: 인접한 식량창고는 터는 것이 불가능할 때, 얻을 수 있는 최대 식량 계산
# - 점화식: d[i] = max(d[i-1], d[i-2] + array[i])
# ==============================================================================
def antWarrior():
    # [1. 입력 처리] 식량창고 개수 N 및 창고별 식량 양 배열
    n = int(input())
    array = list(map(int, input().split()))

    # [2. DP 테이블 초기값 설정]
    d[0] = array[0]  # 첫 번째 창고만 있을 때는 첫 번째 걸 터는 것이 최선
    d[1] = max(
        array[0], array[1]
    )  # 두 번째 창고까지는 둘 중 더 큰 것을 선택 (인접 불가)

    # [3. 점화식을 통한 반복문 탐색]
    # 3번째 창고(인덱스 2)부터 마지막 창고(n-1)까지 판단
    for i in range(2, n):
        # d[i-1]            : 현재(i번째) 창고를 털지 않는 경우의 최댓값
        # d[i-2] + array[i] : 현재(i번째) 창고를 터는 경우의 최댓값 (i-1은 선택 불가)
        d[i] = max(d[i - 1], d[i - 2] + array[i])

    # [4. 결과 출력] N개 창고 고려 시의 최대 식량
    print(d[n - 1])
#########################################
mine=[[1,3,3,2],[2,1,4,1],[0,6,4,7]]
def goldMine():
    x,y=int(input().split(' '))
    for i in range(1,4):
        return a 
    
def goldmine():
    for tc in range(int(input("테스트 케이스 수 입력: "))):
        # 1. n: 행(세로), m: 열(가로)
        n, m = map(int, input().split())

        # 2. 전체 금광 정보 1차원 리스트로 입력 받기 (list로 감싸기 필수!)
        array = list(map(int, input().split()))

        # 3. 2차원 DP 테이블로 재구성 (n행 m열)
        dp = []
        index = 0
        for i in range(n):
            dp.append(array[index : index + m])
            index += m

        # 4. DP 진행 (열 기준: 1열부터 m-1열까지 오른쪽으로 이동)
        for j in range(1, m):
            for i in range(n):
                # ① 왼쪽 위에서 오는 경우
                if i == 0:
                    left_up = 0  # 맨 위 행이면 위에서 못 옴
                else:
                    left_up = dp[i - 1][j - 1]

                # ② 왼쪽 아래에서 오는 경우 (n-1이 맨 아래 행)
                if i == n - 1:
                    left_down = 0  # 맨 아래 행이면 아래서 못 옴
                else:
                    left_down = dp[i + 1][j - 1]

                # ③ 왼쪽에서 오는 경우
                left = dp[i][j - 1]

                # 점화식: 현재 위치 금 + (왼쪽위, 왼쪽아래, 왼쪽 중 최댓값)
                dp[i][j] = dp[i][j] + max(left_up, left_down, left)

        # 5. 마지막 열(m-1)의 값들 중 가장 큰 값이 정답
        result = 0
        for i in range(n):
            result = max(result, dp[i][m - 1])

        # 테스트 케이스 내부에서 결과 출력
        print(f"최대 금의 양: {result}")

###########################
## 파이선 메인 함수, 파일을 실행시키면 여기부터 실행, 이 부분은 반드시 파일의 맨 마지막에 위치해야 함
if __name__ == "__main__":
    start_time = datetime.now()
    print(getCurrentTimeStr(), "main Start..")

    ##############
    ## 파이선의 메인 함수를 이용해서 실행할 함수 (원하는 함수의 주석을 해제해서 실행)
    # programStart()
    # fiboCall()
    # fiboCall2()
    # fiboCall3()
    #antWarrior()
    ##############
    goldmine()
    finish_time = datetime.now()
    print(
        getCurrentTimeStr(),
        f"main Finish..({(finish_time - start_time).total_seconds()}s Elapsed)",
    )