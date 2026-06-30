"""ADVERSARIAL TASK Family #2: NEAR-EXTREMAL perturbations of C5[t]/C7[t].
Try to BREAK the LRS certificate family {B2, PATH-LRS, ROW-LRS, LRS}.
Add/remove a few edges or unbalance parts so |M| stays near N^2/25 but load T concentrates
above N at some vertices.  For EACH candidate:
  1. compute gamma-min connected-B max cut struct (struct_for_side over the parity cut + all maxcut_all cuts)
  2. CP-SAT GLOBAL-max verify: the cut's parity cutsize == true global max (cp_model).  A breaker counts
     ONLY on a CP-SAT-verified triangle-free connected-B GLOBAL-max cut.
  3. evaluate all four forms EXACTLY (Fraction):
       B2:       max_v T(v) <= 2N
       LRS:      sum_v T(T-N) <= Gamma*(N^2/25 - |M|)              [RHS_LRS = Gamma*(N + N^2/25 - |M|) - N*sum T]
       ROW-LRS:  for each bad edge f:  A_f + |M| <= N + N^2/25,  A_f = (1/ell_f) sum_v p_f(v) T(v)
       PATH-LRS: for each bad edge f, each shortest geo path P: A_{f,P} + |M| <= N + N^2/25,
                 A_{f,P} = (1/ell_f) sum_{v in P} T(v)
  Report tightest (smallest) margin per form.  A form is BROKEN iff margin<0 on a CP-SAT global-max cut.
Run from E:/Projects/ErdosProblems/problems/23/writeup.  EXACT Fraction only."""
from fractions import Fraction as F
from collections import deque
import itertools
from _h import dec, maxcut_all, Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side
from ortools.sat.python import cp_model

# ---------- global-max via CP-SAT ----------
def cpmax(n, edges, tl=30):
    m = cp_model.CpModel()
    x = [m.NewBoolVar("x%d" % i) for i in range(n)]
    t = []
    for a, b in edges:
        z = m.NewBoolVar("e%d_%d" % (a, b))
        m.AddBoolXOr([x[a], x[b], z.Not()])
        t.append(z)
    m.Maximize(sum(t))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl
    st = s.Solve(m)
    optimal = (st == cp_model.OPTIMAL)
    return int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), optimal

def trifree(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]): return False
    return True

# ---------- certificate evaluation for ONE (side) on graph (n,adj,E) ----------
def eval_forms(n, adj, side):
    """Returns None if struct invalid; else dict with the four margins (Fraction; >=0 means holds)."""
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    N = n
    bM = len(M)
    Gamma = sum(ell[f] ** 2 for f in M)
    # p_f(v) = (#geos of f thru v)/(#geos of f)
    pf = {}
    for f in M:
        Ps = cyc[f]; k = len(Ps)
        d = {}
        for P in Ps:
            for v in P: d[v] = d.get(v, 0) + 1
        pf[f] = {v: F(c, k) for v, c in d.items()}
    rhs_local = F(N) + F(N * N, 25)        # N + N^2/25
    # B2
    maxT = max(T)
    b2_margin = F(2 * N) - maxT
    # LRS:  sum_v T(T-N) <= Gamma*(N^2/25 - |M|)
    lhs_lrs = sum(t * (t - N) for t in T)
    rhs_lrs = Gamma * (F(N * N, 25) - bM)
    lrs_margin = rhs_lrs - lhs_lrs
    # ROW-LRS per f:  A_f + |M| <= N + N^2/25
    row_min = None; row_wit = None
    for f in M:
        Af = sum(pf[f].get(v, F(0)) * T[v] for v in pf[f]) / ell[f]
        marg = rhs_local - (Af + bM)
        if row_min is None or marg < row_min: row_min = marg; row_wit = (f, Af)
    # PATH-LRS per (f, path P): A_{f,P}=(1/ell)sum_{v in P} T(v)
    path_min = None; path_wit = None
    for f in M:
        for P in cyc[f]:
            Afp = sum(T[v] for v in P) / ell[f]
            marg = rhs_local - (Afp + bM)
            if path_min is None or marg < path_min: path_min = marg; path_wit = (f, tuple(P), Afp)
    return dict(N=N, bM=bM, Gamma=Gamma, maxT=maxT, b2=b2_margin,
                lrs=lrs_margin, row=row_min, row_wit=row_wit,
                path=path_min, path_wit=path_wit,
                ratio_bM=F(bM) / F(N * N, 25))  # |M| / (N^2/25)

