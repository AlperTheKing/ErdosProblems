"""ANGLE D, case |O|=1: single overloaded vertex o.  EXACT scalar effective-conductance certificate.

SETUP.  H = L_omega + diag(N - T),  L_omega = weighted Laplacian on B u M (edge weights omega(e)>=0).
        L_omega >= 0 and L_omega @ 1 = 0.   Diagonal diag(N-T) is >=0 on Q={T<=N}, <0 on O={T>N}.
        IDENTITY  1^T H 1 = sum_v (N-T(v)) = N^2 - Gamma  (so H>=0 => Gamma<=N^2, the full theorem).

|O|=1.  O={o}.  V = {o} u Q.  H_QQ = L_{omega,QQ} + R_Q,  R_Q = diag(N-T)|_Q >= 0.
   H_QQ is a GROUNDED weighted Laplacian (delete row/col o from L_omega) PLUS the nonneg diagonal R_Q.
   With B connected, the grounded Laplacian L_{omega,QQ} is already PD, so H_QQ is PD => invertible.
   By Schur complement (H_QQ PD):   H >= 0  <=>  scalar

       S(o) := H_oo - H_{oQ} H_QQ^{-1} H_{Qo}  >= 0.

   Now H_oo = (N - T(o)) + deg_omega(o),  deg_omega(o)=sum_{e ni o} omega(e) = L_omega[o,o].
   H_{oQ} = L_{omega}[o,Q] (the omega-edges from o, all <=0 entries), since diag(N-T) has no off-diag.
   So  H_oo - L_omega[o,o] = N - T(o) = -(T(o)-N) = -D_o   (D_o = T(o)-N > 0).

   ELECTRICAL READ.  Consider the omega-network on V with extra grounding conductances R_Q(v)=N-T(v)>=0
   tying each q in Q to a global ground node g.  Inject unit current at o, extract at g.  The Schur
   complement of (L_omega+diag(0 on o, R_Q on Q)) onto {o} is exactly the effective conductance
   C_eff(o<->g) of o to ground through the omega-network terminated by the deficit resistors R_Q.
   Precisely:   L_omega[o,o] - L_omega[o,Q] (L_{omega,QQ}+R_Q)^{-1} L_omega[Q,o]  =  C_eff(o<->g).
   Hence

       S(o) = (N - T(o)) + C_eff(o<->g)  =  C_eff(o<->g) - D_o.

   CERTIFICATE (|O|=1):   (CAP)/(GCD) for a single overloaded vertex  <=>   C_eff(o<->g) >= T(o) - N.
   "The omega-network, grounded by the load-deficits (N-T) on under-loaded vertices, presents an
    effective conductance from o to ground at least equal to o's overload T(o)-N."

This file: (a) build H exactly; (b) form S(o) two ways -- Schur complement AND the electrical C_eff via
the grounded-network Laplacian -- and check they AGREE exactly (validates the electrical identity);
(c) report S(o), C_eff, D_o as exact Fractions on every |O|=1 instance in the census + named family.
A PASS means S(o)>=0 i.e. C_eff>=D_o, exact.  This is the exact-testable certificate for |O|=1."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _gcd import build_H

def schur_scalar(H, n, O):
    """S(o) = H_oo - H_oQ H_QQ^{-1} H_Qo for O={o}, by eliminating Q via Gaussian pivoting. Exact."""
    assert len(O)==1
    o=O[0]; Q=[v for v in range(n) if v!=o]
    M=[[H[i][j] for j in range(n)] for i in range(n)]
    pd=True
    for q in Q:
        d=M[q][q]
        if d<=0: pd=False; break
        for i in range(n):
            if i==q or M[i][q]==0: continue
            fac=M[i][q]/d
            for j in range(n): M[i][j]-=fac*M[q][j]
    return (M[o][o] if pd else None), pd

def ceff_electrical(adj, side, n, o):
    """Build C_eff(o<->ground) directly from the grounded omega-network and confirm = N-T(o)+S(o).
       Grounded Laplacian Lg on Q-vertices: Lg = L_{omega,QQ} + R_Q (R_Q=N-T on Q).  Current vector
       b_q = -L_omega[o,q].  Then C_eff = L_omega[o,o] - b^T Lg^{-1} b.  Returns C_eff exact."""
    from _satzmu_conn import struct_for_side
    st=struct_for_side(n,adj,side)
    if st is None: return None
    from _gcd import a_bar
    M_,ell,T,mu,cyc=st; N=n
    omega={}
    for f in M_:
        ae=a_bar(ell[f]); Ps=cyc[f]; k=len(Ps)
        ef=frozenset(f); omega[ef]=omega.get(ef,F(0))+ae
        for P in Ps:
            for i in range(len(P)-1):
                e2=frozenset((P[i],P[i+1])); omega[e2]=omega.get(e2,F(0))+ae*F(1,k)
    L=[[F(0)]*n for _ in range(n)]
    for e,w in omega.items():
        u,v=tuple(e); L[u][u]+=w; L[v][v]+=w; L[u][v]-=w; L[v][u]-=w
    Q=[v for v in range(n) if v!=o]
    # Lg = L_QQ + diag(N-T) on Q
    qi={v:i for i,v in enumerate(Q)}; m=len(Q)
    Lg=[[L[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    for i,v in enumerate(Q): Lg[i][i]+=F(N)-T[v]
    b=[-L[o][v] for v in Q]   # = L_omega[o,q] negated; current injection pattern
    # solve Lg x = b exactly (Gaussian); C_eff = L[o][o] - b^T x
    A=[row[:]+[b[i]] for i,row in enumerate(Lg)]
    for c in range(m):
        p=next((r for r in range(c,m) if A[r][c]!=0),None)
        if p is None: return None
        A[c],A[p]=A[p],A[c]
        pv=A[c][c]
        for r in range(m):
            if r==c or A[r][c]==0: continue
            fac=A[r][c]/pv
            for k in range(c,m+1): A[r][k]-=fac*A[c][k]
    x=[A[i][m]/A[i][i] for i in range(m)]
    bx=sum(b[i]*x[i] for i in range(m))
    Ceff=L[o][o]-bx
    return Ceff, T[o], F(N)

def gmin_sides(n,E):
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

def test_O1(adj,side,n):
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=1: return ('skip',len(O))
    o=O[0]
    S,pd=schur_scalar(H,n,O)
    el=ceff_electrical(adj,side,n,o)
    if el is None or not pd: return ('badpivot',o)
    Ceff,To,Nf=el
    Do=To-Nf
    # identity: S should equal Ceff - Do = Ceff +(N-To)
    ident_ok = (S == Ceff - Do)
    cert_ok = (S>=0)
    return ('ok',dict(o=o,S=S,Ceff=Ceff,Do=Do,ident_ok=ident_ok,cert_ok=cert_ok))

if __name__=="__main__":
    print("=== ANGLE D |O|=1: scalar effective-conductance certificate  S(o)=C_eff(o<->g)-D_o >= 0 ===")
    from _bdef_construct import Cn, mycielski
    named=[]
    C5=(5,Cn(5)); n1,E1=mycielski(*C5)       # Grotzsch N=11
    m1,F1=mycielski(7,Cn(7))                   # Myc(C7) N=15
    named=[("Grotzsch N=11",(n1,E1)),("Myc(C7) N=15",(m1,F1))]
    for g6 in ["I?ABCc]}?"]:
        nn,EE=dec(g6); named.append((g6,(nn,EE)))
    for nm,(nn,EE) in named:
        adj,sides=gmin_sides(nn,EE)
        for s in sides:
            r=test_O1(adj,s,nn)
            if r is None or r[0]!='ok': continue
            d=r[1]
            print(f"  {nm}: o={d['o']} S={d['S']} (Ceff={d['Ceff']} - Do={d['Do']}) "
                  f"ident={d['ident_ok']} CERT(S>=0)={d['cert_ok']}",flush=True)
            break
    # census N=8..10, ALL gamma-min cuts, aggregate the |O|=1 certificate
    print("--- census N=8..10, all gamma-min cuts, |O|=1 certificate ---")
    for nn in range(8,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; idfail=0; certfail=0; minS=None; wit=None
        for g6 in outg:
            n,E=dec(g6); adj,sides=gmin_sides(n,E)
            for s in sides:
                r=test_O1(adj,s,n)
                if r is None or r[0]!='ok': continue
                d=r[1]; tot+=1
                if not d['ident_ok']: idfail+=1
                if not d['cert_ok']: certfail+=1; wit=wit or g6
                if minS is None or d['S']<minS: minS=d['S']
        print(f"  census N={nn}: |O|=1 cuts={tot} ident-FAILS={idfail} CERT-FAILS={certfail}"
              f"{' WIT '+wit if wit else ''} | min S(o)={minS}",flush=True)
