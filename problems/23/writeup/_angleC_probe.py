"""ANGLE C probe: explicit capacitary potential for (GCD)  H = L_omega + diag(N-T) >= 0.
Energy E(x) = sum_e omega(e)(x_u-x_v)^2 + sum_v (N-T(v)) x_v^2.

Per-bad-edge decomposition idea. Recall:
  T(v) = sum_f ell(f) p_f(v).
  omega(e) = sum_f a_bar(ell(f)) tau_f(e),  with tau_f(f)=1, tau_f(B-edge)=Pr[e in C(f,Q)].
So we can split BOTH the Dirichlet energy and the diagonal additively over bad edges f:
  E(x) = sum_f [ a_bar(ell_f) * Dir_f(x)  -  ell_f * sum_v p_f(v) x_v^2 ]  +  N * sum_v x_v^2
where Dir_f(x) = sum_{e} tau_f(e) (x_u-x_v)^2  (the tau_f-weighted Dirichlet form of cycle-edges of f).

We want a per-f LOWER BOUND of the form
   a_bar(ell_f) Dir_f(x) - ell_f sum_v p_f(v) x_v^2  >=  -c_f * (something controllable)
that, summed, beats the -? . The constant N*||x||^2 is the only positive reservoir.

CIRCULANT FACT (per cycle, single shortest geodesic Q closing f, cycle C of odd length L):
   on the L cycle vertices, with q the indicator/uniform vector,
   a*_L L_C  >=  L q q^T - L diag(q)  ... that's the LOCAL half (K<=M). For GLOBAL we need:
   a*_L L_C  +  diag(L*? )  relate to N.

This probe EXACTLY computes, on instances, the per-bad-edge form
   Phi_f(x) := a_bar(ell_f) Dir_f(x) - ell_f sum_v p_f(v) x_v^2
and checks the candidate Angle-C bound:
   Phi_f(x) >= -ell_f * (max over cycle of x_v^2 averaged?)  -- we instead extract the WORST x.

Concretely we test the SHARP per-f bound from the circulant eigenvalue:
   a_bar(L) L_C(f) - L diag(p_f)  has min eigenvalue ??  -> if >= -L*(rank-1 along 1) only.
We compute eig of  A_f := a_bar(L) * L_{tau_f}  -  L * diag(p_f)   (restricted to support of f),
and report (i) its min eigenvalue, (ii) its value on constant mode = -L (since L_tau ann. 1,
   const mode: -L * sum p_f(v) = -L * (mass) ). For a single ell-cycle sum p_f = ... let's see.
Then H = sum_f A_f + N I. So H>=0  <=>  sum_f A_f >= -N I. The constant-mode gives
   1^T(sum_f A_f)1 = - sum_f L * (sum_v p_f(v)).  sum_v p_f(v) = L (each geodesic has L vertices,
   uniform avg). Actually sum_v p_f(v) = ell(f) (number of vertices on an ell-cycle's geodesic = ell).
   => 1^T(sum A_f)1 = -sum_f ell^2 = -Gamma, matches 1^T H 1 = N^2-Gamma. GOOD.

KEY QUESTION (the obstruction): is  A_f >= -ell_f * (p_f p_f^T)/(something) ?  i.e. is the negative
part of each A_f confined to a rank-1 direction we can charge against N*I via sum_f ... <= N I?
We test candidate:  A_f + ell_f * p_f p_f^T / m_f  >= 0  for m_f = sum_v p_f(v) = ell_f, i.e.
   B_f := a_bar(L) L_{tau_f} - L diag(p_f) + p_f p_f^T   >= 0 ??
and separately whether  sum_f (ell_f/m_f) p_f p_f^T = (1/?)K-like <= N I.
"""
import sys, io
if __name__=="__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side
from _gcd import is_psd_exact

def a_bar(ell): return F(ell**3, 4*(ell*ell-2))

