## 기본 라이브러리 임포트
from datetime import datetime
import os
## 추가 라이브러리
from collections import deque
from random import randint


## 실행 함수
def programStart():
    print(getCurrentTimeStr(), "programStart() is started...")
    ############################################################
    ## 여기에 코드를 작성하세요.

    # stackExample()
    # queueExample()

    # recursive_function()
    # recursive_function_withFinish(95)

    # num = 0
    # print(f"반복적으로 구현한 {num}!: {factorial_iterative(num)}")
    # print(f"재귀적으로 구현한 {num}!: {factorial_recursive(num)}")

    # a = 192
    # b = 162
    # print(f"{a}와 {b}의 최대 공약수: {gcd(a, b)}")

    # dfs_example()
    # bfs_example()

    # icing()
    # maze()

    ############################################################
    print(getCurrentTimeStr(), "programStart() is finished...")

#########################################################################################
def maze():
    # N, M을 공백을 기준으로 구분하여 입력 받기
    n, m = map(int, input("미로의 세로, 가로 크기를 입력하세요: ").split())
    # 2차원 리스트의 맵 정보 입력 받기
    graph = []
    for i in range(n):
        graph.append(list(map(int, input(f"미로 인접행렬의 {i+1}번째 행 값을 입력하세요: "))))

    # 이동할 네 가지 방향 정의 (상, 하, 좌, 우)
    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]

    # BFS를 수행한 결과 출력
    print(f"탈출을 위해 움직여야 하는 최소 칸의 수: {bfs_maze(graph, dx, dy, n, m, 0, 0)}")

# BFS 소스코드 구현
def bfs_maze(graph, dx, dy, n, m, x, y):
    # 큐(Queue) 구현을 위해 deque 라이브러리 사용
    queue = deque()
    queue.append((x, y))
    # 큐가 빌 때까지 반복하기
    while queue:
        x, y = queue.popleft()
        # 현재 위치에서 4가지 방향으로의 위치 확인
        for i in range(4):
            nx = x + dx[i]
            ny = y + dy[i]
            # 미로 찾기 공간을 벗어난 경우 무시
            if nx < 0 or nx >= n or ny < 0 or ny >= m:
                continue
            # 벽인 경우 무시
            if graph[nx][ny] == 0:
                continue
            # 해당 노드를 처음 방문하는 경우에만 최단 거리 기록
            if graph[nx][ny] == 1:
                graph[nx][ny] = graph[x][y] + 1
                queue.append((nx, ny))
    # 가장 오른쪽 아래까지의 최단 거리 반환
    return graph[n - 1][m - 1]

def icing():
    # N, M을 공백을 기준으로 구분하여 입력 받기
    n, m = map(int, input("세로 길이 N과 가로 길이 M을 입력하세요: ").split())

    # 2차원 리스트의 맵 정보 입력 받기
    graph = []
    for i in range(n):
        graph.append(list(map(int, input(f"세로 {i+1}번째 행의 가로 입력: "))))

    # 모든 노드(위치)에 대하여 음료수 채우기
    result = 0
    for i in range(n):
        for j in range(m):
            # 현재 위치에서 DFS 수행
            if dfs_icing(graph, n, m, i, j) == True:
                result += 1

    print(f"얼음 조각은 총 {result}개 입니다.")  # 정답 출력

# DFS로 특정한 노드를 방문한 뒤에 연결된 모든 노드들도 방문
def dfs_icing(graph, n, m, x, y):
    # 주어진 범위를 벗어나는 경우에는 즉시 종료
    if x <= -1 or x >= n or y <= -1 or y >= m:
        return False
    # 현재 노드를 아직 방문하지 않았다면
    if graph[x][y] == 0:
        # 해당 노드 방문 처리
        graph[x][y] = 1
        # 상, 하, 좌, 우의 위치들도 모두 재귀적으로 호출
        dfs_icing(graph, n, m, x - 1, y)
        dfs_icing(graph, n, m, x, y - 1)
        dfs_icing(graph, n, m, x + 1, y)
        dfs_icing(graph, n, m, x, y + 1)
        return True
    return False


def bfs_example():
    # 각 노드가 연결된 정보를 리스트 자료형으로 표현(2차원 리스트)
    graph = [
        [],
        [2, 3, 8],
        [1, 7],
        [1, 4, 5],
        [3, 5],
        [3, 4],
        [7],
        [2, 6, 8],
        [1, 7]
    ]

    # 각 노드가 방문된 정보를 리스트 자료형으로 표현(1차원 리스트)
    visited = [False] * 9

    # 정의된 BFS 함수 호출
    print("주어진 그래프를 BFS 방식으로 탐색하는 순서입니다.")
    bfs(graph, 1, visited)
    print()

