"""Best-t distribution for the SPLIT certificate on large odd-cycle blow-ups: does the winning split point t
   cluster (e.g. t=1)? If so the SPLIT proof collapses to two fixed band bounds."""
import random
from fractions import Fraction as F
from _split_verify import split_quotient

def best_ts(m, n):
    N=sum(n)
    prods=[(n[i]*n[(i+1)%m],i) for i in range(m)]; pmin,a=min(prods); b=(a+1)%m; nbad=n[a]*n[b]
    def Pi(i):
        if i==a: return F(n[b])
        if i==b: return F(n[a])
        return F(nbad,n[i])
    order=[(a-k)%m for k in range(m)]; A=[Pi(order[i]) for i in range(m)]; L=m; mm=(L-1)//2
    good=[]
    for t in range(1,mm+1):
        out=sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L))
        cen=sum(A[i] for i in range(t,L-t))
        if out<=F(2*t*N,L) and cen<=F((L-2*t)*N,L): good.append(t)
    return good

if __name__=="__main__":
    rng=random.Random(99)
    for m in (5,7,9,11,13):
        hist={}; t1ok=0; tot=0; nogood=0
        for _ in range(80000):
            n=[rng.choice([1,2,3,5,7,12,30,100,300,700,1500]) for _ in range(m)]
            if sum(n)>4000 or sum(n)<m: continue
            g=best_ts(m,n); tot+=1
            if not g: nogood+=1; continue
            if 1 in g: t1ok+=1
            hist[g[0]]=hist.get(g[0],0)+1
        pct=round(100*t1ok/tot,1) if tot else 0
        print(f"C{m}: tested={tot} t=1-works={t1ok} ({pct}%) no-good-t={nogood} smallest-winning-t hist={dict(sorted(hist.items()))}",flush=True)
