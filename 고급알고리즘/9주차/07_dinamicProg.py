## 기본 라이브러리 임포트
from datetime import datetime
import os
## 추가 라이브러리





## 실행 함수
def programStart():
    print(getCurrentTimeStr(), "programStart() is started...")
    ############################################################
    ## 여기에 코드를 작성하세요.

    n = 6 # 40? 99?
    # fibo_recursiveFunc(n)
    
    # fibo_dp_topdown(n)
    # fibo_dp_bottomup(n)
    
    # makeOne()    
    # antWarrior()
    # valueCombination()
    
    # goldCave()
    # troopDeployment_LIS()
    dextra()

    ############################################################
    print(getCurrentTimeStr(), "programStart() is finished...")
'''
def troopDeployment_LIS():
    n = int(input("병사의 수를 입력하세요: "))
    array = list(map(int, input(f"{n}명의 병사들에 대해 전투력을 입력해주세요: ").split()))
    
    # 순서를 뒤집어 '최장 증가 부분 수열' 문제로 변환
    array.reverse()

    # 다이나믹 프로그래밍을 위한 1차원 DP 테이블 초기화
    dp = [1] * n

    # 가장 긴 증가하는 부분 수열(LIS) 알고리즘 수행
    # 특정 원소의 앞에 자기자신보다 작은 원소가 몇 개나 있는가를 확인, 즉, 정렬을 유지하며 가능한 수열의 길이를 확인
    for i in range(1, n):
        for j in range(0, i):
            if array[j] < array[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    # 열외해야 하는 병사의 최소 수를 출력
    print(f"전투력 내림차순 유지하면서 병사를 최대로 배치하기 위해 열외시켜야 하는 병사의 수: {n - max(dp)}")

def goldCave():
    # 테스트 케이스(Test Case) 입력
    t = int(input("테스트 케이스 수를 입력하세요: "))
    
    for tc in range(t):
        # 금광 정보 입력
        n, m = map(int, input(f"{tc+1}번째 테스트 케이스의 금광 크기를 입력하세요(행, 열): ").split())
        array = list(map(int, input(f"{n}행*{m}열의 총 {n*m}개 금광 내용을 입력하세요: ").split()))
        
        # 다이나믹 프로그래밍을 위한 2차원 DP 테이블 초기화
        dp = []
        index = 0
        for i in range(n):
            dp.append(array[index:index + m])
            index += m
            
        # 다이나믹 프로그래밍 진행
        for j in range(1, m):
            for i in range(n):
                # 왼쪽 위에서 오는 경우
                if i == 0: 
                    left_up = 0
                else: 
                    left_up = dp[i - 1][j - 1]
                
                # 왼쪽 아래에서 오는 경우
                if i == n - 1: 
                    left_down = 0
                else: 
                    left_down = dp[i + 1][j - 1]
                
                # 왼쪽에서 오는 경우
                left = dp[i][j - 1]
                
                #얻을 수 있는 최대 값
                dp[i][j] = dp[i][j] + max(left_up, left_down, left)
                
        result = 0
        for i in range(n):
            result = max(result, dp[i][m - 1])
        print(f"{tc+1}번째 테스트 케이스에서 얻을 수 있는 금의 최대 크기: {result}")

def valueCombination():
    # 정수 N, M을 입력 받기
    n, m = map(int, input("화폐 개수와 만들고자 하는 가치를 입력하세요: ").split())
    
    # N개의 화폐 단위 정보를 입력받기
    array = []
    for i in range(n):
        array.append(int(input(f"{n}개 중, {i+1}번째 화폐 가치를 입력하세요: ")))
    
    # 한 번 계산된 결과를 저장하기 위한 DP 테이블 초기화
    d = [10001] * (m + 1)
    
    # 다이나믹 프로그래밍(Dynamic Programming) 진행(보텀업)
    d[0] = 0
    for i in range(n):
        for j in range(array[i], m + 1):
            if d[j - array[i]] != 10001: # (i - k)원을 만드는 방법이 존재하는 경우
                d[j] = min(d[j], d[j - array[i]] + 1)
    
    # 계산된 결과 출력
    if d[m] == 10001: # 최종적으로 M원을 만드는 방법이 없는 경우
        print(f"{m}원을 만들기 위한 최소 화폐 개수: -1 (만들수 없음)")
    else:
        print(f"{m}원을 만들기 위한 최소 화폐 개수: {d[m]}")
        
def antWarrior():
    # 정수 N을 입력 받기
    n = int(input("식량 창고의 개수를 입력하세요: "))
    
    # 모든 식량 정보 입력 받기
    array = list(map(int, input(f"각 창고의 식량 개수를 입력하세요: ").split()))

    # 앞서 계산된 결과를 저장하기 위한 DP 테이블 초기화
    d = [0] * 100

    # 다이나믹 프로그래밍(Dynamic Programming) 진행 (보텀업)
    d[0] = array[0]
    d[1] = max(array[0], array[1]) 
    for i in range(2, n):
        d[i] = max(d[i - 1], d[i - 2] + array[i])

    # 계산된 결과 출력
    print(f"얻을 수 있는 식량의 최대값: {d[n - 1]}")

def makeOne():
    # 정수 X를 입력 받기
    x = int(input("정수 X를 입력하세요: "))

    # 앞서 계산된 결과를 저장하기 위한 DP 테이블 초기화
    d = [0] * 30001

    # 다이나믹 프로그래밍(Dynamic Programming) 진행 (보텀업)
    for i in range(2, x + 1):
        # 현재의 수에서 1을 빼는 경우
        d[i] = d[i - 1] + 1
        
        # 현재의 수가 2로 나누어 떨어지는 경우
        if i % 2 == 0:
            d[i] = min(d[i], d[i // 2] + 1)
            
        # 현재의 수가 3으로 나누어 떨어지는 경우
        if i % 3 == 0:
            d[i] = min(d[i], d[i // 3] + 1)
            
        # 현재의 수가 5로 나누어 떨어지는 경우
        if i % 5 == 0:
            d[i] = min(d[i], d[i // 5] + 1)

    print(f"{x}를 1로 만들기 위한 최소 연산 횟수: {d[x]}")

operationCnt = 0
def fibo_dp_bottomup(n):
    global operationCnt
    operationCnt = 0
        
    # 앞서 계산된 결과를 저장하기 위한 DP 테이블 초기화
    d = [0] * 100

    # 첫 번째 피보나치 수와 두 번째 피보나치 수는 1
    d[1] = 1
    d[2] = 1    

    # 피보나치 함수(Fibonacci Function) 반복문으로 구현(보텀업 다이나믹 프로그래밍)
    for i in range(3, n + 1):
        operationCnt += 1
        d[i] = d[i - 1] + d[i - 2]

    print(f"피보나치 수열에서 {n}번째 수열의 값: {d[n]}")
    print(f"총 연산 횟수: {operationCnt}")

operationCnt = 0
def fibo_dp_topdown(n):
    global operationCnt
    operationCnt = 0
    
    # 한 번 계산된 결과를 메모이제이션(Memoization)하기 위한 리스트 초기화
    d = [0] * 100

    # 피보나치 함수(Fibonacci Function)를 재귀함수로 구현(탑다운 다이나믹 프로그래밍)
    def fibo(x):
        global operationCnt
        
        # 종료 조건(1 혹은 2일 때 1을 반환)
        if x == 1 or x == 2:
            return 1
            
        # 이미 계산한 적 있는 문제라면 그대로 반환
        if d[x] != 0:
            return d[x]
            
        # 아직 계산하지 않은 문제라면 점화식에 따라서 피보나치 결과 반환        
        operationCnt += 1
        d[x] = fibo(x - 1) + fibo(x - 2)
        return d[x]

    print(f"피보나치 수열에서 {n}번째 수열의 값: {fibo(n)}")
    print(f"총 연산 횟수: {operationCnt}")

operationCnt = 0
def fibo_recursiveFunc(n):
    global operationCnt
    operationCnt = 0
        
    def fibo(x):
        global operationCnt
        if x == 1 or x == 2:
            return 1
        
        operationCnt += 1
        return fibo(x - 1) + fibo(x - 2)    
    
    print(f"피보나치 수열에서 {n}번째 수열의 값: {fibo(n)}")
    print(f"총 연산 횟수: {operationCnt}")
     
##############################################################################
##############################################################################
##############################################################################
## 시간 출력을 위한 함수
'''
def getCurrentTimeStr():
    currentTimeStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return f"[{currentTimeStr}]"