# BFS 함수 정의
def bfs(graph, start, visited):
    # 큐(Queue) 구현을 위해 deque 라이브러리 사용
    queue = deque([start])
    # 현재 노드를 방문 처리
    visited[start] = True
    # 큐가 빌 때까지 반복
    while queue:
        # 큐에서 하나의 원소를 뽑아 출력
        v = queue.popleft()
        print(v, end=' ')
        # 해당 원소와 연결된, 아직 방문하지 않은 원소들을 큐에 삽입
        for i in graph[v]:
            if not visited[i]:
                queue.append(i)
                visited[i] = True

def dfs_example():
    # 각 노드가 연결된 정보를 리스트 자료형으로 표현(2차원 리스트)
    graph = [
        [],
        [2, 3, 8],
        [1, 7],
        [1, 4, 5],
        [3, 5],
        [3, 4],
        [7],
        [2, 6, 8],
        [1, 7]
    ]

    # 각 노드가 방문된 정보를 리스트 자료형으로 표현(1차원 리스트)
    visited = [False] * 9

    # 정의된 DFS 함수 호출
    print("주어진 그래프를 DFS 방식으로 탐색하는 순서입니다.")
    dfs(graph, 1, visited)
    print()

# DFS 함수 정의
def dfs(graph, v, visited):
    # 현재 노드를 방문 처리
    visited[v] = True
    print(v, end=' ')
    # 현재 노드와 연결된 다른 노드를 재귀적으로 방문
    for i in graph[v]:
        if not visited[i]:
            dfs(graph, i, visited)


def gcd(a, b):
    if a % b == 0:
        return b
    else:
        return gcd(b, a % b)


# 반복적으로 구현한 n!
def factorial_iterative(n):
    result = 1
    # 1부터 n까지의 수를 차례대로 곱하기
    for i in range(1, n + 1):
        result *= i
    return result

# 재귀적으로 구현한 n!
def factorial_recursive(n):
    if n <= 1:  # n이 1 이하인 경우 1을 반환
        return 1
    # n! = n * (n - 1)!를 그대로 코드로 작성하기
    return n * factorial_recursive(n - 1)


def recursive_function_withFinish(i):
    # 100번째 호출을 했을 때 종료되도록 종료 조건 명시
    if i == 100:
        return
    print(i, '번째 재귀함수에서', i + 1, '번째 재귀함수를 호출합니다.')
    recursive_function_withFinish(i + 1)
    print(i, '번째 재귀함수를 종료합니다.')


def recursive_function():
    print('재귀 함수를 호출합니다.')
    recursive_function()

def queueExample():
    # 큐(Queue) 구현을 위해 deque 라이브러리 사용
    queue = deque()

    # 삽입(5) - 삽입(2) - 삽입(3) - 삽입(7) - 삭제() - 삽입(1) - 삽입(4) - 삭제()
    queue.append(5)
    queue.append(2)
    queue.append(3)
    queue.append(7)

    popData = queue.popleft()
    print(f"꺼내진(큐에서 삭제된) 데이터: {popData}")

    queue.append(1)
    queue.append(4)

    popData = queue.popleft()
    print(f"꺼내진(큐에서 삭제된) 데이터: {popData}")

    print(f"큐 내의 데이터 (들어온 순서): {queue}")  # 먼저 들어온 순서대로 출력

    queue.reverse()  # 큐의 데이터를 역순으로 바꾸기
    print(f"큐 내의 데이터 (역순으로 바뀐 형태): {queue}")  # 나중에 들어온 원소부터 출력

    popData = queue.popleft()
    print(f"꺼내진(큐에서 삭제된) 데이터: {popData}")


def stackExample():
    stack = []

    # 삽입(5) - 삽입(2) - 삽입(3) - 삽입(7) - 삭제() - 삽입(1) - 삽입(4) - 삭제()
    stack.append(5)
    stack.append(2)
    stack.append(3)
    stack.append(7)

    popData = stack.pop()
    print(f"꺼내진(스택에서 삭제된) 데이터: {popData}")

    stack.append(1)
    stack.append(4)

    popData = stack.pop()
    print(f"꺼내진(스택에서 삭제된) 데이터: {popData}")

    print(f"스택내 데이터(바닥/안쪽부터): {stack}")        # 최하단 (출입구에서 먼 가장 안쪽) 원소부터 출력
    print(f"스택내 데이터(위/바깥쪽부터): {stack[::-1]}")  # 최상단 (출입구에서 가장 가까운) 원소부터 출력


