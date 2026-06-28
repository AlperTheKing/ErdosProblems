"""EXACT-TEST of GPT-Pro's GREEN-CAPACITY DOMINATION (GCD) lemma for rho(K)<=N (my cond3/ROWSUM-O leg).
   omega(e) = sum_{f in M} a_bar(ell(f)) * tau_f(e),  a_bar(ell)=ell^3/(4(ell^2-2)),
   tau_f(e) = fraction of f's shortest geodesics whose odd cycle C(f,Q)=geodesic+bad-edge uses e (tau_f(f)=1).
   L_omega = weighted Laplacian on B∪M; H = L_omega + diag(N - T).  CLAIM (GCD): H ⪰ 0.
   Then K ⪯ diag(T)-L_omega ⪯ N·I  ⟹  rho(K)<=N. Exact rational PSD test."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side

def a_bar(ell): return F(ell**3, 4*(ell*ell-2))   # > ell/4 for ell>=5

def build_H(adj, side, n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    omega={}
    for f in M:
        ae=a_bar(ell[f]); Ps=cyc[f]; k=len(Ps)
        ef=frozenset(f); omega[ef]=omega.get(ef,F(0))+ae           # tau_f(f)=1
        for P in Ps:
            for i in range(len(P)-1):
                e2=frozenset((P[i],P[i+1]))
                omega[e2]=omega.get(e2,F(0))+ae*F(1,k)             # B-edge traffic
    L=[[F(0)]*n for _ in range(n)]
    for e,w in omega.items():
        u,v=tuple(e); L[u][u]+=w; L[v][v]+=w; L[u][v]-=w; L[v][u]-=w
    H=[[L[i][j] for j in range(n)] for i in range(n)]
    for v in range(n): H[v][v]+=F(N)-T[v]
    return H,T,N

def is_psd_exact(A,n):
    """Symmetric PSD test over Fraction via diagonal-pivoted Gaussian elimination."""
    M=[[A[i][j] for j in range(n)] for i in range(n)]
    used=[False]*n
    for _ in range(n):
        piv=-1; best=None
        for i in range(n):
            if used[i]: continue
            if best is None or M[i][i]>best: best=M[i][i]; piv=i
        if piv==-1: break
        d=M[piv][piv]
        if d<0: return False
        if d==0:
            for j in range(n):
                if not used[j] and M[piv][j]!=0: return False
            used[piv]=True; continue
        used[piv]=True
        for i in range(n):
            if used[i] or M[i][piv]==0: continue
            fac=M[i][piv]/d
            for j in range(n):
                if not used[j]: M[i][j]-=fac*M[piv][j]
    return True

def float_mineig(H,n):
    import numpy as np
    A=np.array([[float(H[i][j]) for j in range(n)] for i in range(n)])
    return float(min(np.linalg.eigvalsh(A)))

def build_MmK(adj, side, n):
    """M - K = diag(T) - L_omega - K  (the local comparison K ⪯ M). Returns (M-K) exact."""
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    # K = sum_f p_f p_f^T
    K=[[F(0)]*n for _ in range(n)]
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        pf={}
        for P in Ps:
            for v in P: pf[v]=pf.get(v,F(0))+F(1,k)
        it=list(pf.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    # L_omega
    omega={}
    for f in M:
        ae=a_bar(ell[f]); Ps=cyc[f]; k=len(Ps)
        ef=frozenset(f); omega[ef]=omega.get(ef,F(0))+ae
        for P in Ps:
            for i in range(len(P)-1):
                e2=frozenset((P[i],P[i+1])); omega[e2]=omega.get(e2,F(0))+ae*F(1,k)
    L=[[F(0)]*n for _ in range(n)]
    for e,w in omega.items():
        u,v=tuple(e); L[u][u]+=w; L[v][v]+=w; L[u][v]-=w; L[v][u]-=w
    # MmK = diag(T) - L - K
    MmK=[[ -L[i][j]-K[i][j] for j in range(n)] for i in range(n)]
    for v in range(n): MmK[v][v]+=T[v]
    return MmK

def test_side(adj,side,n):
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    Hpsd=is_psd_exact(H,n)
    MmK=build_MmK(adj,side,n)
    MmKpsd=is_psd_exact(MmK,n) if MmK is not None else None
    return Hpsd and MmKpsd, float_mineig(H,n), Hpsd, MmKpsd

def run_gmin(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]] if False else [(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return None
    gm=min(g for _,g in cand)
    res=[]
    for s,g in cand:
        if g!=gm: continue
        r=test_side(adj,s,n)
        if r: res.append(r)
    return res

if __name__=="__main__":
    print("=== GREEN-CAPACITY DOMINATION (GCD): H = L_omega + diag(N-T) ⪰ 0 (exact PSD) ===")
    from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
    from _superphi import blow
    # C5[t] extremal (should be PSD, tight)
    for t in (1,2,3):
        nn,EE=blow("J?AEB?oE?W?",t) if False else (5*t,[(i*t+a,((i+1)%5)*t+b) for i in range(5) for a in range(t) for b in range(t)])
        info=loads(nn,EE)
        if info:
            r=test_side(info['adj'],info['side'],info['n'])
            print(f"  C5[{t}] N={nn}: GCD PSD-exact={r[0]} float-mineig={r[1]:+.5f}",flush=True)
    # named + Mycielskians + blowups + N=22 witness
    C5=(5,Cn(5)); n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(7,Cn(7))
    named=[("Grotzsch N=11",(n1,E1)),("Myc(Grotzsch) N=23",(n2,E2)),("Myc(C7) N=15",(m1,F1))]
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        nn,EE=dec(g6); named.append((g6,(nn,EE)))
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t); named.append((f"{g6}[{t}]",(nn,EE)))
    for nm,(nn,EE) in named:
        info=loads(nn,EE)
        if info is None: print(f"  {nm}: loads None"); continue
        r=test_side(info['adj'],info['side'],info['n'])
        print(f"  {nm} N={info['n']}: BOTH-PSD-exact={r[0]} (H={r[2]} M-K={r[3]}) float-mineig(H)={r[1]:+.5f}",flush=True)
    # GLUED ISLAND BATTERY (the guardrail blind spot) -- all gamma-min cuts
    print("--- glued-island battery (all gamma-min cuts) ---")
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    gtot=0; gbad=0; gwit=None
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                res=run_gmin(n,E)
                if not res: continue
                for r in res:
                    gtot+=1
                    if not r[0]: gbad+=1; gwit=gwit or f"isl{iN}+gad{gN}{br}"
    print(f"  glued battery: cuts={gtot} BOTH-PSD-FAILS={gbad}{' WIT '+str(gwit) if gwit else ''}",flush=True)
    # census N=7..10 all gamma-min cuts (exact, BOTH H and M-K)
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ncut=0; bad=0; minf=None; wit=None
        for g6 in outg:
            n,E=dec(g6)
            res=run_gmin(n,E)
            if not res: continue
            for r in res:
                ncut+=1
                if not r[0]: bad+=1; wit=wit or g6
                if minf is None or r[1]<minf: minf=r[1]
        print(f"  census N={nn} (all gamma-min cuts): cuts={ncut} BOTH-PSD-FAILS={bad}{' WIT '+wit if wit else ''} | min float-mineig(H)={minf:+.5f}",flush=True)
