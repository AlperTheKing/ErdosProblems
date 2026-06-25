import sys
sys.path.insert(0, '.')
exec(open('ref_sublemma_check.py').read().split('if __name__')[0])
import verify_bridge_QFC25 as vb

# The colleague's "Cauchy chain (the constant 25 explicit)" claims:
#   (a) sum_v lambda_v = sum_M ell - t =: L  (interior length)
#   (b) sum_v deg(v) lambda_v <= n*L/2  (cycle-degree (6) applied to layered structure)
#   (c) 2 lambda_v <= deg(v)  (the sub-lemma)  => sum lam^2 <= (1/2) sum deg*lam <= nL/4
#   (d) Cauchy: (sum lam)^2 <= n * sum lam^2 => (t+L)^2 <= n*(nL/4)
#   wait the colleague writes (sum lam) = L not t+L in (a). Both versions appear. Check.
#
# We test each link numerically on the named instances to see which are even TRUE,
# independent of whether the sub-lemma (c) holds.

def fulltrace(N, A, label):
    adj = adjset(N, A)
    E = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(u, v) for (u, v) in E if side[u] == side[v]]
    adjB = [set() for _ in range(N)]
    for (u, v) in E:
        if side[u] != side[v]:
            adjB[u].add(v)
            adjB[v].add(u)
    lam = [0.0] * N
    L1 = 0.0
    Gamma = 0.0
    t_cnt = len(M)
    for (u, v) in M:
        du = blayers(N, adjB, u)
        d = du[v]
        ell = d + 1
        L1 += ell
        Gamma += ell * ell
        t = geoflow(N, adjB, u, v, d)
        for x in range(N):
            lam[x] += t[x]
    deg = [len(adj[u]) for u in range(N)]
    SL = sum(lam)
    E2 = sum(l * l for l in lam)
    L_interior = L1 - t_cnt  # sum ell - t
    sum_deg_lam = sum(deg[v] * lam[v] for v in range(N))
    print(f"{label:12s} N={N} t={t_cnt} L1(sum ell)={L1:.1f}")
    # (a) which holds: sum lam == L1  or  sum lam == L1 - t ?
    print(f"  (a) sum_v lam = {SL:.2f};  L1={L1:.1f};  L1-t={L_interior:.1f}  "
          f"[colleague says both 'sum lam = L1' AND 'sum lam = sum ell - t' in different lines]")
    # (b) cycle-degree aggregate: sum deg*lam <= n*L/2  -- test with L=L1 and L=L1-t
    print(f"  (b) sum deg*lam = {sum_deg_lam:.2f};  n*L1/2={N*L1/2:.1f} (ok={sum_deg_lam<=N*L1/2+1e-9}); "
          f"n*(L1-t)/2={N*L_interior/2:.1f} (ok={sum_deg_lam<=N*L_interior/2+1e-9})")
    # (c+b) => E2 <= (1/2) sum deg lam  (needs sub-lemma). test the consequence E2<=nL/4 directly:
    print(f"  (c) E2={E2:.2f}; (1/2)sum deg lam = {sum_deg_lam/2:.2f} (E2<= it? {E2<=sum_deg_lam/2+1e-9}); "
          f"n*L1/4={N*L1/4:.1f} (E2<=? {E2<=N*L1/4+1e-9})")
    # final inequality the colleague claims: (t+L)^2 <= n^2 L/4 with s=L/t, t<= n^2 s/(4(s+1)^2)
    # using SL = sum lam as 'L' (=L1 in their (a)); s = L1/t
    s = L1 / t_cnt
    rhs_t = N * N * s / (4 * (s + 1) ** 2)
    print(f"  final claim t <= n^2 s/(4(s+1)^2): s=L1/t={s:.3f}, rhs={rhs_t:.2f}, actual t={t_cnt} "
          f"(holds? {t_cnt <= rhs_t + 1e-9})")
    print()


for (N, A, lab) in [(*vb.petersen(), "Petersen"), (*vb.gpt_k23(), "K23-N13"),
                    (*vb.c5n(1), "C5[1]"), (*vb.c5n(2), "C5[2]"), (*vb.c5n(4), "C5[4]")]:
    fulltrace(N, A, lab)