def gamma_min_cuts(n, E):
    """All connected-B max cuts that achieve the gamma-min, with their gammas. Returns (adj, [sides], gm)."""
    adj = [set() for _ in range(n)]
    for a, b in E: adj[a].add(b); adj[b].add(a)
    cand = []
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side): continue
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        if not M: continue
        G = 0; ok = True
        for (u, v) in M:
            d = bdist_restr(adj, side, u, v)
            if d < 0: ok = False; break
            G += (d + 1) ** 2
        if ok: cand.append((side, G))
    if not cand: return adj, [], None
    gm = min(g for _, g in cand)
    return adj, [s for s, g in cand if g == gm], gm

WORST = {}  # form -> (margin, label, data)
def record_worst(form, margin, label, data):
    if form not in WORST or margin < WORST[form][0]:
        WORST[form] = (margin, label, data)

# tightest NON-extremal (Gamma != N^2, i.e. not a perfect C5[t]) global-max witness per form
WORST_NX = {}
def record_worst_nx(form, margin, label, data):
    if form not in WORST_NX or margin < WORST_NX[form][0]:
        WORST_NX[form] = (margin, label, data)

STATS = {'graphs': 0, 'global_cuts': 0, 'high_ratio_global': 0}  # high_ratio: |M|>=0.8*N^2/25
BREAKERS = []

def test_graph(name, n, E, verbose=False, nmax=18):
    if n > nmax:
        if verbose: print(f"  [{name}] N={n}>{nmax}, maxcut_all too slow, skip")
        return
    adj, sides, gm = gamma_min_cuts(n, E)
    if not sides:
        if verbose: print(f"  [{name}] no connected-B max cut with bad edges");
        return
    if not trifree(n, adj):
        if verbose: print(f"  [{name}] NOT triangle-free, skip")
        return
    # maxcut_all already brute-forces ALL 2^(n-1) cuts -> the true global max is exact here.
    # Compute the true global max directly (no CP-SAT needed for correctness at this N; we
    # additionally CP-SAT-confirm only when a form is tight, to honor the task's CP-SAT requirement).
    alledges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    truemax_val = -1
    for m in range(1 << (n - 1)):
        s = [(m >> u) & 1 for u in range(n)]
        c = sum(1 for u, v in alledges if s[u] != s[v])
        if c > truemax_val: truemax_val = c
    cpsat_done = False; opt = bound = None; optimal = False
    STATS['graphs'] += 1
    # dedupe identical structs (symmetric cuts give identical margins) -- evaluate one per (margins) signature
    sigs = set()
    printed = 0
    cap = 400  # cap distinct cuts evaluated per graph (symmetric graphs have huge orbits; we want the gamma-min ones)
    for side in sides[:cap] if len(sides) > cap else sides:
        cutsz = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
        # brute-force-exact global max (maxcut_all is exhaustive at this N)
        is_global = (cutsz == truemax_val)
        r = eval_forms(n, adj, side)
        if r is None: continue
        sig = (r['bM'], r['Gamma'], r['b2'], r['lrs'], r['row'], r['path'])
        if sig in sigs: continue
        sigs.add(sig)
        # CP-SAT confirm any potential breaker (margin<0) or near-tight (margin<2) global-max cut
        if is_global and (min(r['b2'], r['lrs'], r['row'], r['path']) < 2) and not cpsat_done:
            opt, bound, optimal = cpmax(n, E); cpsat_done = True
            is_global = (cutsz == opt == bound) and optimal
        label = f"{name} N={n} |M|={r['bM']} Gamma={r['Gamma']} ratio={float(r['ratio_bM']):.3f} global={is_global}"
        if is_global:
            STATS['global_cuts'] += 1
            if r['ratio_bM'] >= F(4, 5): STATS['high_ratio_global'] += 1
            is_perfect = (r['Gamma'] * 25 == n * n)  # perfect C5[t] extremal: Gamma=N^2/... actually Gamma=N^2 when ell=5,|M|=t^2*5? check via maxT
            record_worst('B2', r['b2'], label, r)
            record_worst('LRS', r['lrs'], label, r)
            record_worst('ROW-LRS', r['row'], label, r)
            record_worst('PATH-LRS', r['path'], label, r)
            # non-extremal = not an exactly-tight uniform C5[t] (those have all of lrs,row,path == 0)
            extremal = (r['lrs'] == 0 and r['row'] == 0 and r['path'] == 0)
            if not extremal:
                record_worst_nx('B2', r['b2'], label, r)
                record_worst_nx('LRS', r['lrs'], label, r)
                record_worst_nx('ROW-LRS', r['row'], label, r)
                record_worst_nx('PATH-LRS', r['path'], label, r)
            for form, key in [('B2', 'b2'), ('LRS', 'lrs'), ('ROW-LRS', 'row'), ('PATH-LRS', 'path')]:
                if r[key] < 0:
                    BREAKERS.append((form, label, r))
        if verbose and printed < 4:
            printed += 1
            print(f"  [{name}] cut globalmax={is_global} |M|={r['bM']} Gamma={r['Gamma']} maxT={float(r['maxT']):.3f}(<=2N={2*n}) "
                  f"B2margin={float(r['b2']):.3f} LRSmargin={float(r['lrs']):.4g} "
                  f"ROWmin={float(r['row']):.4f} PATHmin={float(r['path']):.4f}", flush=True)