##############################################################
## 정렬 예제들
def jung():
    array = [7, 5, 9, 0, 3, 1, 6, 2, 4, 8]
    print("정렬 전:", array)

    sortedArray = array[:]  # 원본 복사해서 정렬
    for i in range(len(sortedArray)):
        min_index = i
        for j in range(i + 1, len(sortedArray)):
            if sortedArray[j] < sortedArray[min_index]:
                min_index = j
        sortedArray[i], sortedArray[min_index] = sortedArray[min_index], sortedArray[i]

    print("정렬 후:", sortedArray)
    print("뒤집은 것:", sortedArray[::-1])


def insertJung(array):
    operationCnt = 0

    for i in range(1, len(array)):
        for j in range(i, 0, -1):
            operationCnt += 1
            if array[j] < array[j - 1]:
                array[j], array[j - 1] = array[j - 1], array[j]
            else:
                break

    print(array, operationCnt)


def second():
    i = 7
    j = 9
    print(f"i={i},j={j}")
    i, j = j, i
    print(f"i={i},j={j}")

    print()


#########################################################################################
array = [7, 5, 9, 0, 3, 1, 6, 2, 4, 8]

# 옛날 버전 (카운트 없음)
def quickJung(array, start, end):
    if start >= end:
        return
    pivot = start
    left = start + 1
    right = end
    while left <= right:
        while left <= end and array[left] <= array[pivot]:
            left += 1
        while right > start and array[right] >= array[pivot]:
            right -= 1
        if left > right:
            array[right], array[pivot] = array[pivot], array[right]
        else:
            array[left], array[right] = array[right], array[left]
    quickJung(array, start, right - 1)
    quickJung(array, right + 1, end)

# 2 버전 (operCnt 포함)
def quickJung2(array):
    print("정렬 전:", array)

    def quickSort2(start, end):
        if start >= end:
            return 0
        operCnt = 0
        pivot = start
        left = start + 1
        right = end
        while left <= right:
            operCnt += 1
            while left <= end and array[left] <= array[pivot]:
                operCnt += 1
                left += 1
            while right > start and array[right] >= array[pivot]:
                operCnt += 1
                right -= 1
            if left > right:
                array[right], array[pivot] = array[pivot], array[right]
            else:
                array[left], array[right] = array[right], array[left]
        operCnt += quickSort2(start, right - 1)
        operCnt += quickSort2(right + 1, end)
        return operCnt

    cnt = quickSort2(0, len(array) - 1)
    print("정렬 후:", array)
    print("연산횟수:", cnt)


def psort(array):
    if len(array) <= 1:
        return array
    pivot = array[0]
    tail = array[1:]
    left_side = [x for x in tail if x <= pivot]
    right_side = [x for x in tail if x > pivot]
    return psort(left_side) + [pivot] + psort(right_side)


def CountJung():
    ary = [7, 5, 9, 0, 3, 1, 6, 2, 9, 1, 4, 8, 0, 5, 2]
    ct = [0] * (max(ary) + 1)
    for i in range(len(ary)):
        ct[ary[i]] += 1
    for i in range(len(ct)):
        for j in range(ct[i]):
            print(i, end='')


def CountJung2(array):
    print("정렬 전:", array)
    opCt = 0
    stAry = []
    Clst = [0] * (max(array) + 1)

    for data in array:
        opCt += 1
        Clst[data] += 1

    for i in range(len(Clst)):
        for j in range(Clst[i]):
            opCt += 1
            stAry.append(i)

    print("정렬 후:", stAry)
    print("연산횟수:", opCt)
    return stAry, opCt


def STC():
    ary = []
    for _ in range(10000000):
        ary.append(randint(1, 100))


def ABChan():
    n, k = map(int, input().split())
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))
    a.sort()
    b.sort(reverse=True)
    for i in range(k):
        if a[i] < b[i]:
            a[i], b[i] = b[i], a[i]
        else:
            break
    print(sum(a))


#########################################################################################
##############################################################################
## 시간 출력을 위한 함수
def getCurrentTimeStr():
    currentTimeStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return f"[{currentTimeStr}]"

##############################################################################
## 파이선 메인 함수, 파일을 실행시키면 여기부터 실행, 이 부분은 반드시 파일의 맨 마지막에 위치해야 함
if __name__ == "__main__":
    start_time = datetime.now()
    print(getCurrentTimeStr(), "main Start..")

    ##############
    ## 파이선의 메인 함수를 이용해서 실행할 함수
    #programStart()
    ##############
    #jung()
    #second()
    #insertJung([7, 5, 9, 0, 3, 1, 6, 2, 4, 8])
    #quickJung2(array.copy())
    #quickJung(array, 0, len(array) - 1)
    #print(psort(array))
    #CountJung()
    #CountJung2([7, 5, 9, 0, 3, 1, 6, 2, 9, 1, 4, 8, 0, 5, 2])
    ABChan()
    finish_time = datetime.now()
    print(getCurrentTimeStr(), f"main Finish..({(finish_time - start_time).total_seconds()}s Elapsed)")