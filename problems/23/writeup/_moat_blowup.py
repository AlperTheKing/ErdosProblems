"""Test generalized CROSS / MOAT on odd-cycle blow-ups and Mycielskians (the standing gate),
including the multi-geodesic-heavy regime. For each gamma-min cut compute, for every bad edge f:
   ROW = <p_f,S>,  self=<p_f,p_f>,  cross=ROW-self,  and check ROW<=N and cross<=N-self.
Report worst margins and whether worst edge is single- or multi-geodesic."""
from fractions import Fraction as F
from _h import dec
from _stark1 import gmins
from _corridor import cut_S
from _bdef_construct import Cn, mycielski, is_triangle_free

def blow(m, t):
    """uniform C_m blow-up, parts size t."""
    n=m*t; E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(t):
            for b in range(t):
                E.append((i*t+a, j*t+b))
    return n,E

def worst(g6=None, n=None, E=None):
    if g6 is not None: n,E=dec(g6)
    adj2,cuts=gmins(n,E)
    wROW=None; wMOAT=None
    for ci,s in enumerate(cuts):
        r=cut_S(n,adj2,s)
        if r is None: continue
        M,ell,S,pf,cyc=r
        for f in M:
            self_=sum(pv*pv for pv in pf[f].values())
            ROW=sum(pv*S[v] for v,pv in pf[f].items())
            ng=len(cyc[f])
            moat_margin=F(n)-self_-(ROW-self_)  # == N-ROW
            if wROW is None or ROW>wROW[0]: wROW=(ROW,ci,f,ng,self_)
            if wMOAT is None or moat_margin<wMOAT[0]: wMOAT=(moat_margin,ci,f,ng)
    return n,wROW,wMOAT

if __name__=="__main__":
    print("=== MOAT / ROWSUM on blow-ups & Mycielskians ===")
    tests=[]
    for m in [5,7,9,11,13]:
        for t in [2,3,4]:
            tests.append((f"C{m}[{t}]", blow(m,t)))
    # non-uniform-ish via larger t
    g=mycielski(5,Cn(5)); tests.append(("Grotzsch=N11",(g[0],g[1])))
    g2=mycielski(*g); tests.append(("Myc2(C5)=N23",(g2[0],g2[1])))
    g3=mycielski(7,Cn(7)); tests.append(("Myc(C7)=N15",(g3[0],g3[1])))
    for nm,(n,E) in tests:
        if not is_triangle_free(n,E):
            print(f"  {nm}: NOT triangle-free, skip"); continue
        nn,wROW,wMOAT=worst(n=n,E=E)
        ng="single" if wROW[3]==1 else f"multi({wROW[3]})"
        print(f"  {nm} N={nn}: worstROW={float(wROW[0]):.3f} ({ng}) margin N-ROW={float(F(nn)-wROW[0]):.3f}  worstMOATmargin={float(wMOAT[0]):.3f} ({'single' if wMOAT[3]==1 else 'multi'})",flush=True)
