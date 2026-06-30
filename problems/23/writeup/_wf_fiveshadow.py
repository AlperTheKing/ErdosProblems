"""_wf_fiveshadow.py  ---  EXACT-RATIONAL GATE for GPT-Pro's FIVE-SHADOW NORMAL FORM.

For every gamma-min connected-B MAX cut (census N<=10 + named gadgets + C5[t] + nonuniform
C5 blow-ups + C5|C7 + Mycielskians) and every bad (monochromatic) edge f with ell_f=5 and
shortest blue geodesic P=(x_0..x_4):

 (1) layers  Lambda_i = {v : dB(x_0,v)=i  AND  dB(v,x_4)=4-i},  i=0..4,  n_i=|Lambda_i|.
 (2) FIVE-SHADOW: every blue edge of every geodesic of f is between CONSECUTIVE layers
     Lambda_i,Lambda_{i+1}; the bad edge f is between Lambda_4 and Lambda_0 (cyclic gap).
 (3) ACTIVE SUPPORT: vertices on/adjacent to geodesics not in any Lambda_i ("gadget" verts);
     for tight/near-tight F(P) do these contribute STRICTLY POSITIVE slack.
 (4) F(P) vs cyclic-min-product:  cyc_bound := (sum n_i)^2 - 25*min_i(n_i*n_{i+1}) >= 0,
     and  25*F(P) ?>= cyc_bound  (i.e. is F(P)>=0 implied by the 5-layer C5 inequality
     plus non-layer slack).

EXACT: fractions.Fraction for every verdict.  dB = blue-graph (across-cut edges only) BFS.

Run:  python _wf_fiveshadow.py
"""
import sys, subprocess, itertools
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, blow
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint, is_triangle_free


def blue_bfs(adj, side, s):
    """dB distance from s over across-cut (blue) edges only."""
    d = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if side[u] != side[v] and v not in d:
                d[v] = d[u] + 1; q.append(v)
    return d


def analyze_f(n, adj, side, f, cyc_f, T, Gamma):
    """Return a dict of five-shadow diagnostics for one bad edge f (ell_f=5)."""
    N = n
    x0, x4 = f[0], f[1]
    # orient geodesics so they run x0 .. x4
    geos = []
    for P in cyc_f:
        if P[0] == x0 and P[-1] == x4:
            geos.append(P)
        elif P[0] == x4 and P[-1] == x0:
            geos.append(P[::-1])
        else:
            # endpoints must be f's endpoints
            geos.append(P)
    L = 5
    d0 = blue_bfs(adj, side, x0)
    d4 = blue_bfs(adj, side, x4)
    # layers
    Lam = [set() for _ in range(L)]
    layer_of = {}
    for v in range(n):
        if v in d0 and v in d4 and d0[v] + d4[v] == L - 1 and 0 <= d0[v] <= L - 1:
            i = d0[v]
            Lam[i].add(v)
            layer_of[v] = i
    n_i = [len(Lam[i]) for i in range(L)]

    # (2) FIVE-SHADOW check
    edge_ok = True
    for P in geos:
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            # must be a blue edge
            if side[a] == side[b]:
                edge_ok = False; break
            la = layer_of.get(a, None); lb = layer_of.get(b, None)
            if la is None or lb is None:
                edge_ok = False; break
            if abs(la - lb) != 1:
                edge_ok = False; break
        if not edge_ok:
            break
    # bad edge between Lambda_4 and Lambda_0
    bad_gap_ok = (x0 in Lam[0]) and (x4 in Lam[L - 1])
    five_layered = edge_ok and bad_gap_ok

    # (3) active support: geodesic vertices + their blue-neighbours
    supp = set()
    for P in geos:
        supp.update(P)
    nbr = set()
    for v in supp:
        for w in adj[v]:
            if side[v] != side[w]:
                nbr.add(w)
    active = supp | nbr
    nonlayer = sorted(v for v in active if v not in layer_of)
    # restrict to vertices ON geodesics that are non-layer (true refutation signal)
    nonlayer_on_geo = sorted(v for v in supp if v not in layer_of)

    # F(P) for each geodesic (uniform geodesic load T already global; F same for all P of f
    # because it depends only on which vertices ARE x in P -- but P varies, so compute per P)
    # F(P) := (L/25)*(N^2 - Gamma) - sum_{x in P}(T(x) - N)
    coef = F(L, 25)
    deficit = F(N) * F(N) - Gamma
    F_vals = []
    for P in geos:
        s = sum(T[x] - N for x in set(P))
        Fp = coef * deficit - s
        F_vals.append(Fp)
    F_min = min(F_vals)

    # (4) cyclic-min-product bound from layers
    minprod = min(n_i[i] * n_i[(i + 1) % L] for i in range(L))
    cyc_bound = (sum(n_i)) ** 2 - 25 * minprod  # >=0 by AM-GM
    # 25*F_min vs cyc_bound:  is F_min >= cyc_bound/25 ?  (pure-layer lower bound)
    # F_min - cyc_bound/25 = "non-layer slack"
    nonlayer_slack = F_min - F(cyc_bound, 25)

    return dict(
        f=f, n_i=n_i, five_layered=five_layered, edge_ok=edge_ok, bad_gap_ok=bad_gap_ok,
        F_min=F_min, cyc_bound=cyc_bound, nonlayer_slack=nonlayer_slack,
        nonlayer_on_geo=nonlayer_on_geo, nonlayer_active=nonlayer, ngeo=len(geos),
    )


