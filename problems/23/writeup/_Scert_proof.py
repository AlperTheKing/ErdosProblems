"""Proof-structure probe for  C(f)=sum_v p_f(v) S(v) <= N,  S(v)=sum_g p_g(v).

Decompose C(f) = D_f + Off_f where
  D_f = sum_v p_f(v)^2 = ||p_f||^2 = O_ff  (diagonal/self overlap)  <= ell(f)  [since p_f(v)<=1, sum=ell]
  Off_f = sum_{g != f} sum_v p_f(v) p_g(v) = sum_{g!=f} O_fg.

Candidate proof avenues to test EXACTLY:
 (Q1)  S(v) <= N for ALL v?  (pointwise; if true with sum_v p_f(v)<=... no -- p_f mass=ell, would give N*ell. too weak.)
       But maybe S(v) small where p_f large. Test correlation.
 (Q2)  The 'gate' version on S: is sum_v p_f(v) S(v) <= sum over a CUT-budget of N?
       Equivalent target: sum_g O_fg <= N. Since O_fg=<p_f,p_g>, and CD bounds cut crossings...
 (Q3)  Double counting:  sum_f C(f) = sum_f sum_g O_fg = 1^T O 1 = ||sum_g p_g||^2 = sum_v S(v)^2.
       And sum_f (rowsum) <= N * m would follow from sum_v S(v)^2 <= N * (#bad edges)? test.
       More useful: sum_v S(v)^2 <= N * sum_v S(v)?  i.e. sum_v S(v)^2 <= N * L (L=sum ell).
       That's '<S,S> <= N <S,1>' = avg-weighted-by-S of S <= N. test.
 (Q4)  KEY: S(v) is the number of bad-geodesics through v. Triangle-free + shortest-odd-cycle structure:
       a vertex v lies on the geodesic of bad edge g only if d_B(g)+... Is there a bound
       'S(v) <= (number of bad edges incident to the B-ball around v)'? Probe S(v) vs local degree.
Report exact census small + blowups."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads, blow

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def analyze(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']
    pfs={f:pf_vec(info,f) for f in M}
    S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
    L=sum(S.values())
    # Q3 global: sum_v S^2 <= N*L ?
    SS=sum(S[v]*S[v] for v in range(n))
    q3 = (SS<=F(N)*L)
    # Q1 pointwise maxS
    maxS=max(S.values()) if S else F(0)
    per=[]
    for f in M:
        Cf=sum(pfs[f][v]*S[v] for v in pfs[f])
        Dff=sum(pfs[f][v]*pfs[f][v] for v in pfs[f])
        per.append(dict(f=f,Cf=Cf,Dff=Dff,Off=Cf-Dff,ell=ell[f],N=N))
    return dict(N=N,L=L,SS=SS,q3=q3,maxS=maxS,per=per)

def run(nmin,nmax,limit=None):
    print(f"=== Scert proof-structure census N={nmin}..{nmax} ===")
    q3fail=0; ng=0; worst_q3=F(0); wg=None; worst_maxS=F(0); wmg=None
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            r=analyze(info)
            if not r['q3']:
                q3fail+=1
            ratio=r['SS']/(F(r['N'])*r['L']) if r['L']>0 else F(0)
            if ratio>worst_q3: worst_q3=ratio; wg=(g6,str(r['SS']),str(r['L']),r['N'])
            if r['maxS']/F(r['N'])>worst_maxS: worst_maxS=r['maxS']/F(r['N']); wmg=(g6,str(r['maxS']),r['N'])
    print(f"graphs={ng} | (Q3) sum_v S^2 <= N*L fails:{q3fail}")
    print(f"  worst (sum S^2)/(N*L) = {float(worst_q3):.5f} @ {wg}")
    print(f"  worst max_v S(v)/N = {float(worst_maxS):.5f} @ {wmg}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups ===")
    for t in range(1,7):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        r=analyze(info)
        print(f"  C5[{t}] N={n}: sum S^2={float(r['SS']):.2f} N*L={float(F(n)*r['L']):.2f} q3={r['q3']} maxS/N={float(r['maxS'])/n:.3f}")
