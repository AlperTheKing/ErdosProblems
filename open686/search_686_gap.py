import math
MODS=[1000000007,1000000009]
LOG25=math.log(25.0)

def log_ratio(k,n,d):
    s=0.0
    for i in range(1,k+1):
        s += math.log(n+d+i) - math.log(n+i)
    return s

def prod_mod(k,x,p):
    r=1; xm=x%p
    for i in range(1,k+1): r=(r*((xm+i)%p))%p
    return r

def prod(k,x):
    r=1
    for i in range(1,k+1): r*=x+i
    return r

def exact(k,n,d):
    m=n+d
    for p in MODS:
        if prod_mod(k,m,p)!=(25*prod_mod(k,n,p))%p: return False
    return prod(k,m)==25*prod(k,n)

def candidate_n(k,d):
    # R(n) decreases; find n with log R near log25
    if log_ratio(k,0,d) < LOG25: return []
    lo=0; hi=1
    while log_ratio(k,hi,d) > LOG25:
        hi*=2
        if hi>10**14: return []
    while lo+1<hi:
        mid=(lo+hi)//2
        if log_ratio(k,mid,d) > LOG25: lo=mid
        else: hi=mid
    return range(max(0,lo-3), hi+4)

checked=0
for k in range(301,2001):
    for mult in range(1,6):
        for off in range(0,k,max(1,k//20)):
            d=mult*k+off
            if d<k: continue
            for n in candidate_n(k,d):
                checked+=1
                if exact(k,n,d):
                    print('HIT',k,n,n+d,'d',d,flush=True); raise SystemExit
    if k%100==0: print('gap completed k',k,'checked',checked,flush=True)
print('NO_HIT_GAP 301 2000 d<=6k checked',checked,flush=True)