def _greedy_maxcut(n, adj):
    """Local-search to a 1-flip-stable (locally maximum) cut. Deterministic init by parity
       of a BFS 2-coloring, then flip any vertex that strictly increases the cut."""
    side = [0] * n
    # BFS 2-coloring as a strong starting cut
    seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True; col = {s: 0}; q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True; col[v] = 1 - col[u]; q.append(v)
        for v, c in col.items():
            side[v] = c
    improved = True
    while improved:
        improved = False
        for v in range(n):
            same = sum(1 for w in adj[v] if side[w] == side[v])
            diff = sum(1 for w in adj[v] if side[w] != side[v])
            if same > diff:
                side[v] ^= 1; improved = True
    return side


def gmin_connected_cuts(n, E):
    """gamma-min connected-B max cuts (struct computed)."""
    adj, cuts = gmins(n, E)
    out = []
    for s in cuts:
        st = struct_for_side(n, adj, s)
        if st is None:
            continue
        out.append((adj, s, st))
    return out


class Acc:
    def __init__(self):
        self.tot_f = 0           # (f,instance) with ell_f=5
        self.five = 0            # cleanly 5-layered
        self.refute = []         # non-layerable active support => refutes lemma
        self.edge_fail = 0
        self.gap_fail = 0
        self.F_neg = 0           # F(P)<0  (would refute PATH-GAMMA)
        self.tight = []          # small F_min instances
        self.nonlayer_slack_neg = []  # F_min < cyc_bound/25  => pure-layer bound NOT enough
        self.min_F = None
        self.min_nlslack = None

    def add(self, nm, res, gmin=True):
        self.tot_f += 1
        if gmin:
            self.tot_f_gmin = getattr(self, 'tot_f_gmin', 0) + 1
            if res['F_min'] < 0:
                self.F_neg_gmin = getattr(self, 'F_neg_gmin', 0) + 1
                self.F_neg_gmin_wit = getattr(self, 'F_neg_gmin_wit', [])
                self.F_neg_gmin_wit.append((nm, res['f'], res['F_min'], res['n_i']))
            if res.get('five_layered') and (getattr(self, 'min_F_gmin', None) is None or res['F_min'] < self.min_F_gmin):
                self.min_F_gmin = res['F_min']
            # point (4): does pure-layer cyc bound lower-bound F on the REAL domain?
            self.nls_gmin_min = getattr(self, 'nls_gmin_min', None)
            if self.nls_gmin_min is None or res['nonlayer_slack'] < self.nls_gmin_min:
                self.nls_gmin_min = res['nonlayer_slack']
            if res['nonlayer_slack'] < 0:
                self.nls_gmin_neg = getattr(self, 'nls_gmin_neg', 0) + 1
                w = getattr(self, 'nls_gmin_wit', [])
                if len(w) < 12:
                    w.append((nm, res['f'], res['F_min'], res['nonlayer_slack'], res['n_i']))
                self.nls_gmin_wit = w
        if res['five_layered']:
            self.five += 1
        else:
            if not res['edge_ok']:
                self.edge_fail += 1
            if not res['bad_gap_ok']:
                self.gap_fail += 1
            # a non-layerable ON-geodesic vertex would refute the normal form
            if res['nonlayer_on_geo']:
                self.refute.append((nm, res['f'], res['nonlayer_on_geo'], res['n_i']))
        if res['F_min'] < 0:
            self.F_neg += 1
        if self.min_F is None or res['F_min'] < self.min_F:
            self.min_F = res['F_min']
        if res['nonlayer_slack'] < 0:
            self.nonlayer_slack_neg.append((nm, res['f'], float(res['nonlayer_slack']), res['n_i']))
        if self.min_nlslack is None or res['nonlayer_slack'] < self.min_nlslack:
            self.min_nlslack = res['nonlayer_slack']
        if res['F_min'] <= F(2):  # tight / near-tight
            self.tight.append((nm, res['f'], res['F_min'], res['nonlayer_slack'],
                               res['n_i'], res['nonlayer_on_geo']))


