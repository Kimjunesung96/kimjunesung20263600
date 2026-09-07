from datetime import datetime

def programstart():
    print("this function is core")
   # getChangeCnt()
    #getMinimumCalcnCnt()
    #adventureGuild()
    multiplyOrPlus()
def getCurrentTimeStr():
    currentTimeStr=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    return "["+currentTimeStr+"]"

def getChangeCnt():
    n=1260
    count=0
    array=[500,100,50,10]
    for coin in array:
        count += n//coin
        n=n%coin
    
    print(f"your coin number is{count}")

def getMinimumCalcnCnt():
    N,K=map(int,input("n space k").split())
    count = 0

    #while N != 1:
#        if N % K == 0:
 #           N = N // K
  #      else:
   ###   print(N)

    while N > K:
        target = (N // K) * K
        count += N - target      
        count += 1               
        N = N // K

    count += N - 1                

    print("총 횟수:", count)

def adventureGuild():
    n= int(input("how many adventurer?"))
    data=list(map(int,input(f"input adventurer's fear").split()))
    data.sort()
    restult=0
    count=0
    for i in data:
        count +=1
        if count >=i :
            restult += 1
            count=0
    print(f"maximum groupNum{restult}")

def multiplyOrPlus():
    numStr=input("number of string")
    result=int(numStr[0])
    #"02984"
    for i in range(1,len(numStr)):
        n=int(numStr[i])
        # 연산해야할 두개의 숫자중 1개라도 0/1 이면(1보다 작거나 같으면)
        #그렇지 않으면 곱하고
        if (n <= 1) or (result <= 1):
            result +=n
        else:
            result=result*n
    print(result)






if __name__ == "__main__":
    start_time = datetime.now()  # 현재시간확인해서 시작시간으로 저장
    print(getCurrentTimeStr(),"this is main start")

    programstart()
    
    end_time = datetime.now()  # 현재시간 확인해서 종료시간으로 저장
    print(getCurrentTimeStr(),"this is main finish")
    
    print(getCurrentTimeStr(),f"Total={end_time-start_time}")