def test_fixedcut(name, n, E, side, verbose=False):
    """Evaluate the four forms on an EXPLICIT cut `side`; CP-SAT-verify it is a GLOBAL max cut
    (cutsize == opt == bound, optimal). Bypasses 2^(n-1) brute force -> reaches large blow-ups
    where load genuinely concentrates above N. Counts as a breaker only if global-max + tri-free + connected-B."""
    adj = [set() for _ in range(n)]
    for a, b in E: adj[a].add(b); adj[b].add(a)
    if not trifree(n, adj):
        if verbose: print(f"  [{name}] not tri-free, skip"); return
    if not Bconn(n, adj, side):
        if verbose: print(f"  [{name}] cut not connected-B, skip"); return
    cutsz = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
    opt, bound, optimal = cpmax(n, E, tl=60)
    is_global = (cutsz == opt == bound) and optimal
    r = eval_forms(n, adj, side)
    if r is None:
        if verbose: print(f"  [{name}] struct invalid"); return
    label = f"{name} N={n} |M|={r['bM']} Gamma={r['Gamma']} ratio={float(r['ratio_bM']):.3f} global={is_global} cut={cutsz} opt={opt}"
    STATS['graphs'] += 1
    if is_global:
        STATS['global_cuts'] += 1
        if r['ratio_bM'] >= F(4, 5): STATS['high_ratio_global'] += 1
        for form, key in [('B2', 'b2'), ('LRS', 'lrs'), ('ROW-LRS', 'row'), ('PATH-LRS', 'path')]:
            record_worst(form, r[key], label, r)
        extremal = (r['lrs'] == 0 and r['row'] == 0 and r['path'] == 0)
        if not extremal:
            for form, key in [('B2', 'b2'), ('LRS', 'lrs'), ('ROW-LRS', 'row'), ('PATH-LRS', 'path')]:
                record_worst_nx(form, r[key], label, r)
        for form, key in [('B2', 'b2'), ('LRS', 'lrs'), ('ROW-LRS', 'row'), ('PATH-LRS', 'path')]:
            if r[key] < 0: BREAKERS.append((form, label, r))
    if verbose:
        print(f"  [{name}] global={is_global} |M|={r['bM']} ratio={float(r['ratio_bM']):.3f} maxT={float(r['maxT']):.3f}(2N={2*n}) "
              f"B2={float(r['b2']):.3f} LRS={float(r['lrs']):.4g} ROW={float(r['row']):.4f} PATH={float(r['path']):.4f}", flush=True)

