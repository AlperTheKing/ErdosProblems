"""Probe the t=1 band inequality OUT_1 = S(a)+S(b) <= 2N/ell (the clean core of (P1)).
Find blow-ups where t=1 FAILS and report the min rescuing t and the layer-load profile A, to understand
what structure forces a larger band. Quotient level (exact)."""
import random
from fractions import Fraction as F

def profile(m, n):
    N=sum(n)
    prods=[(n[i]*n[(i+1)%m],i) for i in range(m)]; pmin,a=min(prods); b=(a+1)%m; nbad=n[a]*n[b]
    def Pi(i):
        if i==a: return F(n[b])
        if i==b: return F(n[a])
        return F(nbad,n[i])
    order=[(a-k)%m for k in range(m)]; A=[Pi(order[i]) for i in range(m)]; L=m; mm=(L-1)//2
    R=sum(A)-F(N)   # = ROWSUM - N (should be <=0 if ROWSUM-O holds)
    bands=[]
    for t in range(1,mm+1):
        out=sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L))
        cen=sum(A[i] for i in range(t,L-t))
        bands.append((t, out<=F(2*t*N,L) and cen<=F((L-2*t)*N,L), out-F(2*t*N,L)))
    t1=bands[0][1]
    win=[t for t,ok,_ in bands if ok]
    return N,L,A,R,t1,win,bands

if __name__=="__main__":
    rng=random.Random(7)
    print("=== t=1 band failures on overloaded blow-ups (quotient, exact) ===",flush=True)
    for m in (5,7,9,11,13):
        t1fail=0; rowsum_viol=0; nogood=0; examples=[]
        for _ in range(120000):
            n=[rng.choice([1,2,3,5,7,12,30,100,300,700,1500]) for _ in range(m)]
            if sum(n)>4000 or sum(n)<m: continue
            N,L,A,R,t1,win,bands=profile(m,n)
            if R>0: rowsum_viol+=1   # ROWSUM-O itself violated (should never happen)
            if not win: nogood+=1
            if not t1:
                t1fail+=1
                if len(examples)<3: examples.append((n,N,[str(x) for x in A],str(R),win))
        print(f"C{m}: t1-FAILS={t1fail} ROWSUM-viol={rowsum_viol} no-winning-t={nogood}",flush=True)
        for ex in examples:
            print(f"    n={ex[0]} N={ex[1]} A={ex[2]} R={ex[3]} winning-t={ex[4]}",flush=True)
