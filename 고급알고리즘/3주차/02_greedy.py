## 기본 라이브러리 임포트
from datetime import datetime
import os
## 추가 라이브러리


# -*- coding: utf-8 -*-


## 실행 함수
def programStart():
    print(getCurrentTimeStr(), "programStart() is started...")
    ############################################################
    ## 여기에 코드를 작성하세요.

    # getChangeCnt()
    
    # getMinimumCalcCnt()
    # getMinimumCalcCnt_1()
    # getMinimumCalcCnt_2()
    
    # adventureGuild()
    # multiplyOrDevide()

    ############################################################
    print(getCurrentTimeStr(), "programStart() is finished...")

#########################################################################################
#########################################################################################
#########################################################################################
def multiplyOrDevide():
    data = input("여러개의 숫자로 이루어진 문자열을 입력하세요: ")

    # 첫 번째 문자를 숫자로 변경하여 대입
    result = int(data[0])

    for i in range(1, len(data)):
        # 두 수 중에서 하나라도 '0' 혹은 '1'인 경우, 곱하기보다는 더하기 수행
        num = int(data[i])
        if num <= 1 or result <= 1:
            result += num
        else:
            result *= num

    print(f"더하기나 곱하기로 만들 수 있는 가장 큰 숫자 = {result}")


def adventureGuild():
    n = int(input("모험가의 수를 입력하세요: "))
    data = list(map(int, input(f"모험가 {n} 명의 공포도를 입력하세요: ").split()))
    data.sort()

    result = 0 # 총 그룹의 수
    count = 0 # 현재 그룹에 포함된 모험가의 수

    for i in data: # 공포도를 낮은 것부터 하나씩 확인하며
        count += 1 # 현재 그룹에 해당 모험가를 포함시키기
        if count >= i: # 현재 그룹에 포함된 모험가의 수가 현재의 공포도 이상이라면, 그룹 결성
            result += 1 # 총 그룹의 수 증가시키기
            count = 0 # 현재 그룹에 포함된 모험가의 수 초기화

    print(f"여행을 떠날 수 있는 최대 그룹의 수 = {result}") # 총 그룹의 수 출력

## While문 최소 한번 더 줄이기
def getMinimumCalcCnt_2():
    # N, K공백을 기준으로 구분하여 입력 받기
    n, k = map(int, input("n과 k를 입력하세요: ").split())

    result = 0

    # N이 K보다 작은 경우, 최초부터 while 문을 실행하지 않음 
    while n >= k:
        # N이 K로 나누어 떨어지는 수가 될 때까지만 1씩 빼기
        target = (n // k) * k
        result += (n - target)
        n = target
        
        n //= k
        result += 1

    # 마지막으로 남은 수에 대하여 1씩 빼기
    result += (n - 1)
    print(f"수행해야 하는 횟수의 최솟값 = {result}")

## K의 배수만큼 미리 빼기
def getMinimumCalcCnt_1():
    # N, K공백을 기준으로 구분하여 입력 받기
    n, k = map(int, input("n과 k를 입력하세요: ").split())

    result = 0

    while True:
        # N이 K로 나누어 떨어지는 수가 될 때까지만 1씩 빼기
        target = (n // k) * k
        result += (n - target)
        n = target
        
        # N이 K보다 작을 때 (더 이상 나눌 수 없을 때) 반복문 탈출
        if n < k:
            break
        
        # K로 나누기
        n //= k
        result += 1        

    # 마지막으로 남은 수에 대하여 1씩 빼기
    result += (n - 1)
    print(f"수행해야 하는 횟수의 최솟값 = {result}")


def getMinimumCalcCnt():
    n, k = map(int, input("n과 k를 입력하세요: ").split())
    
    result = 0
        
    # N이 K 이상이라면 K로 계속 나누기
    while n >= k:
        # N이 K로 나누어 떨어지지 않는다면 N에서 1씩 빼기
        while n % k != 0:
            n -= 1
            result += 1
        
        # K로 나누기
        n //= k
        result += 1

    # 마지막으로 남은 수에 대하여 1씩 빼기
    while n > 1:
        n -= 1
        result += 1

    print(f"수행해야 하는 횟수의 최솟값 = {result}")


def getChangeCnt():
    n = 1260
    count = 0
    
    array = [500, 100, 50, 10]
    
    for coin in array:
        count = count + (n // coin)
        n = n % coin
    
    print(f"거슬러 줘야 할 동전의 최소 갯수 = {count}회")

#########################################################################################
#########################################################################################
#########################################################################################
##############################################################################
## 시간 출력을 위한 함수
def getCurrentTimeStr():
    currentTimeStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return f"[{currentTimeStr}]"

##############################################################################
## 파이선 메인 함수, 파일을 실행시키면 여기부터 실행, 이 부분은 반드시 파일의 맨 마지막에 위치해야 함

def twoDExample():

    for i in range(5):
        for j in range(5):
            print(f"({i},{j})", end=" ")
        print()
    
    
    area=["동","북","서","남"]
    dx=[0,-1,0,1]
    dy=[1,0,-1,0]
    x,y=2,2
    for i in range(len(dx)):
        nx=x+dx[i]
        ny=y+dy[i]
        print(f"{area[i]}({nx},{ny})")
  

def udlr():
    n= int(input("맵크기/n"))
    x,y=1,1
    plans=input("방향").split()
    dx=[0,0,-1,1]
    dy=[-1,1,0,0]
    move_types=['l','r','u','d']
    for plan in plans:
        for i in range(len(move_types)):
            if plan==move_types[i]:
                nx=x+dx[i]
                ny=y+dy[i]
        if nx <1 or ny <1 or nx >n or ny >n:
            continue
        x,y=nx,ny
        
    print(f"최종위치는{x},{y}")
  
  
def sight():
    h= int(input())
    count=0
    checkNum=3
    for i in range(h+1):
        for j in range(60):
            for k in range(60):
                #if '3' in str(i)+str(j)+str(k):
                if str(checkNum) in str(i)+str(j)+str(k):
                    count+=1
    print(count)

def knight():
    input_data=input()
    row=int(input_data[1])
    
    column=int(ord(input_data[0]))-int(ord('a'))+1
    steps=[(-2,-1),(-1,-2),(1,-2),(2,-1),(2,1),(1,2),(-1,2),(-2,1)]
    
    result=0
    for step in steps:
        next_row=row + step[0]
        next_column=column+step[1]
        if next_row >= 1 and next_row<=8 and next_column >= 1 and next_column <=8:
            result +=1
            
    print(result)


def sort():
 #   sentence=str.input().split()
  #  for i in range(len(sentence)):
    data=input("대문자와 숫자만 입력")
    result=[]
    value=0
    for x in data:
        if x.isalpha():
            result.append(x)
        elif x.isdigit():
            result.append(x)
            value += int(x)
        else:
            print(f"{x}넣으라고 한것만 넣으라고")
            
            
    result.sort()
    if value !=0:
        result.append(str(value))
    print(''.join(result))




if __name__ == "__main__":
    start_time = datetime.now()
    print(getCurrentTimeStr(), "main Start..")
    
    ##############
    ## 파이선의 메인 함수를 이용해서 실행할 함수
    #programStart()
    ##############
    #twoDExample()
    #udlr()
    #sight()
    
    #knight()
    sort()
    finish_time = datetime.now()
    print(getCurrentTimeStr(), f"main Finish..({(finish_time - start_time).total_seconds()}s Elapsed)")
