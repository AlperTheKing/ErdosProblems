"""KEY CLAIM to verify EXACTLY: B = diag(T) - K is a weighted graph Laplacian and hence PSD.
B_vw = -K_vw <=0 for v!=w (since K_vw=sum_f p_f(v)p_f(w) >=0).  B_vv = T_v - K_vv.
Row sum_w B_vw = B_vv + sum_{w!=v} B_vw = (T_v - K_vv) - sum_{w!=v} K_vw = T_v - sum_w K_vw = T_v - T_v = 0.
A symmetric matrix with B_vw<=0 (v!=w) and zero row sums is the Laplacian of a weighted graph with edge
weights c_vw = K_vw >= 0, hence PSD with B = sum_{v<w} K_vw (e_v - e_w)(e_v - e_w)^T.  PROVABLE PSD.

VERIFY EXACTLY (Fraction):
  (a) K_vw >= 0 all v,w               -> off-diagonals of B are <=0
  (b) sum_w K_vw = T_v (row sums)     -> B row sums = 0
  (c) Then B = sum_{v<w} K_vw (e_v-e_w)(e_v-e_w)^T EXACTLY (reconstruct, compare).  [Laplacian identity]
This gives the FIRST half of the structured decomposition with a RIGOROUS proof:
   N*I - K = (N*I - diag(T)) + B,  B PSD-with-proof (Laplacian),  but (N*I - diag(T)) INDEFINITE (T_v can exceed N).
So the decomposition's REMAINING content = control the overloaded vertices (T_v>N) using B's slack.
We quantify: define the 'overload form'  q(x) = x^T(K - N I)x = x^T(diag(T)-N I)x - x^T B x.
For N*I-K PSD we need x^T B x >= x^T(diag(T)-N I)x for all x, i.e.
   sum_{v<w} K_vw (x_v-x_w)^2 >= sum_v (T_v - N) x_v^2.
RHS only has POSITIVE terms from overloaded vertices (T_v>N). So the certificate reduces to a
LAPLACIAN/POINCARE inequality: the geodesic-coincidence Laplacian B dominates the (signed) overload potential.
Report exact verification of (a)(b)(c) + the Poincare reformulation residual census-wide."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow

def build(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; cyc=info['cyc']; m=len(M)
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    K=[[F(0)]*n for _ in range(n)]
    for d in pf:
        for v,pv in d.items():
            for w,pw in d.items():
                K[v][w]+=pv*pw
    T=[sum(ell[M[g]]*pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    return n,N,K,T

def verify(info):
    n,N,K,T=build(info)
    # (a) K_vw>=0
    a_ok=all(K[v][w]>=0 for v in range(n) for w in range(n))
    # (b) row sums = T
    b_err=max(abs(sum(K[v][w] for w in range(n))-T[v]) for v in range(n))
    # (c) Laplacian reconstruction: B = sum_{v<w} K_vw (e_v-e_w)(e_v-e_w)^T
    #  -> B_vv = sum_{w!=v} K_vw ; B_vw = -K_vw (v!=w).  Compare to diag(T)-K.
    Brec=[[F(0)]*n for _ in range(n)]
    for v in range(n):
        for w in range(v+1,n):
            c=K[v][w]
            Brec[v][v]+=c; Brec[w][w]+=c; Brec[v][w]-=c; Brec[w][v]-=c
    Btrue=[[ (T[v]-K[v][v]) if v==w else -K[v][w] for w in range(n)] for v in range(n)]
    c_err=max(abs(Brec[v][w]-Btrue[v][w]) for v in range(n) for w in range(n))
    # Poincare residual: min over unit-ish x of  sum_{v<w}K_vw(x_v-x_w)^2 - sum_v(T_v-N)x_v^2
    # Just report the OVERLOAD MASS sum_v (T_v-N)+ and the laplacian total weight sum K_vw.
    over=sum((T[v]-N) for v in range(n) if T[v]>N)
    lapW=sum(K[v][w] for v in range(n) for w in range(v+1,n))
    return a_ok, b_err, c_err, over, lapW, max(T)

def census(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; alla=True; maxberr=F(0); maxcerr=F(0); maxover=F(0); og=None
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        a,be,ce,ov,lw,mt=verify(info)
        alla=alla and a
        if be>maxberr: maxberr=be
        if ce>maxcerr: maxcerr=ce
        if ov>maxover: maxover=ov; og=g6
    print(f"N={nn}: cfg={nt} | (a) K>=0 all:{alla} | (b) max|rowsumK-T|={maxberr} | (c) max|B_recon-B|={maxcerr} | max overload sum(T-N)+={maxover}={float(maxover):.2f}@{og}")

if __name__=="__main__":
    print("=== EXACT: B=diag(T)-K is a weighted Laplacian (a:K>=0, b:rowsum=T, c:Laplacian recon exact) ===")
    for nn in [7,8,9,10,11]:
        census(nn, limit=(None if nn<=10 else 1200))
    print("\n=== blowups ===")
    for t in [2,3,4]:
        nn,E=blow(t); info=loads(nn,E)
        a,be,ce,ov,lw,mt=verify(info)
        print(f"  C5[{t}] N={nn}: Kge0:{a} |rowsum-T|={be} |Brecon-B|={ce} overload(T-N)+={ov} maxT={float(mt):.2f}")
    print("\n=== tight ===")
    for g6 in ["H?bB@_W","I?rFf_{N?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E)
        a,be,ce,ov,lw,mt=verify(info)
        print(f"  {g6} N={n}: Kge0:{a} |rowsum-T|={be} |Brecon-B|={ce} overload={ov} maxT={float(mt):.2f}")
