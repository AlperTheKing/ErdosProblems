import random

def feasible(a,b,e,d,R,f):
    c=e+R; x=d+e; v=a*e+f*x-x*x; u=x-v
    return min(a,b,e,d,f)>=1 and R>0 and v>=1 and u>=1 and e>=v and b+c-x-1>=-1e-9
for i in range(100000):
    e=random.uniform(1,5); R=random.uniform(0.01,5); d=random.uniform(1,5); f=random.uniform(1,5); b=1
    x=d+e
    lo=(1 - f*x+x*x)/e; hi=(min(e,x-1)-f*x+x*x)/e
    lo=max(lo,1)
    if hi<lo: continue
    a=random.uniform(lo,hi)
    if feasible(a,b,e,d,R,f):
        print('feas', (a,b,e,d,R,f), 's3', b+R-d); break
else: print('none')
