
## 기본 라이브러리 임포트
from datetime import datetime
import os

## 추가 라이브러리
from random import randint
import time
from bisect import bisect_left,bisect_right

####################################
## 실행 함수
def programStart():
    print(getCurrentTimeStr(), "programStart() is started...")

    ############################################################
    ## 여기에 코드를 작성하세요.

    ############################################################
    print(getCurrentTimeStr(), "programStart() is finished...")


#########################################################################################
def listItemSwap():
    n, k = map(int, input("데이터의 갯수와 바꿔치기 가능 횟수를 입력하세요: ").split())

    a = list(map(int, input("배열 A의 모든 원소를 입력하세요: ").split()))
    b = list(map(int, input("배열 B의 모든 원소를 입력하세요: ").split()))

    a.sort()
    b.sort(reverse=True)

    for i in range(k):
        if a[i] < b[i]:
            a[i], b[i] = b[i], a[i]
        else:
            break

    print(f"배열 A의 모든 원소의 합의 최대값: {sum(a)}")


####################################
def sortTimeCompare():
    array = []

    for _ in range(10000):
        array.append(randint(1, 100))

    start_time = time.time()
    selectionSort(array.copy())
    end_time = time.time()
    print("선택 정렬 성능 측정:", end_time - start_time)

    start_time = time.time()
    array.sort()
    end_time = time.time()
    print("리스트 내 기본 정렬 성능 측정:", end_time - start_time)


#####################################
def countSort(array):
    operationCnt = 0

    countMap = [0] * (max(array) + 1)
    sortedArray = []

    for i in range(len(array)):
        operationCnt += 1
        countMap[array[i]] += 1

    for i in range(len(countMap)):
        operationCnt += 1
        for j in range(countMap[i]):
            sortedArray.append(i)

    return sortedArray, operationCnt


####################################
def quickSort_py(array):

    def quick_sort(array):
        if len(array) <= 1:
            return array

        pivot = array[0]
        tail = array[1:]

        left_side = [x for x in tail if x <= pivot]
        right_side = [x for x in tail if x > pivot]

        return quick_sort(left_side) + [pivot] + quick_sort(right_side)

    return quick_sort(array), None


####################################
def quickSort(array):
    operationCnt = 0

    def quick_sort(array, start, end):
        operationCnt = 0

        if start >= end:
            return 0

        pivot = start
        left = start + 1
        right = end

        while left <= right:
            operationCnt += 1

            while left <= end and array[left] <= array[pivot]:
                operationCnt += 1
                left += 1

            while right > start and array[right] >= array[pivot]:
                operationCnt += 1
                right -= 1

            if left > right:
                array[right], array[pivot] = array[pivot], array[right]
            else:
                array[left], array[right] = array[right], array[left]

        operationCnt += quick_sort(array, start, right - 1)
        operationCnt += quick_sort(array, right + 1, end)

        return operationCnt

    operationCnt += quick_sort(array, 0, len(array) - 1)

    return array, operationCnt


####################################
def insertionSort(array):
    operationCnt = 0

    for i in range(1, len(array)):
        for j in range(i, 0, -1):
            operationCnt += 1

            if array[j] < array[j - 1]:
                array[j], array[j - 1] = array[j - 1], array[j]
            else:
                break

    return array, operationCnt


####################################
def selectionSort(array):
    operationCnt = 0

    for i in range(len(array)):
        min_index = i

        for j in range(i + 1, len(array)):
            operationCnt += 1

            if array[min_index] > array[j]:
                min_index = j

        array[i], array[min_index] = array[min_index], array[i]

    return array, operationCnt


####################################
## 시간 출력을 위한 함수
def getCurrentTimeStr():
    currentTimeStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return f"[{currentTimeStr}]"


##############################################################################
def b_s():
    n, target = list(map(int, input().split()))

    array = list(map(int, input().split()))

    def binary_search(array, target, st, ed):
        if st > ed:
            return None

        mid = (st + ed) // 2

        if array[mid] == target:
            return mid

        elif array[mid] > target:
            return binary_search(array, target, st, mid - 1)

        else:
            return binary_search(array, target, mid + 1, ed)

    result = binary_search(array, target, 0, n - 1)

    if result is None:
        print("원소엄슴")
    else:
        print(result + 1)
######################################################################
def dduck():
    n, target = list(map(int, input().split()))
    array = list(map(int, input().split()))

    start = 0
    end = max(array)

    while start <= end:
        mid = (start + end) // 2

        allLength = 0

        for i in range(n):
            if array[i] > mid:
                allLength += array[i] - mid

        if allLength >= target:
            start = mid + 1
        else:
            end = mid - 1

    print(end)
##떡 시험에나올거같음
###def countNum():
  #  #요건입력,데이터리스트길이n,찾는숫자x,데이터리스트 입력받기
   # #x출현횟수=가장큰x-가장 작은 인덱스
  ##  n,x=map(int,input("데이터길이와 찾는숫자 한칸띄어서").split())
   # minIndx=bisect_left(array,x)
  ##  maxIndx=bisect_right(array,x)
   # xCnt=maxIndx-minIndx
  #  #x중 가장 큰인덱스 구하기x중 가장 작은인덱스 구하기
   # if xCnt==0:
   #     print("-1")
  #  else:
 #       print(f"{n}중에서{x}는{xCnt}")###
###

def countNum():
    n, x = map(int, input().split())
    arr = list(map(int, input().split()))

    left = bisect_left(arr, x)
    right = bisect_right(arr, x)

    count = right - left

    if count == 0:
        print(-1)
    else:
        print(count)




            
        
    
#########################################################################
## 파이선 메인 함수
## 파일을 실행시키면 여기부터 실행
## 이 부분은 반드시 파일의 맨 마지막에 위치해야 함

if __name__ == "__main__":
    start_time = datetime.now()
    print(getCurrentTimeStr(), "main Start..")

    ##############
    ## 파이선의 메인 함수를 이용해서 실행할 함수
    #programStart()
    #b_s()
    #dduck()
    countNum()
    ##############

    finish_time = datetime.now()
    print(
        getCurrentTimeStr(),
        f"main Finish..({(finish_time - start_time).total_seconds()}s Elapsed)"
    )