def canon_C5_cut(sizes):
    """Canonical 2-coloring of C5 blow-up: side[part i] = i%2; part 4 lands same parity as part 0 (the bad-edge pair)."""
    n = sum(sizes); start = [0]*5
    for i in range(1, 5): start[i] = start[i-1] + sizes[i-1]
    side = [0]*n
    for i in range(5):
        for j in range(sizes[i]): side[start[i]+j] = i % 2
    return side

# ---------- constructions: near-extremal C5[t]/C7[t] perturbations ----------
def Cm_blowup_edges(m, sizes):
    """C_m blow-up with given part sizes. Returns n, E (no side -- gamma_min_cuts finds the cut)."""
    n = sum(sizes)
    start = [0] * m
    for i in range(1, m): start[i] = start[i - 1] + sizes[i - 1]
    E = []
    for i in range(m):
        j = (i + 1) % m
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                E.append((start[i] + a, start[j] + b))
    return n, E, start

if __name__ == "__main__":
    print("=== LRS BREAK family #2: near-extremal C5[t]/C7[t] perturbations ===", flush=True)
    print("--- baseline uniform C5[t], C7[t] (sanity: extremal, exactly tight) ---", flush=True)
    for t in range(1, 4):
        n, E, _ = Cm_blowup_edges(5, [t]*5)
        test_graph(f"C5[{t}]", n, E, verbose=True)
    for t in range(1, 3):
        n, E, _ = Cm_blowup_edges(7, [t]*7)
        test_graph(f"C7[{t}]", n, E, verbose=True)

    print("--- UNBALANCED C5 blow-ups (concentrate load) ---", flush=True)
    seen = set()
    for sizes in itertools.product(range(1, 6), repeat=5):
        if sum(sizes) > 22: continue
        key = min(tuple(sizes[i:]+sizes[:i]) for i in range(5))  # rotation canonical
        if key in seen: continue
        seen.add(key)
        n, E, _ = Cm_blowup_edges(5, list(sizes))
        test_graph(f"C5{sizes}", n, E)
    print(f"  tested {len(seen)} unbalanced C5 blow-ups", flush=True)

    print("--- UNBALANCED C7 blow-ups ---", flush=True)
    seen7 = set()
    cnt = 0
    for sizes in itertools.product(range(1, 4), repeat=7):
        if sum(sizes) > 20: continue
        key = min(tuple(sizes[i:]+sizes[:i]) for i in range(7))
        if key in seen7: continue
        seen7.add(key); cnt += 1
        n, E, _ = Cm_blowup_edges(7, list(sizes))
        test_graph(f"C7{sizes}", n, E)
    print(f"  tested {cnt} unbalanced C7 blow-ups", flush=True)

    print("--- EDGE-REMOVAL perturbations of C5[t] (remove single cross edges) ---", flush=True)
    for t in [2, 3, 4]:
        n, E0, _ = Cm_blowup_edges(5, [t]*5)
        for k in range(min(len(E0), 8)):
            E = E0[:k] + E0[k+1:]
            test_graph(f"C5[{t}]-e{k}", n, E)
    print("  done edge-removal", flush=True)

    print("--- EDGE-ADD perturbations: add a chord inside a C5[t] (keep tri-free) ---", flush=True)
    # add an edge between part i and part i+2 (distance-2 parts) -- may create triangle; tri-free filter handles it
    for t in [2, 3]:
        n, E0, start = Cm_blowup_edges(5, [t]*5)
        for (pi, pj) in [(0, 2), (1, 3), (0, 3)]:
            E = list(E0) + [(start[pi], start[pj])]
            test_graph(f"C5[{t}]+chord{pi}-{pj}", n, E)
    print("  done edge-add", flush=True)

    print("--- LARGE asymmetric C5 blow-ups via FIXED canonical cut + CP-SAT global verify ---", flush=True)
    print("    (load-concentrators: enlarge some parts; |M| near N^2/25; check T>N regime)", flush=True)
    # historically load-concentrating shapes (STAR-O1 killer was C5(1,48,6,8,48))
    large_shapes = [
        (1,48,6,8,48),(1,40,5,7,40),(2,30,4,6,30),(1,20,3,4,20),(1,10,2,3,10),
        (5,5,5,5,5),(6,6,6,6,6),(4,6,4,6,4),(3,7,3,7,3),(2,8,2,8,2),
        (1,9,1,9,1),(10,10,10,10,10),(8,12,8,12,8),(1,1,1,1,30),(1,1,30,1,1),
        (1,25,1,25,1),(2,20,2,20,2),(3,15,3,15,3),(1,30,1,1,30),(30,1,30,1,1),
        (1,50,1,50,1),(1,12,12,12,1),(12,1,12,1,12),(1,18,4,18,1),
    ]
    for sizes in large_shapes:
        n, E, _ = Cm_blowup_edges(5, list(sizes))
        side = canon_C5_cut(sizes)
        test_fixedcut(f"C5{sizes}", n, E, side, verbose=True)
    # also re-confirm uniform extremal at larger t via fixed cut (must stay margin 0 / global)
    for t in [4, 5, 6, 8, 10]:
        n, E, _ = Cm_blowup_edges(5, [t]*5)
        side = canon_C5_cut([t]*5)
        test_fixedcut(f"C5[{t}]fixed", n, E, side, verbose=True)

    print("--- LRS-boundary push: maximize |M|/(N^2/25) on global-max cuts (the LRS slack -> 0 regime) ---", flush=True)
    # exhaustively brute-force small graphs (N<=16) for the HIGHEST-ratio global-max connected-B cut,
    # then report tightest LRS-family margin among those (the genuine danger zone for LRS/ROW/PATH).
    best_ratio = {'ratio': F(0), 'lab': None}
    import subprocess
    from _h import GENG
    for nn in range(7, 12):
        try:
            outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, timeout=120).stdout.split()
        except Exception:
            outg = []
        for g6 in outg:
            n2, E2 = dec(g6)
            test_graph(g6, n2, E2)
        print(f"  census N={nn} done ({len(outg)} graphs); STATS graphs={STATS['graphs']} global={STATS['global_cuts']}", flush=True)

    print("\n=== WORST (tightest) MARGIN per form over CP-SAT global-max cuts ===", flush=True)
    for form in ['B2', 'PATH-LRS', 'ROW-LRS', 'LRS']:
        if form in WORST:
            m, lab, data = WORST[form]
            print(f"  {form}: min margin = {m} = {float(m):.6g}   at {lab}", flush=True)
            if form in ('ROW-LRS',): print(f"        wit f,A_f={data['row_wit']}", flush=True)
            if form in ('PATH-LRS',): print(f"        wit f,P,A={data['path_wit']}", flush=True)
        else:
            print(f"  {form}: no global-max cut sampled", flush=True)

    print("\n=== TIGHTEST NON-EXTREMAL global-max witness per form (not a perfect C5[t]) ===", flush=True)
    for form in ['B2', 'PATH-LRS', 'ROW-LRS', 'LRS']:
        if form in WORST_NX:
            m, lab, data = WORST_NX[form]
            print(f"  {form}: min non-extremal margin = {float(m):.6g}   at {lab}", flush=True)
        else:
            print(f"  {form}: no non-extremal global-max cut sampled", flush=True)

    print(f"\n=== STATS: graphs-with-CPSAT={STATS['graphs']} global-max-cuts-evaluated={STATS['global_cuts']} "
          f"high-ratio(|M|>=0.8*N^2/25)-global={STATS['high_ratio_global']} ===", flush=True)

    print("\n=== BREAKERS (margin<0 on CP-SAT global-max) ===", flush=True)
    if not BREAKERS:
        print("  NONE. No form broken on any CP-SAT-verified global-max cut.", flush=True)
    else:
        for form, lab, r in BREAKERS:
            print(f"  *** {form} BROKEN at {lab}", flush=True)
            print(f"      full: |M|={r['bM']} Gamma={r['Gamma']} maxT={r['maxT']} b2={r['b2']} lrs={r['lrs']} row={r['row']} path={r['path']}", flush=True)