########################################################################################


# 최단 거리가 가장 짧은 노드의 번호를 반환하는 함수
INF = int(1e9)


# 가장 최단 거리가 짧은 노드의 번호를 반환하는 함수
def get_smallest_node(distance, visited, n):
    minNodIndex = 0
    minNodValue = INF
    
    for i in range(1, n + 1):
        # 방문하지 않았고, 현재 계산된 노드의 거리가 최솟값보다 작은 경우
        if not visited[i] and distance[i] < minNodValue:
            minNodValue = distance[i]
            minNodIndex = i
            
    return minNodIndex


# 다익스트라 코어 함수
def dextra_core(grap, start, n, distance, INF):
    # 1. 방문 여부 체크 리스트 생성
    visited = [False] * (n + 1)
    
    # 2. 시작 노드 초기화 및 방문 처리
    distance[start] = 0
    visited[start] = True
    
    # 3. 시작 노드와 직접 연결된 인접 노드들의 거리 설정
    for edge in grap[start]:
        # edge[0]: 도착 노드, edge[1]: 비용
        distance[edge[0]] = edge[1]
        
    # 4. 시작 노드를 제외한 나머지 (n - 1)개 노드에 대해 반복
    for _ in range(n - 1):
        # 방문하지 않은 노드 중 최단 거리가 가장 짧은 노드 번호 가져오기
        now = get_smallest_node(distance, visited, n)
        
        # 갈 수 있는 노드가 더 이상 없으면 종료
        if now == 0:
            break
            
        # 선택한 노드 방문 처리
        visited[now] = True
        
        # 선택한 노드(now)를 거쳐서 가는 거리 갱신
        for edge in grap[now]:
            curCost = distance[now] + edge[1]  # edge[1]: 이동 비용
            next_node = edge[0]                # edge[0]: 다음 노드
            
            if curCost < distance[next_node]:
                distance[next_node] = curCost


