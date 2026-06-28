"""ANGLE C obstruction confirmation: is H>=0 reducible to per-bad-edge (per-cycle) PSD atoms,
or does it REQUIRE B-edge sharing (Dirichlet overlap) between distinct bad edges?

Test: compute   H = sum_f A_f + N I   where A_f = a_bar(L_f) L_{tau_f} - L_f diag(p_f).
1. 'No-share' surrogate: replace H by  H_noshare = sum_f (A_f restricted, treated independently) ...
   Actually the cleanest test: H = N I + sum_f A_f. The +N I is the SOLE positive reservoir besides
   the off-diagonal (Dirichlet) coupling. We test what fraction of vertices have
       (row sum of sum_f A_f) = -ell-weighted ... and whether diagonal-only N + diag(sum A_f) >= 0.
   diag(A_f)[v] = a_bar(L) * deg_tau(v) - L p_f(v).  sum over f.
2. The real question: is there a vertex v with N + diag(sum_f A_f)[v] < 0 (diagonal already negative)?
   If diagonal stays >=0 but H needs off-diag, then sharing/Dirichlet cancellation is essential.

Also: confirm  sum_v p_f(v) = ell(f)  (mass identity) and  diag accounting 1^T A_f 1 = -ell^2.
"""
import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side
from _angleC_probe import per_f_objects, build_Af, a_bar
from _gcd import is_psd_exact

def analyze(adj,side,n):
    r=per_f_objects(adj,side,n)
    if r is None: return None
    objs,T,N=r
    sumA=[[F(0)]*n for _ in range(n)]
    mass_ok=True
    for (f,L,ae,tau,pf) in objs:
        if sum(pf.values())!=L: mass_ok=False
        A=build_Af(tau,pf,L,ae,n)
        for i in range(n):
            for j in range(n): sumA[i][j]+=A[i][j]
    # diagonal of N I + sumA
    diag_neg=[v for v in range(n) if N+sumA[v][v]<0]
    diagmin=min(N+sumA[v][v] for v in range(n))
    # row sums of N I + sumA  ( = N - T(v) + 0  since L_tau row sums 0 => row sum sumA = -L p_f summed = -T(v))
    rowmin=min( N+sum(sumA[v][j] for j in range(n)) for v in range(n))
    # full H psd
    H=[[sumA[i][j] for j in range(n)] for i in range(n)]
    for v in range(n): H[v][v]+=N
    hpsd=is_psd_exact(H,n)
    # 'diagonal-dominance without sharing' surrogate: zero out all off-diagonal coupling BETWEEN
    # different bad edges? Hard. Instead: is the DIAGONAL part alone (N + diag sumA) enough? No -> need offdiag.
    return dict(mass_ok=mass_ok, diag_neg=len(diag_neg), diagmin=float(diagmin),
                rowmin=float(rowmin), hpsd=hpsd, nbad=len(objs))

def run(nm,n,E):
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
    if not cand: return
    gm=min(g for _,g in cand)
    for s,g in cand:
        if g!=gm: continue
        d=analyze(adj,s,n)
        if d is None: continue
        print(f"  {nm} N={n}: nbad={d['nbad']} mass(m_f=ell)={d['mass_ok']} "
              f"diag(N+sumA) min={d['diagmin']:+.3f} (#neg={d['diag_neg']}) rowmin={d['rowmin']:+.3f} H>=0={d['hpsd']}",flush=True)
        break

if __name__=="__main__":
    from _bdef_construct import Cn, mycielski
    print("=== ANGLE C: is the diagonal of H=N I+sum_f A_f already <0? (=> off-diag Dirichlet sharing essential) ===")
    cur=(5,Cn(5)); run("C5",*cur)
    for t in (2,3):
        nn=5*t; EE=[(i*t+a,((i+1)%5)*t+b) for i in range(5) for a in range(t) for b in range(t)]
        run(f"C5[{t}]",nn,EE)
    cur=(5,Cn(5)); cur=mycielski(*cur); run("Grotzsch",cur[0],cur[1]); cur=mycielski(*cur); run("Myc2(C5)N23",cur[0],cur[1])
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); run(g6,n,E)
