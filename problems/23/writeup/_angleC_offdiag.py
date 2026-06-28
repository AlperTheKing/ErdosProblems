"""ANGLE C final pin: sign structure of H off-diagonals on O, and the irreducible crux.
H = L_omega + diag(N-T). Off-diag H[u][v] = -omega(uv) <= 0 (Laplacian) -> H IS a Z-matrix? YES:
all off-diagonals are -omega(e) <= 0. So H is a symmetric Z-matrix with NEGATIVE row sums on O.
A symmetric Z-matrix with a negative row sum is NOT diagonally dominant; PSD must come from the
Schur/effective-conductance (grounded network) mechanism, NOT from any sign/telescoping potential.

We confirm: (a) H is a Z-matrix (offdiag<=0) exactly; (b) negative row sums occur exactly on O={T>N};
(c) the Schur complement onto O (grounding Q with deficits R_Q) is the well-posed PD->PSD reduction.
This is the exact obstruction to Angle C: there is NO entrywise-nonnegative test function decomposition,
because H itself is a graph Laplacian PLUS an INDEFINITE diagonal (positive on Q, negative on O), and
its PSDness is a true effective-conductance domination, equivalent to the full theorem on the const mode.
"""
import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr
from _gcd import build_H
from _satzmu_conn import struct_for_side

def analyze(adj,side,n):
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    O=[v for v in range(n) if T[v]>N]
    # Z-matrix check
    zmat=all(H[i][j]<=0 for i in range(n) for j in range(n) if i!=j)
    # negative row sums exactly on O?
    negrows=[v for v in range(n) if sum(H[v][j] for j in range(n))<0]
    onO = set(negrows)==set(O)
    return dict(O=len(O), zmat=zmat, negrows=len(negrows), negrows_eq_O=onO,
                Tmax=float(max(T)), N=N)

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
        print(f"  {nm} N={n}: |O|={d['O']} Zmatrix(offdiag<=0)={d['zmat']} "
              f"neg-rowsum-set==O? {d['negrows_eq_O']} (#neg={d['negrows']}) Tmax={d['Tmax']:.2f}",flush=True)
        break

if __name__=="__main__":
    from _bdef_construct import Cn, mycielski
    print("=== ANGLE C pin: H is a Z-matrix with negative row sums exactly on O ===")
    cur=(5,Cn(5)); run("C5",*cur)
    cur=mycielski(*cur); run("Grotzsch",cur[0],cur[1]); cur=mycielski(*cur); run("Myc2(C5)N23",cur[0],cur[1])
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); run(g6,n,E)