def dextra():
    ## 조건 및 데이터
    '''
    1. 노드의 개수와 간선의 개수 입력
    2. 시작 노드 번호 입력
    3. 간선 정보 입력
    4. 최단거리 테이블 초기화/생성
    5. 다익스트라 실행 (별도 함수로)
    '''
    # 1. 노드의 개수(n)와 간선의 개수(m) 입력
    n, m = map(int, input("노드 개수 와 간선 개수 입력: ").split())
    
    # 2. 시작 노드 번호 입력
    start = int(input("시작 노드 번호 입력: "))
    
    # 3. 간선 정보 입력받기 (인접 리스트)
    grap = [[] for _ in range(n + 1)]
    for _ in range(m):
        a, b, c = map(int, input("간선 정보(출발, 도착, 비용): ").split())
        grap[a].append((b, c))  # grap[a]에 (도착지 b, 비용 c) 저장
        
    # 4. 최단 거리 테이블 초기화
    distance = [INF] * (n + 1)
    
    # 5. 다익스트라 실행
    dextra_core(grap, start, n, distance, INF)
    
    # 결과 출력
    print(f"\n=== {start}번 노드 기준 최단 거리 결과 ===")
    for i in range(1, n + 1):
        if distance[i] == INF:
            print(f"{start}번 노드에서 {i}번 노드까지: 도달할 수 없음")
        else:
            print(f"{start}번 노드에서 {i}번 노드까지: {distance[i]}")
    #####################################################################################

####################################################################################

####################################################################################
INF = int(1e9)


def dextra_core2(grap, start, n, distance):
    # 1. 우선순위 큐(최소 힙) 생성
    q = []
    
    # 2. 시작 노드 초기화 및 큐에 삽입
    # heapq는 튜플의 첫 번째 원소를 기준으로 정렬하므로 (비용, 노드번호) 순으로 저장
    distance[start] = 0
    heapq.heappush(q, (0, start))
    
    # 3. 큐가 빌 때까지 반복 (while 문 사용)
    while q:
        # 가장 거리가 짧은 노드 정보 꺼내기
        dist, now = heapq.heappop(q)
        
        # 이미 처리된 노드(기존 기록이 더 짧은 경로)라면 건너뜁니다
        if distance[now] < dist:
            continue
            
        # 선택한 노드(now)를 거쳐서 인접 노드로 이동하는 거리 계산
        for edge in grap[now]:
            next_node = edge[0]
            cost = edge[1]
            curCost = dist + cost
            
            # 더 짧은 경로를 발견한 경우
            if curCost < distance[next_node]:
                distance[next_node] = curCost
                heapq.heappush(q, (curCost, next_node))  # 갱신된 정보 큐에 삽입
            



def dextra2():
    n, m = map(int, input("노드 개수 와 간선 개수 입력: ").split())
    start = int(input("시작 노드 번호 입력: "))
    
    grap = [[] for _ in range(n + 1)]
    for _ in range(m):
        a, b, c = map(int, input("간선 정보(출발, 도착, 비용): ").split())
        grap[a].append((b, c))
        
    distance = [INF] * (n + 1)
    
    # INF 인자는 넘길 필요도 없어집니다
    dextra_core2(grap, start, n, distance)
    dextra_priority(grap,start,n,distance,INF)
    print(f"\n=== {start}번 노드 기준 최단 거리 결과 ===")
    for i in range(1, n + 1):
        if distance[i] == INF:
            print(f"{start}번 노드에서 {i}번 노드까지: 도달할 수 없음")
        else:
            print(f"{start}번 노드에서 {i}번 노드까지: {distance[i]}")
###################################################################################








##############################################################################
## 파이선 메인 함수, 파일을 실행시키면 여기부터 실행, 이 부분은 반드시 파일의 맨 마지막에 위치해야 함
if __name__ == "__main__":
    start_time = datetime.now()
    print(getCurrentTimeStr(), "main Start..")
    
    ##############
    ## 파이선의 메인 함수를 이용해서 실행할 함수
    programStart()
    ##############
    
    finish_time = datetime.now()
    print(getCurrentTimeStr(), f"main Finish..({(finish_time - start_time).total_seconds()}s Elapsed)")
