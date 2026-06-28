"""ANGLE B pt5: (i) EXACT Dirichlet/Thomson variational identity for Y_eff,
(ii) where N enters, (iii) extremal C5[t] equality (connectivity / global mode).

(i) For x on O, the grounded Dirichlet energy
      E(x) = min_{y on Q}  sum_{e=(a,b)} omega(e) (z_a - z_b)^2 + sum_q R_Q(q) z_q^2
      with z = x on O, z = y on Q  (ground at potential 0, R_Q = leak edges to ground)
    equals  x^T Y_eff x  where Y_eff = Schur(L_omega / (L_omega,QQ+R_Q)).
    PROOF (standard): minimize the quadratic in y; KKT gives y* = -(L_QQ+R_Q)^{-1} L_QO x;
    plug back -> x^T (L_OO - L_OQ(L_QQ+R_Q)^{-1}L_QO) x = x^T Y_eff x.   We verify EXACTLY
    on a random rational x by comparing x^T Y_eff x against energy at y* (and that y* is the min).

(iii) C5[t] blow-up: T == N everywhere (extremal). Then O is EMPTY, R_Q = 0,
    H = L_omega has constant null mode (1^T H 1 = N^2 - Gamma = 0). CAP is vacuous but
    H>=0 is tight (mineig 0). Connectivity of B <=> H has a 1-dim kernel (only constant).
    We confirm: kernel of H = span(1) exactly iff B connected (Laplacian connectivity).
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _gcd import is_psd_exact, a_bar, build_H
from _capflow import build_Lomega_and_T
from _capflow3 import schur_Lomega_on_O

def energy_at(L,T,n,O,Q,xO,yQ):
    """sum_e omega(e)(z_a-z_b)^2 + sum_q R_Q(q) z_q^2, z=xO on O, yQ on Q.
       omega(e)(z_a-z_b)^2 summed = z^T L_omega z (z restricted to V, ground excluded)."""
    z=[F(0)]*n
    for i,v in enumerate(O): z[v]=xO[i]
    for i,v in enumerate(Q): z[v]=yQ[i]
    # z^T L z
    e=F(0)
    for i in range(n):
        for j in range(n):
            e+=z[i]*L[i][j]*z[j]
    # ground leak: sum_q R_Q(q) z_q^2
    for i,v in enumerate(Q):
        e+=(F(n)-T[v])*yQ[i]**2
    return e

def solve_yQ(L,T,n,O,Q,xO):
    """y* = -(L_QQ+R_Q)^{-1} L_QO xO, exact via solving linear system."""
    nq=len(Q)
    A=[[L[Q[i]][Q[j]]+(F(n)-T[Q[i]] if i==j else F(0)) for j in range(nq)] for i in range(nq)]
    b=[ -sum(L[Q[i]][O[k]]*xO[k] for k in range(len(O))) for i in range(nq)]
    # Gaussian elimination exact
    M=[A[i][:]+[b[i]] for i in range(nq)]
    for c in range(nq):
        p=next((r for r in range(c,nq) if M[r][c]!=0),None)
        if p is None: continue
        M[c],M[p]=M[p],M[c]
        d=M[c][c]
        M[c]=[v/d for v in M[c]]
        for r in range(nq):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[M[r][k]-f*M[c][k] for k in range(nq+1)]
    return [M[i][nq] for i in range(nq)]

def test_variational(adj,side,n,seed=0):
    r=build_Lomega_and_T(adj,side,n)
    if r is None: return None
    L,T,omega=r
    O=[v for v in range(n) if T[v]>n]; Q=[v for v in range(n) if T[v]<=n]
    if not O: return None
    scY=schur_Lomega_on_O(L,T,n)
    if scY is None: return None
    Yeff,_,_=scY
    rng=random.Random(seed)
    xO=[F(rng.randint(-4,4)) for _ in O]
    yStar=solve_yQ(L,T,n,O,Q,xO)
    Emin=energy_at(L,T,n,O,Q,xO,yStar)
    quadY=sum(xO[i]*Yeff[i][j]*xO[j] for i in range(len(O)) for j in range(len(O)))
    # perturb y to confirm it's a MIN (energy increases)
    yP=[yStar[i]+(F(1) if i==0 else F(0)) for i in range(len(Q))]
    Epert=energy_at(L,T,n,O,Q,xO,yP) if Q else Emin
    return dict(identity=(Emin==quadY), is_min=(Epert>=Emin), Emin=Emin, quadY=quadY)

def kernel_dim_H(adj,side,n):
    """dim ker(H) via exact rank. For extremal (T==N) H=L_omega; ker=span(1) iff B-omega connected."""
    bh=build_H(adj,side,n)
    if bh is None: return None
    H,T,N=bh
    # rank over Fraction
    M=[row[:] for row in H]; rank=0; rows=n; cols=n; pr=0
    for c in range(cols):
        piv=next((r for r in range(pr,rows) if M[r][c]!=0),None)
        if piv is None: continue
        M[pr],M[piv]=M[piv],M[pr]
        d=M[pr][c]; M[pr]=[v/d for v in M[pr]]
        for r in range(rows):
            if r!=pr and M[r][c]!=0:
                f=M[r][c]; M[r]=[M[r][k]-f*M[r and pr or pr][k] for k in range(cols)] if False else [M[r][k]-f*M[pr][k] for k in range(cols)]
        pr+=1; rank+=1
        if pr==rows: break
    return n-rank  # nullity

def run_gmin_cuts(n,E):
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
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

if __name__=="__main__":
    print("=== ANGLE B pt5: Dirichlet identity + extremal kernel ===",flush=True)
    from _bdef_construct import Cn, mycielski
    C5=(5,Cn(5)); g11=mycielski(*C5); g23=mycielski(*g11); g15=mycielski(7,Cn(7))
    named=[("Grotzsch N11",g11),("Myc2(C5) N23",g23),("Myc(C7) N15",g15)]
    for g6 in ["G?bF`w","I?BD@g]Qo","J??CE?{{?]?"]:
        named.append((g6,dec(g6)))
    print("--- (i) Dirichlet variational identity  x^T Y_eff x == min_y energy  (exact) ---",flush=True)
    for nm,(nn,EE) in named:
        adj,cs=run_gmin_cuts(nn,EE)
        for s in cs:
            allok=True; ismin=True
            for sd in range(4):
                d=test_variational(adj,s,nn,seed=sd)
                if d is None: allok=None; break
                if not d['identity']: allok=False
                if not d['is_min']: ismin=False
            if allok is None: continue
            print(f"  {nm}: identity(x^TY x=Emin)={allok} y*-is-min={ismin}",flush=True)
            break
    print("--- (iii) extremal C5[t]: T==N, H=L_omega, nullity(H) (=1 iff B connected) ---",flush=True)
    for t in (1,2,3):
        nn=5*t; EE=[(i*t+a,((i+1)%5)*t+b) for i in range(5) for a in range(t) for b in range(t)]
        adj=[set() for _ in range(nn)]
        for x,y in EE: adj[x].add(y); adj[y].add(x)
        cuts=[s for s in maxcut_all(nn,adj) if Bconn(nn,adj,s)]
        # take a connected-B max cut
        s=None
        for cc in cuts:
            Mb=[(u,v) for u in range(nn) for v in adj[u] if v>u and cc[u]==cc[v]]
            if Mb: s=cc; break
        if s is None: print(f"  C5[{t}]: no bad-edge cut"); continue
        bh=build_H(adj,s,nn)
        if bh is None: print(f"  C5[{t}]: build None"); continue
        H,T,N=bh
        nul=kernel_dim_H(adj,s,nn)
        allTeqN=all(T[v]==N for v in range(nn))
        Hpsd=is_psd_exact([row[:] for row in H],nn)
        print(f"  C5[{t}] N={nn}: T==N all={allTeqN} H-PSD={Hpsd} nullity(H)={nul} (1 => only constant null mode => B connected, tight)",flush=True)
