"""ANGLE D sub-case (2): |O|=2 overloaded vertices {o1,o2}.  EXACT 2x2 Schur certificate.

H>=0 (with H_QQ PD) <=> 2x2 Schur complement  S = H_OO - H_OQ H_QQ^{-1} H_QO  >= 0
  <=>  S[0][0]>=0  AND  det(S)>=0   (then S[1][1]>=0 follows if S[0][0]>0; check both diags + det).

ELECTRICAL READING.  S = Y_O - C_grid, where the omega-network grounded by deficits R_Q on Q has a
2-port effective ADMITTANCE between {o1,o2}.  Equivalently S is the Schur complement giving the
2x2 'Green/capacity' matrix seen from O.  H_OO = [[deg_w(o1)-D1, -omega(o1o2)],[-omega(o1o2), deg_w(o2)-D2]]
where Di=T(oi)-N>0, deg_w(oi)=sum_e omega(oi,e).  Subtracting H_OQ H_QQ^{-1} H_QO replaces the bare
o1,o2 degrees by their grounded effective self/mutual conductances.

CERTIFICATE (|O|=2):  with C := [[C11,C12],[C12,C22]] the 2x2 effective-conductance (Schur) matrix of
the omega-network grounded by R_Q, seen from {o1,o2} (C = H_OO + diag(D1,D2)  after Schur, i.e.
C = S + diag(D1,D2)):    C - diag(D1,D2) >= 0  (PSD).   Equivalently the overload vector quadratic form
   x^T C x >= D1 x1^2 + D2 x2^2  for all x in R^2.
This file forms S two ways: (i) Schur via Gaussian elimination of Q, (ii) C via grounded-network solve,
and checks S = C - diag(D) exactly, then reports S PSD (S00>=0, S11>=0, detS>=0)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _gcd import build_H
from _angleD_O1 import gmin_sides
from _angleD_O1_lb import omega_of

def schur_2x2(H,n,O):
    o1,o2=O; Q=[v for v in range(n) if v not in O]
    M=[[H[i][j] for j in range(n)] for i in range(n)]
    pd=True
    for q in Q:
        d=M[q][q]
        if d<=0: pd=False; break
        for i in range(n):
            if i==q or M[i][q]==0: continue
            fac=M[i][q]/d
            for j in range(n): M[i][j]-=fac*M[q][j]
    if not pd: return None
    S=[[M[o1][o1],M[o1][o2]],[M[o2][o1],M[o2][o2]]]
    return S

def cmat_electrical(adj,side,n,O):
    """2x2 grounded effective-conductance matrix C seen from O={o1,o2}. C = L_OO - L_OQ Lg^{-1} L_QO,
       Lg = L_QQ + R_Q.  Then S should equal C - diag(D)."""
    om,T,N=omega_of(adj,side,n)
    L=[[F(0)]*n for _ in range(n)]
    for e,w in om.items():
        u,v=tuple(e); L[u][u]+=w; L[v][v]+=w; L[u][v]-=w; L[v][u]-=w
    o1,o2=O; Q=[v for v in range(n) if v not in O]; m=len(Q)
    Lg=[[L[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    for i,v in enumerate(Q): Lg[i][i]+=F(N)-T[v]
    # solve Lg X = [L_Qo1 | L_Qo2]
    B=[[L[Q[i]][o1], L[Q[i]][o2]] for i in range(m)]
    A=[Lg[i][:]+B[i] for i in range(m)]
    for c in range(m):
        p=next((r for r in range(c,m) if A[r][c]!=0),None)
        if p is None: return None
        A[c],A[p]=A[p],A[c]; pv=A[c][c]
        for r in range(m):
            if r==c or A[r][c]==0: continue
            fac=A[r][c]/pv
            for k in range(c,m+2): A[r][k]-=fac*A[c][k]
    X=[[A[i][m]/A[i][i], A[i][m+1]/A[i][i]] for i in range(m)]
    def dot(col):  # L_O,Q @ X[:,col] -> 2-vec
        s1=sum(L[o1][Q[i]]*X[i][col] for i in range(m))
        s2=sum(L[o2][Q[i]]*X[i][col] for i in range(m))
        return s1,s2
    a1,a2=dot(0); b1,b2=dot(1)
    C=[[L[o1][o1]-a1, L[o1][o2]-b1],[L[o2][o1]-a2, L[o2][o2]-b2]]
    D=[T[o1]-N, T[o2]-N]
    return C,D

def test(adj,side,n):
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=2: return None
    S=schur_2x2(H,n,O)
    if S is None: return ('badpivot',O)
    cm=cmat_electrical(adj,side,n,O)
    if cm is None: return ('badpivot',O)
    C,D=cm
    Sc=[[C[0][0]-D[0],C[0][1]],[C[1][0],C[1][1]-D[1]]]
    ident = (S[0][0]==Sc[0][0] and S[0][1]==Sc[0][1] and S[1][1]==Sc[1][1] and S[1][0]==Sc[1][0])
    det=S[0][0]*S[1][1]-S[0][1]*S[1][0]
    psd = (S[0][0]>=0 and S[1][1]>=0 and det>=0)
    return ('ok',dict(O=O,D=D,S00=S[0][0],S11=S[1][1],det=det,ident=ident,psd=psd))

if __name__=="__main__":
    print("=== ANGLE D |O|=2: 2x2 Schur certificate  S = C - diag(D) >= 0 ===")
    from _bdef_construct import Cn, mycielski
    n2,E2=mycielski(*mycielski(5,Cn(5)))  # Myc2(C5) N=23 (|O|=2)
    for nm,(nn,EE) in [("Myc2(C5)=23",(n2,E2)),("G?bF`w",dec("G?bF`w")),("J??CE?{{?]?",dec("J??CE?{{?]?"))]:
        adj,sides=gmin_sides(nn,EE)
        for s in sides:
            r=test(adj,s,nn)
            if r is None or r[0]!='ok': continue
            d=r[1]
            print(f"  {nm}: O={d['O']} D={[float(x) for x in d['D']]} S00={float(d['S00']):.4f} "
                  f"S11={float(d['S11']):.4f} det={float(d['det']):.5f} ident={d['ident']} PSD={d['psd']}",flush=True)
            break
    print("--- census N=8..11, all gamma-min cuts, |O|=2 ---")
    for nn in range(8,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; idf=0; pf=0; wit=None
        for g6 in outg:
            n,E=dec(g6); adj,sides=gmin_sides(n,E)
            for s in sides:
                r=test(adj,s,n)
                if r is None or r[0]!='ok': continue
                d=r[1]; tot+=1
                if not d['ident']: idf+=1
                if not d['psd']: pf+=1; wit=wit or g6
        print(f"  N={nn}: |O|=2 cuts={tot} ident-FAILS={idf} PSD-FAILS={pf}{' WIT '+wit if wit else ''}",flush=True)
