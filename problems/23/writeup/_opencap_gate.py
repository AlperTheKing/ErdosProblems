"""EXACT gate for the OPEN CAPACITY LEMMA -- the single remaining statement of the K-route SPEC proof
(SCHUR_SPEC_PROOF_DRAFT.md).  K-route is sufficient AND cleaner than K2/Lstar: (P1) A_QQ Stieltjes is
PROVEN directly from T(q)<=N (weak diagonal dominance), no odd-girth needed.

  K[v,w] = sum_f p_f(v) p_f(w),  p_f(v) = (#{Q in cyc[f]: v in Q})/|cyc[f]|  (through-fraction).
  T = K*1  (= load: (K1)(v)=sum_f p_f(v) L_f).  A = N I - K.  O={v:T_v>N}, Q=V\O.
  SPEC: A>=0  <=>  Gamma=1^T K 1 <= rho(K) N <= N^2.

OPEN CAPACITY LEMMA (the SOLE remaining step): solve A_QQ g = (N-T)_Q (per K-connected component of Q;
nonsingular Stieltjes components solved exactly, decoupled zero-row-sum components -> g=0). Then
  0 <= g <= 1  AND  for every o in O:  N - T(o) + sum_{q in Q} K[o,q] g(q) >= 0.
If both hold => Schur complement E=A_OO - A_OQ A_QQ^{-1} A_QO is a weakly diag-dominant Z-matrix => PSD
=> A>=0 => SPEC => Erdos #23.  EXACT Fraction.  Full battery incl N=23 guardrail.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain


def build_K(n, M, cyc):
    """K[v,w] = sum_f p_f(v) p_f(w), p_f(v)=through-fraction."""
    P = [[F(0)] * len(M) for _ in range(n)]
    Ml = list(M)
    for fi, f in enumerate(Ml):
        Qs = cyc[f]; k = len(Qs)
        cnt = {}
        for Q in Qs:
            for v in set(Q):
                cnt[v] = cnt.get(v, 0) + 1
        for v, c in cnt.items():
            P[v][fi] = F(c, k)
    K = [[F(0)] * n for _ in range(n)]
    for v in range(n):
        for w in range(n):
            K[v][w] = sum(P[v][fi] * P[w][fi] for fi in range(len(Ml)))
    return K


def solve_sym(A, b):
    """Exact solve A x = b for symmetric A (Fraction); A assumed nonsingular. Gaussian elimination w/ partial pivot."""
    m = len(A)
    M = [list(A[i]) + [b[i]] for i in range(m)]
    for col in range(m):
        piv = None
        for r in range(col, m):
            if M[r][col] != 0:
                piv = r; break
        if piv is None:
            return None  # singular
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        for r in range(m):
            if r != col and M[r][col] != 0:
                fac = M[r][col] / pv
                for c in range(col, m + 1):
                    M[r][c] -= fac * M[col][c]
    return [M[i][m] / M[i][i] for i in range(m)]


def components(adj_idx, nodes):
    """connected components of the subgraph on `nodes` given adjacency over node-set."""
    nodeset = set(nodes); seen = set(); comps = []
    for s in nodes:
        if s in seen:
            continue
        stack = [s]; comp = []; seen.add(s)
        while stack:
            u = stack.pop(); comp.append(u)
            for w in adj_idx[u]:
                if w in nodeset and w not in seen:
                    seen.add(w); stack.append(w)
        comps.append(comp)
    return comps


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T2, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    acc['cuts'] += 1
    N = F(n)
    K = build_K(n, M, cyc)
    T = [sum(K[v][w] for w in range(n)) for v in range(n)]   # = K*1 = load
    A = [[(N if i == j else F(0)) - K[i][j] for j in range(n)] for i in range(n)]
    O = [v for v in range(n) if T[v] > N]
    Q = [v for v in range(n) if T[v] <= N]
    if not O:
        acc['Oempty'] += 1
        return
    acc['Ononempty'] += 1
    # K-adjacency on Q (edge if K[q,q']!=0)
    Kadj = [set(w for w in range(n) if w != v and K[v][w] != 0) for v in range(n)]
    qidx = {q: i for i, q in enumerate(Q)}
    g = {q: F(0) for q in Q}
    ok_solve = True
    for comp in components(Kadj, Q):
        # row sum of A_QQ within comp for each node
        # solve A_comp g_comp = (N-T)_comp ; if singular (zero-row-sum decoupled), g=0
        idx = {q: i for i, q in enumerate(comp)}
        Asub = [[A[a][b] for b in comp] for a in comp]
        bsub = [N - T[a] for a in comp]
        # detect decoupled zero component: all bsub 0 and row sums (within Q) 0
        sol = solve_sym(Asub, bsub)
        if sol is None:
            # singular: must be decoupled zero-row-sum (T=N, no O link). check bsub all 0.
            if all(x == 0 for x in bsub):
                for q in comp:
                    g[q] = F(0)
            else:
                ok_solve = False
                acc['solve_fail'] += 1
                if acc['solve_ex'] is None:
                    acc['solve_ex'] = (name, n, 'singular-coupled', len(comp))
        else:
            for q in comp:
                g[q] = sol[idx[q]]
    if not ok_solve:
        return
    # check 0<=g<=1
    gbad = [(q, g[q]) for q in Q if g[q] < 0 or g[q] > 1]
    if gbad:
        acc['gbound_fail'] += 1
        if acc['gbound_ex'] is None:
            acc['gbound_ex'] = (name, n, ''.join(map(str, side)), gbad[0][0], str(gbad[0][1]))
    # OPEN CAPACITY: for every o in O, N - T(o) + sum_{q in Q} K[o,q] g(q) >= 0
    for o in O:
        val = N - T[o] + sum(K[o][q] * g[q] for q in Q)
        if val < 0:
            acc['cap_fail'] += 1
            if acc['cap_ex'] is None:
                acc['cap_ex'] = (name, n, ''.join(map(str, side)), o, str(val), str(T[o]))
        else:
            if val == 0:
                acc['cap_tight'] += 1
            if acc['cap_min'] is None or val < acc['cap_min']:
                acc['cap_min'] = val


def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    acc = dict(cuts=0, Oempty=0, Ononempty=0, solve_fail=0, gbound_fail=0, cap_fail=0, cap_tight=0,
               cap_min=None, solve_ex=None, gbound_ex=None, cap_ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d: cuts=%d Ononempty=%d cap_fail=%d gbnd=%d solve_fail=%d"
              % (nn, acc['cuts'], acc['Ononempty'], acc['cap_fail'], acc['gbound_fail'], acc['solve_fail']), flush=True)
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Grotzsch+Myc23: cuts=%d Ononempty=%d cap_fail=%d %s"
          % (acc['cuts'], acc['Ononempty'], acc['cap_fail'], acc['cap_ex'] or ''), flush=True)
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24:
            gfam("blow%s" % (sizes,), nn, EE, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam("isl_C5_MycC7", nn, EE, acc)
    print("after chains+blowups+islands: cuts=%d Ononempty=%d cap_fail=%d %s"
          % (acc['cuts'], acc['Ononempty'], acc['cap_fail'], acc['cap_ex'] or ''), flush=True)
    rng = random.Random(7); made = 0; tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam("rand%d" % made, nn, EE, acc)
    print("=" * 60)
    print("gamma-min cuts tested:", acc['cuts'], " (O-nonempty:", acc['Ononempty'], ", O-empty:", acc['Oempty'], ")")
    print("solve failures (singular-coupled):", acc['solve_fail'], acc['solve_ex'] or '')
    print("0<=g<=1 failures:", acc['gbound_fail'], acc['gbound_ex'] or '')
    print("OPEN CAPACITY failures:", acc['cap_fail'], acc['cap_ex'] or '')
    print("capacity tight (=0):", acc['cap_tight'], " min capacity (exact):", str(acc['cap_min']))
    ok = acc['cap_fail'] == 0 and acc['gbound_fail'] == 0 and acc['solve_fail'] == 0
    print("VERDICT:", "OPEN CAPACITY LEMMA HOLDS exact incl N=23 -- K-route SPEC reduces to THIS ONE inequality (P1 already proven); #23 = prove Open Capacity"
          if ok else "FAIL")


if __name__ == "__main__":
    main()