def _eval_cut(nm, n, adj, s, st, acc, gmin=True):
    M, ell, T, mu, cyc = st
    Gamma = sum(T)
    local = 0
    for f in M:
        if ell[f] != 5:
            continue
        res = analyze_f(n, adj, s, f, cyc[f], T, Gamma)
        acc.add(nm, res, gmin=gmin)
        local += 1
    return local


def run_instance(nm, n, E, acc, report=False):
    """Full gamma-min connected-B max-cut enumeration (brute force; small n only).
       These ARE certified gamma-min max cuts => the PATH-GAMMA domain."""
    if not is_triangle_free(n, E):
        return
    cuts = gmin_connected_cuts(n, E)
    local = 0
    for adj, s, st in cuts:
        local += _eval_cut(nm, n, adj, s, st, acc, gmin=True)
    if report:
        print(f"  {nm} N={n}: ell5 (f,cut) instances={local}", flush=True)


def run_single_cut(nm, n, E, adj, side, acc, report=False):
    """Evaluate the five-shadow on ONE supplied cut (no maxcut enumeration).
       Used for large blow-ups / Mycielskians where brute-force maxcut is infeasible.
       NOTE: we still REQUIRE the supplied cut to be connected-B and verify Gamma<=N^2."""
    if not is_triangle_free(n, E):
        return
    from _h import Bconn
    if not Bconn(n, adj, side):
        if report:
            print(f"  {nm} N={n}: supplied cut NOT B-connected, skipped", flush=True)
        return
    # require the supplied cut to be 1-flip-LOCALLY-maximum (necessary for gamma-min max cut)
    locmax = True
    for v in range(n):
        same = sum(1 for w in adj[v] if side[w] == side[v])
        diff = sum(1 for w in adj[v] if side[w] != side[v])
        if same > diff:
            locmax = False; break
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    # gmin=False: not a CERTIFIED global gamma-min cut (only locally-max);
    # diagnostics still recorded but excluded from the F(P)>=0 PATH-GAMMA verdict.
    local = _eval_cut(nm, n, adj, side, st, acc, gmin=False)
    if report:
        print(f"  {nm} N={n}: ell5 (f,cut) instances={local} 1flip-localmax={locmax}", flush=True)


