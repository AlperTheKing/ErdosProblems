"""Test whether the DICHOTOMY's 'absolute margin' lead is viable: can a NON-C5-colorable triangle-free graph have
beta/N^2 arbitrarily close to 1/25? Construction: C5[t] blow-up (C5-colorable, beta=t^2, N=5t) bridged to a Grotzsch
gadget (non-C5-colorable). The whole graph is non-C5-colorable (contains Grotzsch) and triangle-free; beta=t^2+4.
If beta/N^2 -> 1/25, the margin-dichotomy (non-C5-colorable => beta < N^2/25 - absolute_margin) is DEAD."""
from fractions import Fraction as F
from _h import maxcut_all
from _bdef_construct import mycielski, Cn, union_disjoint

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

def beta_of(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj)
    mc=max(sum(1 for x,y in E if s[x]!=s[y]) for s in cuts)
    return len(E)-mc

def trifree(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

print("C5[t] (+ Grotzsch gadget bridged) -- non-C5-colorable, triangle-free, beta vs N^2/25:")
grot=mycielski(5,Cn(5))  # (11, edges)
for t in (1,2,3):
    n1,E1=blowup([t]*5)
    n,E=union_disjoint((n1,E1),grot)
    E=E+[(0,n1)]  # bridge C5[t] vertex 0 to Grotzsch vertex 0 (a cut edge)
    b=beta_of(n,E); cap=F(n*n,25)
    print("  t=%d: N=%d e=%d beta=%d  N^2/25=%s=%.2f  beta<=N^2/25:%s  beta/N^2=%.4f (limit 1/25=0.04)  tri-free=%s margin=%.2f"%(
        t,n,len(E),b,str(cap),float(cap),b<=cap,b/(n*n),trifree(n,E),float(cap)-b))
# asymptotic via formula beta=t^2+4, N=5t+11
print("  asymptotic (beta=t^2+4, N=5t+11):")
for t in (20,100,1000):
    N=5*t+11; b=t*t+4; cap=F(N*N,25)
    print("    t=%d: N=%d beta=%d N^2/25=%.1f beta/N^2=%.5f abs_margin=N^2/25-beta=%.2f rel_margin=%.5f"%(
        t,N,b,float(cap),b/(N*N),float(cap)-b,(float(cap)-b)/(N*N)))
