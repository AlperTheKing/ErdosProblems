"""Pin the EXACT obstruction: show the LOCAL data (deficit >=0, rho(K|_C)<=N, K-closed, a saturated
vertex present, a dead boundary B-neighbor) is consistent with a Q-only component -- so no local
energy/Perron argument forbids the C-alltie contrapositive. The only thing forbidding it is GLOBAL
(the gamma-min max-cut structure / NO-Q-ONLY connectivity).

Demonstration: take the real load-bearing component L of J??CBAPFvo? and DELETE the unique O vertex
o*=10 from K (zeroing its row/col). The residual matrix K' on L\{o*} is:
  - entrywise >=0, symmetric, PSD (principal submatrix of PSD K),
  - has the saturated vertex v=9 with K'-row-sum = T(9) - K[9,10] = N - K[9,10] (<=N),
  - and v=9 still has the dead B-neighbor z=5 (z never carried load).
Compute rho(K'), deficit, and check A'=N I - K' is PSD nonsingular. If so, the residual is a
perfectly valid 'critical-free Q-only-like component with a saturated-ish vertex' at the LOCAL
level -- confirming the obstruction is purely global connectivity (the deleted o* is exactly the
link that C-alltie asserts must exist).
Exact Fraction + float Perron.
"""
from fractions import Fraction as F
from _h import dec, loads
from _satzmu_conn import struct_for_side, kcomponents

def buildK(n, cyc):
    K = [[F(0)]*n for _ in range(n)]
    for f, Ps in cyc.items():
        nf = len(Ps)
        cnt = [0]*n
        for P in Ps:
            for v in P: cnt[v] += 1
        pf = [F(cnt[v], nf) for v in range(n)]
        for a in range(n):
            if pf[a] == 0: continue
            for b in range(n):
                if pf[b] == 0: continue
                K[a][b] += pf[a]*pf[b]
    return K

def perron(M, iters=3000):
    m = len(M)
    if m == 0: return 0.0
    Mf = [[float(M[i][j]) for j in range(m)] for i in range(m)]
    x = [1.0+0.01*i for i in range(m)]
    for _ in range(iters):
        y = [sum(Mf[i][j]*x[j] for j in range(m)) for i in range(m)]
        nrm = max(abs(v) for v in y) or 1.0
        x = [v/nrm for v in y]
    Mx = [sum(Mf[i][j]*x[j] for j in range(m)) for i in range(m)]
    num = sum(x[i]*Mx[i] for i in range(m)); den = sum(x[i]*x[i] for i in range(m))
    return num/den

def smallest_eig(A):
    # A symmetric; smallest eigenvalue via inverse-ish: just float numpy-free Jacobi-lite => use power on (cI - A)
    m = len(A); Af = [[float(A[i][j]) for j in range(m)] for i in range(m)]
    c = max(sum(abs(Af[i][j]) for j in range(m)) for i in range(m)) + 1.0
    B = [[(c if i == j else 0.0) - Af[i][j] for j in range(m)] for i in range(m)]
    lam_max_B = perron(B)
    return c - lam_max_B

if __name__ == "__main__":
    g6 = "J??CBAPFvo?"
    n, E = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in E: adj[a].add(b); adj[b].add(a)
    # use the gamma-min cut with the C-alltie case
    from _h import maxcut_all, Bconn, bdist_restr
    side = [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0]
    st = struct_for_side(n, adj, side)
    M, ell, T, mu, cyc = st; N = n
    O = [v for v in range(N) if T[v] > N]
    K = buildK(n, cyc)
    comp, find = kcomponents(n, cyc)
    L = sorted(comp[find(9)])
    print(f"K-comp L of v=9: {L}, O={O}, sat v=9 T={float(T[9])}, dead z=5 T={float(T[5])}")
    # full L
    subL = [[K[i][j] for j in L] for i in L]
    rhoL = perron(subL)
    print(f"rho(K|_L) ~ {rhoL:.4f}   (N={N})  -- contains O so can exceed... rowsum_max={float(max(sum(K[i][j] for j in L) for i in L)):.3f}")
    # delete o*=10
    Lq = [v for v in L if v not in O]
    subQ = [[K[i][j] for j in Lq] for i in Lq]
    rhoQ = perron(subQ)
    rowsums = [sum(K[i][j] for j in Lq) for i in Lq]
    deficit = sum(N - rs for rs in rowsums)
    AQ = [[(N if i == j else 0) - subQ[i][j] for j in range(len(Lq))] for i in range(len(Lq))]
    mineig = smallest_eig(AQ)
    print(f"\nResidual K' on L\\O = {Lq}:")
    print(f"  rho(K') ~ {rhoQ:.4f}  <= N={N}? {rhoQ < N + 1e-6}")
    print(f"  v=9 row-sum in K' = {float(rowsums[Lq.index(9)]):.4f}  (was N={N}; lost K[9,10]={float(K[9][10]):.4f})")
    print(f"  deficit(K') = sum(N - rowsum) = {float(deficit):.4f}  (>=0)")
    print(f"  A' = N I - K' smallest eig ~ {mineig:.4f}  PSD-nonsingular? {mineig > 1e-6}")
    print(f"  z=5 still B-adjacent to v=9? {5 in adj[9]}  (dead, K'-isolated: row sum {float(sum(K[5][j] for j in Lq))})")
    print("\n=> The LOCAL data of a Q-only component with a (near-)saturated vertex + dead B-neighbor")
    print("   is fully consistent (A' PSD-nonsingular, deficit>=0). The ONLY thing that makes v=9")
    print("   actually saturated (T=N) is the deleted K-link to o*=10 in O. That link IS the")
    print("   C-alltie conclusion. No local argument recovers it; the obstruction is GLOBAL.")