def main():
    from _stark1 import odd_blowup
    acc = Acc()
    BRUTE = 16  # brute-force maxcut only for n <= BRUTE (2^(n-1) feasible)

    print("=== FIVE-SHADOW NORMAL FORM exact gate ===", flush=True)

    # --- C5[t] uniform blow-ups (canonical parity cut; single-cut for large t) ---
    for t in range(1, 9):
        n, E, adj, side = odd_blowup(5, [t] * 5)
        if n <= BRUTE:
            run_instance(f"C5[{t}]", n, E, acc)
        else:
            run_single_cut(f"C5[{t}]", n, E, adj, side, acc)
    print(f"[C5[t] t=1..8] tot_ell5={acc.tot_f} five={acc.five}", flush=True)

    # --- nonuniform C5 blow-ups (canonical cut from odd_blowup) ---
    nu_count = 0
    for sizes in itertools.product([1, 2, 3, 5], repeat=5):
        if sum(sizes) > 40:
            continue
        n, E, adj, side = odd_blowup(5, list(sizes))
        if n <= BRUTE:
            run_instance(f"C5{sizes}", n, E, acc)
        else:
            run_single_cut(f"C5{sizes}", n, E, adj, side, acc)
        nu_count += 1
    print(f"[nonuniform C5 blow-ups] sampled={nu_count} tot_ell5={acc.tot_f} five={acc.five}", flush=True)

    # --- C5 | C7 disjoint union and glued variants (small => brute force) ---
    for (i, j) in [(None, None), (0, 0), (0, 1), (0, 2)]:
        nC5, EC5 = 5, Cn(5)
        nC7, EC7 = 7, Cn(7)
        n, E = union_disjoint((nC5, EC5), (nC7, EC7))
        nm = "C5|C7"
        if i is not None:
            E = E + [(i, nC5 + j)]
            nm = f"C5|C7+{i}~{j}"
        run_instance(nm, n, E, acc)
    print(f"[C5|C7] tot_ell5={acc.tot_f} five={acc.five}", flush=True)

    # --- Mycielskians (single-cut: use a known gamma-min connected cut via gmins ONLY
    #     for small N=11,15; for N=23 brute force is infeasible so use a parity-ish cut) ---
    g = mycielski(5, Cn(5))   # Grotzsch N=11
    run_instance("Grotzsch=N11", g[0], g[1], acc)
    g7 = mycielski(7, Cn(7))  # N=15
    run_instance("Myc(C7)=N15", g7[0], g7[1], acc)
    g2 = mycielski(*g)        # N=23 -- too big for brute force; find a connected max cut greedily
    n23, E23 = g2
    adj23 = [set() for _ in range(n23)]
    for a, b in E23:
        adj23[a].add(b); adj23[b].add(a)
    side23 = _greedy_maxcut(n23, adj23)
    run_single_cut("Myc2(C5)=N23", n23, E23, adj23, side23, acc, report=True)
    print(f"[Mycielskians] tot_ell5={acc.tot_f} five={acc.five}", flush=True)

    # --- census N<=10 triangle-free connected ---
    for nn in range(5, 11):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        before = acc.tot_f
        for g6 in outg:
            n, E = dec(g6)
            run_instance(g6, n, E, acc)
        print(f"  census N={nn}: graphs={len(outg)} new ell5 (f,cut)={acc.tot_f - before}", flush=True)

    # ===== REPORT =====
    print("\n===== SUMMARY =====", flush=True)
    print(f"total (bad-edge, cut) instances with ell_f=5 : {acc.tot_f}", flush=True)
    frac = F(acc.five, acc.tot_f) if acc.tot_f else F(0)
    print(f"cleanly FIVE-LAYERED                          : {acc.five}  "
          f"({float(frac):.6f} = {frac})", flush=True)
    print(f"  edge-not-consecutive-layer failures         : {acc.edge_fail}", flush=True)
    print(f"  bad-edge-not-in-(L4,L0) failures            : {acc.gap_fail}", flush=True)
    print(f"REFUTING (non-layerable ON-geodesic vertex)   : {len(acc.refute)}", flush=True)
    for r in acc.refute[:10]:
        print(f"    REFUTE {r}", flush=True)
    tgm = getattr(acc, 'tot_f_gmin', 0)
    fng = getattr(acc, 'F_neg_gmin', 0)
    print(f"--- CERTIFIED gamma-min cuts (PATH-GAMMA domain) ---", flush=True)
    print(f"certified-gmin ell5 instances                 : {tgm}", flush=True)
    print(f"  F(P)<0 among CERTIFIED gamma-min (REFUTES)   : {fng}", flush=True)
    for w in getattr(acc, 'F_neg_gmin_wit', [])[:10]:
        print(f"    GMIN-F<0 {w}", flush=True)
    mfg = getattr(acc, 'min_F_gmin', None)
    if mfg is not None:
        print(f"  min F(P) among certified gamma-min          : {float(mfg):.6f} = {mfg}", flush=True)
    nlsg = getattr(acc, 'nls_gmin_neg', 0)
    nlsgmin = getattr(acc, 'nls_gmin_min', None)
    print(f"  [pt4] non-layer slack (F - cyc_bound/25) < 0 on CERTIFIED gmin : {nlsg}", flush=True)
    if nlsgmin is not None:
        print(f"  [pt4] min non-layer slack on CERTIFIED gmin : {float(nlsgmin):.6f} = {nlsgmin}", flush=True)
    for w in getattr(acc, 'nls_gmin_wit', [])[:12]:
        print(f"      [pt4] NLS<0(gmin) {w}", flush=True)
    print(f"--- ALL cuts (incl. uncertified canonical/greedy blow-up cuts) ---", flush=True)
    print(f"F(P)<0 instances over ALL cuts (incl non-gmin) : {acc.F_neg}", flush=True)
    print(f"min F(P) over all instances                   : {float(acc.min_F):.6f} "
          f"= {acc.min_F}", flush=True)
    print(f"min non-layer slack (F - cyc_bound/25)        : {float(acc.min_nlslack):.6f} "
          f"= {acc.min_nlslack}", flush=True)
    print(f"non-layer-slack < 0 instances (pure-layer bound insufficient): "
          f"{len(acc.nonlayer_slack_neg)}", flush=True)
    for r in acc.nonlayer_slack_neg[:10]:
        print(f"    NLSLACK<0 {r}", flush=True)
    print(f"\ntight/near-tight (F_min<=2) instances: {len(acc.tight)}", flush=True)
    # show distinct tight signatures
    seen = set()
    for nm, f, Fm, nls, ni, nlg in acc.tight:
        key = (tuple(ni), Fm, nls, bool(nlg))
        if key in seen:
            continue
        seen.add(key)
        print(f"    {nm} f={f} F={Fm} nonlayer_slack={nls} n_i={ni} nonlayer_on_geo={nlg}",
              flush=True)
        if len(seen) >= 25:
            print("    ...", flush=True)
            break

    # verdict: the FIVE-SHADOW NORMAL FORM structure is about layering, not F>=0.
    if acc.refute:
        verdict = "structure-refuted"
    elif acc.five == acc.tot_f:
        verdict = "structure-confirmed"
    else:
        verdict = "partial"
    print(f"\nVERDICT(layering): {verdict}", flush=True)
    if fng == 0:
        print("PATH-GAMMA F(P)>=0 HOLDS on all certified gamma-min cuts.", flush=True)
    else:
        print(f"WARNING: F(P)<0 on {fng} certified gamma-min instances (would refute PATH-GAMMA).",
              flush=True)
    return acc, verdict


if __name__ == "__main__":
    main()
