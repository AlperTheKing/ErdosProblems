import subprocess
from fractions import Fraction
from census_GPI import dec, maxcut_all, gmin, geos, GENG
out=open('_between_out.txt','w')
def W(s): out.write(s+"\n")
# For the argmax vertex w in the RIGID case Gamma=N^2 (odd-cycle blowups), verify p_f(w) structure:
# In C_{2k+1}[t]: each vertex is in one of 2k+1 classes. Bad edges all within... actually let's just
# verify the EQUALITY-CASE claim computationally on the Gamma=N^2 family and a key SOFT bound:
#   T(w) <= sum_{f in M_w} ell(f) * p_f(w)   (equality, def)
#   and the COARSE per-vertex:  T(w) <= max_f ell(f) * |{f: w in cycle}| ... no.
#
# Test the SHARP per-vertex inequality that the rigid case saturates:
#   For every vertex w:   sum_{f in M} ell(f) p_f(w)  <=  N  +  sum_{f in M}( ell(f) p_f(w) - ell(f)^2/N )_+ ??? 
# Too speculative. Instead, directly test whether the following "local Gamma" bound holds EXACTLY:
#   Define Gamma_w = sum_f ell(f)^2 p_f(w)  (the w-weighted mass).  Is  T(w) <= N + (N^2 - Gamma)  
#   provable from  T(w)^2 <= (sum_f ell p_f) and Gamma_w? 
# Empirically: relationship between T(w), Gamma_w, and the bound.
def analyze(g6):
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[Fraction(0) for _ in range(n)]
    Gw=[Fraction(0) for _ in range(n)]   # sum_f ell^2 p_f(w)
    for (u,v) in M:
        Ps=geos(adj,side,u,v); nf=len(Ps)
        cnt={}
        for P in Ps:
            for w in set(P): cnt[w]=cnt.get(w,0)+1
        h=ell[(u,v)]
        for w,c in cnt.items():
            pf=Fraction(c,nf)
            T[w]+=h*pf
            Gw[w]+=h*h*pf
    n2=n*n; bound=n+(n2-G)
    # test:  T(w) + (Gamma - Gw(w))/??? 
    # Key candidate: T(w) <= 2N - Gw(w)/T(w)*... 
    # Test simple:  Gw(w) <= N * T(w)  ?  (i.e. ell-weighted-avg of ell over w's cycles <= N)
    okA=all(Gw[w] <= n*T[w] for w in range(n) if T[w]>0)
    # and  T(w) <= 2N - Gw(w)/N ?  (power mean: since Gw=sum ell^2 p, T=sum ell p; by ell<=? )
    candB=[2*n - Fraction(Gw[w], n) for w in range(n)]
    okB=all(T[w] <= candB[w] for w in range(n))
    return n,G,bound,max(T),okA,okB
W("test A: Gw(w)<=N*T(w) [ell-wtd avg ell <= N];  test B: T(w) <= 2N - Gw(w)/N")
for N in [8,9,10]:
    res=subprocess.run([GENG,"-tc",str(N)],capture_output=True,text=True).stdout.split()
    failA=0; failB=0; tot=0; worstB=None
    for g6 in res:
        a=analyze(g6)
        if a is None: continue
        n,G,bound,maxT,okA,okB=a; tot+=1
        if not okA: failA+=1
        if not okB: failB+=1
    W(f"N={N}: tot={tot} failA(Gw<=N*T)={failA} failB(T<=2N-Gw/N)={failB}")
out.close()
