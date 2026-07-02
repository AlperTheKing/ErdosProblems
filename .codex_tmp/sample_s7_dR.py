import random

def feasible(a,b,e,d,R,f):
    c=e+R; x=d+e; v=a*e+f*x-x*x; u=x-v
    return min(a,b,e,d,f)>=1 and R>0 and v>=1 and u>=1 and e>=v and b+c-x-1>=0
cnt=0
for i in range(100000):
    e=random.uniform(1,5); R=random.uniform(0.01,5); d=random.uniform(1,min(R,5)) if R>1 else random.uniform(1,5)
    f=random.uniform(1,5); x=d+e
    lo=(1 - f*x + x*x)/e
    hi=(min(e,x-1)-f*x+x*x)/e
    lo=max(lo,1)
    if hi<lo: continue
    a=random.uniform(lo,hi)
    b=random.uniform(max(1,d+1-R), max(1,d+1-R)+5)
    if feasible(a,b,e,d,R,f) and d<R:
        print('found d<R', (a,b,e,d,R,f), 's3', b+R-d-1); break
else:
    print('none')
