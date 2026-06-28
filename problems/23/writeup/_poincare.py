"""The decomposition N*I-K = B + (N*I - diag(T)) reduces (SPEC) to a POINCARE inequality:
   (POIN)  for all x:  Q_B(x) := sum_{v<w} K_vw (x_v-x_w)^2  >=  sum_v (T_v - N) x_v^2 =: R(x).
B PSD-with-proof (Laplacian). RHS R(x) is a signed potential: positive on overloaded vertices (T_v>N),
negative on underloaded (T_v<N). (POIN) <=> N I - K PSD <=> SPEC.

Investigate the STRUCTURE that makes (POIN) hold:
 1. The overloaded vertices: how many, where (always interior of long geodesics? high-multiplicity?).
 2. B's connectivity: do overloaded vertices have large B-degree (sum_w K_vw = T_v) connecting them to
    underloaded vertices? Row sum of B is 0, diag B_vv = T_v - K_vv. For an overloaded v, T_v>N, and the
    Laplacian 'pushes' x_v toward neighbors -> Poincare slack.
 3. Localized test: the worst x for (POIN) is the bottom eigenvector of N I - K. Print it at worst-slack graphs.
 4. Two-sided: since sum_v(T_v-N)=Gamma-N^2 = (over - under). For Gamma<=N^2, total RHS coefficient sum<=0.
    But R(x) can still be positive for x concentrated on overloaded set. Key: B must beat LOCAL concentration.
 5. CRUCIAL simpler sufficient condition: is the *diagonal-shifted* form provable, e.g.
       Q_B(x) >= sum_v (T_v-N)x_v^2  follows if for each overloaded v, K_vw mass to lower-T vertices is enough?
    Test the 'star/local' bound:  (T_v-N) x_v^2 <= sum_w K_vw (x_v-x_w)^2 charged per-vertex? (likely FALSE,
    needs global). Report whether per-vertex charging works or fails (with the failing graph)."""
import numpy as np
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow
from _crofton_lp import overlap_matrix

np.set_printoptions(precision=3, suppress=True, linewidth=200)

def data(info):
    n=info['n']; N=n
    O,P,pf=overlap_matrix(info)
    K=P@P.T
    T=np.array([float(t) for t in info['T']])
    NIK=N*np.eye(n)-K
    w,V=np.linalg.eigh(NIK)
    over=[v for v in range(n) if T[v]>N+1e-9]
    return n,N,K,T,NIK,w,V,over

def worst_x_struct(info, g6):
    n,N,K,T,NIK,w,V,over=data(info)
    x=V[:,0]  # bottom eigvec
    print(f"\n{g6} N={N}: lam_min(N I-K)={w[0]:+.4f}  #overloaded={len(over)} over-set={over}")
    print(f"   T={np.round(T,3)}")
    print(f"   bottom eigvec x={np.round(x/ x[np.argmax(np.abs(x))],3)}")
    # is bottom eigvec concentrated on overloaded set? sign pattern
    if over:
        print(f"   x on overloaded {[round(x[v],3) for v in over]}  vs mean|x|={np.mean(np.abs(x)):.3f}")

def per_vertex_charge(info):
    """Test sufficient (per-vertex) charging: does (T_v-N)x_v^2 <= sum_w K_vw (x_v-x_w)^2 hold per v
    for the worst x? Equivalent: is diag(T-N) <= B-as-rowsplit? This per-vertex bound is generally FALSE;
    we look for a counterexample (overloaded v whose B-edges can't pay). We test on the bottom eigvec."""
    n,N,K,T,NIK,w,V,over=data(info)
    x=V[:,0]
    bad=[]
    for v in over:
        lhs=(T[v]-N)*x[v]**2
        rhs=sum(K[v][w]*(x[v]-x[w])**2 for w in range(n) if w!=v)
        if lhs>rhs+1e-9: bad.append((v,lhs,rhs))
    return bad

def census_overload(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit: out=out[:limit]
    nt=0; worst=None; wg=None; maxnover=0; mg=None; pvfail=0; pvfail_g=None
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1
        nn2,N,K,T,NIK,w,V,over=data(info)
        if worst is None or w[0]<worst: worst=w[0]; wg=g6
        if len(over)>maxnover: maxnover=len(over); mg=g6
        b=per_vertex_charge(info)
        if b: pvfail+=1; pvfail_g=g6
    print(f"N={nn}: cfg={nt} | min lam(N I-K)={worst:+.5e}@{wg} | max #overloaded-verts={maxnover}@{mg} | #graphs where per-vertex charge FAILS on bottom-eigvec={pvfail}@{pvfail_g}")

if __name__=="__main__":
    print("=== overload structure + per-vertex charging test ===")
    for nn in [8,9,10]:
        census_overload(nn, limit=(None if nn<=9 else 1500))
    print("\n=== detailed worst-slack and most-overloaded graphs ===")
    for g6 in ["G?`F`w","I?ABCc]}?","H?AFBo]"]:
        n,E=dec(g6); info=loads(n,E)
        if info is None: print(f"  {g6}: None"); continue
        worst_x_struct(info,g6)
        b=per_vertex_charge(info)
        print(f"   per-vertex charge failures on bottom eigvec: {b if b else 'none (per-vertex charging HOLDS here)'}")
    print("\n=== blowups (tight, x=const nullvec) ===")
    for t in [3,4]:
        nn,E=blow(t); info=loads(nn,E)
        worst_x_struct(info,f"C5[{t}]")
