t=0
array=[2,3,1,2,2]

for i in range(1,5):
    if i<4:
        if array[i]>array[i+1]:
            t=array[i+1]
            array[i+1]=array[i]
            array[i]=t
            print(array)