def per_f_objects(adj, side, n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    out=[]
    for f in M:
        L=ell[f]; ae=a_bar(L); Ps=cyc[f]; k=len(Ps)
        # tau_f edge weights (including f itself, tau=1)
        tau={}
        ef=frozenset(f); tau[ef]=F(1)
        for P in Ps:
            for i in range(len(P)-1):
                e2=frozenset((P[i],P[i+1])); tau[e2]=tau.get(e2,F(0))+F(1,k)
        # p_f
        pf={}
        for P in Ps:
            for v in P: pf[v]=pf.get(v,F(0))+F(1,k)
        out.append((f,L,ae,tau,pf))
    return out, T, N

def build_Af(tau,pf,L,ae,n):
    """A_f = ae * L_{tau} - L*diag(pf)  (n x n exact)."""
    A=[[F(0)]*n for _ in range(n)]
    for e,w in tau.items():
        u,v=tuple(e); ww=ae*w
        A[u][u]+=ww; A[v][v]+=ww; A[u][v]-=ww; A[v][u]-=ww
    for v,pv in pf.items(): A[v][v]-=L*pv
    return A

def min_eig(A,n):
    import numpy as np
    if n==0: return 0.0
    Anp=np.array([[float(A[i][j]) for j in range(n)] for i in range(n)])
    return float(min(np.linalg.eigvalsh(Anp)))

def test_candidate(adj,side,n,verbose=False):
    r=per_f_objects(adj,side,n)
    if r is None: return None
    objs,T,N=r
    results={}
    # Candidate B_f := A_f + p_f p_f^T  >= 0 ?  (charge rank-1 against identity reservoir)
    Bfail=0; Bmins=[]
    sumcharge=[[F(0)]*n for _ in range(n)]  # sum_f (ell/m_f) p_f p_f^T  with m_f=ell => sum_f p_f p_f^T
    for (f,L,ae,tau,pf) in objs:
        A=build_Af(tau,pf,L,ae,n)
        # support of f
        supp=sorted(set([x for e in tau for x in tuple(e)]) | set(pf.keys()))
        idx={v:i for i,v in enumerate(supp)}; m=len(supp)
        # B_f = A + pf pf^T  on support
        Bf=[[A[supp[i]][supp[j]] for j in range(m)] for i in range(m)]
        for i in range(m):
            for j in range(m):
                vi,vj=supp[i],supp[j]
                Bf[i][j]+=pf.get(vi,F(0))*pf.get(vj,F(0))
        psd=is_psd_exact(Bf,m)
        if not psd: Bfail+=1
        Bmins.append(min_eig(Bf,m))
        # accumulate charge pf pf^T (coefficient ell/m_f, m_f=sum pf = should be L? check)
        mf=sum(pf.values())
        coef=F(L,1)/mf  # ell/m_f
        for vi in pf:
            for vj in pf:
                sumcharge[vi][vj]+=coef*pf[vi]*pf[vj]
    # Is sum charge <= N I ?  i.e. N*I - sumcharge PSD
    C=[[ -sumcharge[i][j] for j in range(n)] for i in range(n)]
    for i in range(n): C[i][i]+=N
    charge_psd=is_psd_exact(C,n)
    charge_min=min_eig(C,n)
    # also report mass mf per f
    masses=[float(sum(pf.values())) for (f,L,ae,tau,pf) in objs]
    return dict(nbad=len(objs), Bfail=Bfail, Bmin=min(Bmins) if Bmins else None,
                charge_psd=charge_psd, charge_min=charge_min,
                masses=(min(masses),max(masses)) if masses else None)

def run_named(nm,n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: print(f"  {nm}: no bad edges"); return
    gm=min(g for _,g in cand)
    for s,g in cand:
        if g!=gm: continue
        d=test_candidate(adj,s,n)
        if d is None: continue
        print(f"  {nm} N={n}: nbad={d['nbad']} B_f-PSD-fails={d['Bfail']} (Bmin={d['Bmin']:+.4f}) "
              f"| charge<=N*I: PSD={d['charge_psd']} (min={d['charge_min']:+.4f}) mass[m_f]={d['masses']}",flush=True)
        break

if __name__=="__main__":
    from _bdef_construct import Cn, mycielski
    print("=== ANGLE C candidate: B_f=A_f+p_f p_f^T >=0  AND  sum (ell/m_f) p_f p_f^T <= N I ===")
    cur=(5,Cn(5)); run_named("C5",*cur)
    # C5[t] blowups
    for t in (2,3):
        nn=5*t; EE=[(i*t+a,((i+1)%5)*t+b) for i in range(5) for a in range(t) for b in range(t)]
        run_named(f"C5[{t}]",nn,EE)
    cur=(5,Cn(5)); cur=mycielski(*cur); run_named("Grotzsch=N11",cur[0],cur[1])
    cur=mycielski(*cur); run_named("Myc2(C5)=N23",cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run_named("Myc(C7)=N15",cur[0],cur[1])
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); run_named(g6,n,E)
