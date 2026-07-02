import random, math

def phi_s6(a,b,c,d,e,f):
    x=d+e; y=1
    v=a*c+d*f+e*f-x*x
    u=x-v
    S=a+b+c+d+e+f
    m=x*x+v
    N=S+y+x+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(N*N-25*m)-75*(x*x*A/Z+v*B/(e*Y)-S)

def feasible(a,b,c,d,e,f):
    x=d+e
    v=a*c+d*f+e*f-x*x
    u=x-v
    return e>c and v>=1 and u>=1 and e>=v and b+c-x-1>=0 and min(a,b,c,d,e,f)>=1

for i in range(20000):
    # construct random feasible-ish by choosing c,d,e,f then solve a range
    c=random.uniform(1,4); r=random.uniform(0.01,4); e=c+r; d=random.uniform(1,4); f=random.uniform(1,4)
    x=d+e
    # v=ac+f*x-x^2, need 1<=v<=min(e,x-1); choose a in interval
    lo=(1 - f*x + x*x)/c
    hi=(min(e,x-1)- f*x + x*x)/c
    lo=max(lo,1)
    if hi<lo: continue
    a=random.uniform(lo,hi)
    b=random.uniform(max(1,d+e+1-c), max(1,d+e+1-c)+5)
    if not feasible(a,b,c,d,e,f): continue
    eps=1e-5*(1+b)
    der=(phi_s6(a,b+eps,c,d,e,f)-phi_s6(a,b,c,d,e,f))/eps
    if der <= -1e-6:
        print('NEG',der,(a,b,c,d,e,f),'phi',phi_s6(a,b,c,d,e,f)); break
else:
    print('no negative d/db sample')
