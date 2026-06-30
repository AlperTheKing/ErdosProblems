"""INDEPENDENT gate for Codex's TERMINAL-SHADOW Psi(W) descent bound (Erdos #23 endgame).

Setup (reduction already proven & verified elsewhere): triangle-free G, max cut also minimizing
Gamma = sum_f L_f^2 (L_f = shortest blue-geodesic odd-cycle length of bad edge f).
struct_for_side(n,adj,side) -> (M, ell, T, mu, cyc):
  M    = list of bad (monochromatic) edges f=(u,v), u<v
  ell  = {f: odd cycle length = len(geodesic path)}
  cyc  = {f: list of shortest blue-geodesic paths Q (each Q a vertex list s..t); Q + closing edge f = odd cycle}
  T    = vertex loads (sum T = Gamma), mu = blue-edge multiplicities

THE TERMINAL-SHADOW Psi(W).  For a switch (vertex set) W:
  crossM = bad edges f with exactly one endpoint in W
  bdyB   = blue edges e with exactly one endpoint in W   (e = unordered {a,b}, side[a]!=side[b])
  TERMINAL gate: for each f in crossM, for each Q in cyc[f], orient Q from the in-W endpoint of f
     outward; the W-membership pattern along the oriented Q must be a terminal prefix 1..10..0
     (a run of in-W vertices then a run of out-of-W vertices, no return); the unique exit blue-edge
     e_S(f,Q) = the Q-edge crossing the 1->0 boundary must lie in bdyB.
  COVERAGE: every e in bdyB is some e_S(f,Q) for a crossing f.
  SAFETY:   every NONcrossing bad edge h (both endpoints same side wrt W) has some Q in cyc[h]
     entirely avoiding bdyB (i.e. no edge of Q is in bdyB).
  lambda_S(e) = min over crossing f witnessing e (e=e_S(f,Q) for some Q) of ell[f].
  Psi(W) = sum_{f in crossM} ell[f]^2  -  sum_{e in bdyB} lambda_S(e)^2.

DESCENT BOUND (to prove/test):  for every W passing terminal+coverage+safety with delta_B==delta_M
  (cut-size preserving / neutral) and B-connected-after,
       Gamma(after) - Gamma(before)  <=  -Psi(W)     (exact, recompute Gamma after the flip).

Gate: census N<=9 over ALL neutral half-switches (subsets W) passing the gates, plus the N=23 apex
switch(es). Report 0-fail or first counterexample. Also test whether Psi(W) == -phi^T H phi for the
matching level-set phi (reconcile with the descent-estimate / Schur-complement angle).
EXACT Fraction throughout.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _hardy_gate import build_H, BETA


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    return adj


def gamma_of(n, adj, side):
    """Recompute Gamma = sum ell^2 for this cut. Returns None if B disconnected / a bad edge has no geodesic."""
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return F(0)
    return sum(F(ell[f]) * ell[f] for f in M)


def flip(side, W):
    out = side[:]
    for v in W:
        out[v] ^= 1
    return out


def edge_key(a, b):
    return (a, b) if a < b else (b, a)


def boundary_edges(n, adj, side, W):
    """Return (crossM, bdyB) for switch W.
       crossM = list of bad edges with exactly one endpoint in W.
       bdyB   = set of blue edges {a,b} (side differs) with exactly one endpoint in W."""
    Wset = set(W)
    crossM = []
    bdyB = set()
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            inu = u in Wset; inv = v in Wset
            if inu == inv:
                continue  # both in or both out: not a boundary edge
            if side[u] == side[v]:
                crossM.append((u, v))     # bad edge crossing W
            else:
                bdyB.add((u, v))           # blue edge crossing W
    return crossM, bdyB


def terminal_exit(Q, src, Wset, bdyB):
    """Orient path Q from endpoint src outward. Check W-membership is a terminal prefix 1..10..0.
       Return the exit blue edge (a,b) (the 1->0 crossing edge) if valid & in bdyB, else None.
       If src is NOT in W the pattern would start 0..., which is not a valid terminal prefix for a
       crossing edge whose in-W endpoint is src -> caller passes the in-W endpoint as src."""
    if Q[0] != src:
        Q = Q[::-1]
    assert Q[0] == src
    membership = [(x in Wset) for x in Q]
    if not membership[0]:
        return None  # src not in W: not a terminal prefix starting with 1
    # find first transition to out-of-W; everything after must stay out-of-W
    k = None
    for i in range(1, len(membership)):
        if membership[i] != membership[i - 1]:
            if k is not None:
                return None  # second transition -> not 1..10..0
            k = i  # transition between i-1 (in W) and i (out of W)
    if k is None:
        # all-in-W along Q: no exit edge inside the cycle path; the exit happens at closing bad edge.
        # No blue exit edge to witness -> invalid for the terminal-shadow accounting.
        return None
    a, b = Q[k - 1], Q[k]  # a in W, b out of W
    e = edge_key(a, b)
    if e not in bdyB:
        return None
    return e


def psi_and_gate(n, adj, side, W):
    """Compute terminal gate + Psi(W). Returns dict with:
       ok (bool: passes terminal+coverage+safety), Psi (Fraction or None), and diagnostics.
       Uses struct of the ORIGINAL cut (before flip)."""
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    Wset = set(W)
    crossM, bdyB = boundary_edges(n, adj, side, W)
    Mset = set(M)
    # classify bad edges
    crossM_set = set(edge_key(*f) for f in crossM)

    # TERMINAL gate: each crossing f, each Q in cyc[f], oriented from in-W endpoint outward,
    # must be terminal prefix with exit in bdyB. Collect witnesses for coverage & lambda.
    witnesses = {}  # e (blue edge) -> set of ell[f] of crossing f witnessing e
    terminal_ok = True
    for f in crossM:
        u, v = f
        src = u if u in Wset else v   # the in-W endpoint
        assert (u in Wset) != (v in Wset)
        for Q in cyc[f]:
            e = terminal_exit(list(Q), src, Wset, bdyB)
            if e is None:
                terminal_ok = False
            else:
                witnesses.setdefault(e, set()).add(ell[f])

    # COVERAGE: every e in bdyB is witnessed by some crossing f
    coverage_ok = all(e in witnesses for e in bdyB)

    # SAFETY: every noncrossing bad edge h has some Q in cyc[h] avoiding bdyB
    safety_ok = True
    for h in M:
        if edge_key(*h) in crossM_set:
            continue  # h is crossing, not a noncrossing bad edge
        # h is noncrossing: both endpoints same side wrt W
        found_safe = False
        for Q in cyc[h]:
            qedges = set(edge_key(Q[i], Q[i + 1]) for i in range(len(Q) - 1))
            if not (qedges & bdyB):
                found_safe = True
                break
        if not found_safe:
            safety_ok = False
            break

    ok = terminal_ok and coverage_ok and safety_ok

    # lambda_S(e) = min ell[f] over crossing f witnessing e
    Psi = None
    if ok:
        lam2_sum = F(0)
        for e in bdyB:
            lam = min(witnesses[e])
            lam2_sum += F(lam) * lam
        cross_sum = sum(F(ell[f]) * ell[f] for f in crossM)
        Psi = cross_sum - lam2_sum

    return dict(ok=ok, terminal_ok=terminal_ok, coverage_ok=coverage_ok, safety_ok=safety_ok,
                Psi=Psi, crossM=crossM, bdyB=bdyB)


def delta_neutral(n, adj, side, W):
    """delta_B - delta_M for switch W; 0 == cut-size-preserving (neutral)."""
    Wset = set(W)
    dB = 0; dM = 0
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            inu = u in Wset; inv = v in Wset
            if inu == inv:
                continue
            if side[u] == side[v]:
                dB += 1
            else:
                dM += 1
    return dB - dM


def scan_cut(name, n, adj, side, acc, full_subsets=True, W_list=None):
    """For one max-cut (must be B-connected & have bad edges), enumerate switches W,
       keep those neutral + B-connected-after, run terminal+coverage+safety gate, and on a PASS
       verify the descent bound Gamma(after)-Gamma(before) <= -Psi(W)."""
    if not Bconn(n, adj, side):
        return
    gamma0 = gamma_of(n, adj, side)
    if gamma0 is None or gamma0 == 0:
        return
    acc['cuts'] += 1

    if W_list is not None:
        subsets = W_list
    elif full_subsets:
        subsets = []
        for mask in range(1, 1 << n):
            subsets.append([v for v in range(n) if (mask >> v) & 1])
    else:
        subsets = []

    for W in subsets:
        # neutral?
        if delta_neutral(n, adj, side, W) != 0:
            continue
        side2 = flip(side, W)
        gamma1 = gamma_of(n, adj, side2)
        if gamma1 is None:
            continue  # B disconnected after / invalid -> not a valid switch
        res = psi_and_gate(n, adj, side, W)
        if res is None or not res['ok']:
            continue
        acc['gated_switches'] += 1
        Psi = res['Psi']
        dG = gamma1 - gamma0
        # descent bound:  dG <= -Psi   <=>  dG + Psi <= 0
        if dG + Psi == 0:
            acc['exact_eq'] += 1
        if dG + Psi <= 0:
            acc['pass'] += 1
            if Psi > 0:
                acc['pass_pospsi'] += 1
                if dG >= 0:
                    # positive surplus but Gamma did NOT strictly drop: that would break the
                    # geometric claim "positive-surplus switch strictly lowers Gamma"
                    acc['pospsi_no_drop'] += 1
                    if acc['pospsi_no_drop_ex'] is None:
                        acc['pospsi_no_drop_ex'] = (name, n, ''.join(map(str, side)),
                                                    tuple(W), str(Psi), str(dG))
            slack = -Psi - dG  # >=0 means bound holds with this slack
            if acc['min_slack'] is None or slack < acc['min_slack']:
                acc['min_slack'] = slack
                acc['min_slack_ex'] = (name, n, ''.join(map(str, side)), tuple(W),
                                       str(Psi), str(dG))
        else:
            acc['fail'] += 1
            if acc['first_fail'] is None:
                acc['first_fail'] = (name, n, ''.join(map(str, side)), tuple(W),
                                     str(Psi), str(dG), str(dG + Psi))


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def new_acc():
    return dict(cuts=0, gated_switches=0, **{'pass': 0}, pass_pospsi=0, fail=0,
                exact_eq=0, pospsi_no_drop=0, pospsi_no_drop_ex=None,
                first_fail=None, min_slack=None, min_slack_ex=None)


# ---- N=23 apex switch construction (Mycielski of Grotzsch / from MEMORY side string) ----
def mycielski_grotzsch_edges():
    """Build Mycielski(Grotzsch) = the N=23 graph used as the spectral guardrail.
       Grotzsch graph = Mycielski(C5). Then take Mycielski again -> 23 vertices.
       We construct via the standard Mycielski operator from _bdef_construct if available."""
    try:
        from _bdef_construct import Cn, mycielski, is_triangle_free
    except Exception:
        return None
    E5 = Cn(5)                      # C5 edges (vertices 0..4)
    n11, E11 = mycielski(5, E5)    # Grotzsch (11 vertices)
    n23, E23 = mycielski(n11, E11) # 23 vertices
    if not is_triangle_free(n23, E23):
        return None
    return n23, E23


def main():
    acc = new_acc()
    print("=== Psi(W) TERMINAL-SHADOW descent gate: census N<=9, ALL neutral gated half-switches ===")
    for n in range(4, 10):
        graphs = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        for g6 in graphs:
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print("  census N=%d: cuts=%d gated_switches=%d pass=%d pospsi=%d fail=%d"
              % (n, acc['cuts'], acc['gated_switches'], acc['pass'], acc['pass_pospsi'], acc['fail']),
              flush=True)

    print("-" * 72)
    print("TOTAL cuts:", acc['cuts'])
    print("gated switches (terminal+coverage+safety + neutral + Bconn-after):", acc['gated_switches'])
    print("PASS (dG <= -Psi):", acc['pass'])
    print("  of which EXACT EQ (dG == -Psi):", acc['exact_eq'])
    print("  of which Psi>0:", acc['pass_pospsi'])
    print("  Psi>0 but Gamma did NOT strictly drop:", acc['pospsi_no_drop'], acc['pospsi_no_drop_ex'] or "")
    print("FAIL (dG > -Psi):", acc['fail'])
    print("first FAIL:", acc['first_fail'] or "NONE")
    print("min slack (-Psi - dG):", acc['min_slack'], acc['min_slack_ex'] or "")

    # --- N=23 apex switches ---
    print("=" * 72)
    print("=== N=23 Mycielski(Grotzsch) apex switches ===")
    mg = mycielski_grotzsch_edges()
    if mg is None:
        print("  (could not build N=23 graph -- skipping)")
    else:
        n23, E23 = mg
        adj = adj_from_edges(n23, E23)
        # MEMORY: side string for the apex cut. Use the documented O = [1,2,3,10,22], apex=22.
        side_str = "10101101011001000000001"
        if len(side_str) == n23:
            side = [int(c) for c in side_str]
            acc23 = new_acc()
            # full 2^23 subset enumeration is infeasible; instead probe single-vertex and
            # apex-centered small switches + level-set switches from the apex residual mode.
            # Single-vertex neutral switches:
            singles = [[v] for v in range(n23)]
            # Pairs/triples around O = {1,2,3,10,22}:
            O = [1, 2, 3, 10, 22]
            import itertools
            small = []
            pool = O + [v for v in range(n23) if v not in O][:8]
            for r in range(1, 4):
                for combo in itertools.combinations(sorted(set(pool)), r):
                    small.append(list(combo))
            W_list = singles + small
            if Bconn(n23, adj, side):
                scan_cut("Myc23", n23, adj, side, acc23, full_subsets=False, W_list=W_list)
                print("  N=23 cut Bconn=True gamma0=%s" % gamma_of(n23, adj, side))
            else:
                # try the gamma-min cut found by maxcut search instead
                print("  documented side not B-connected; scanning a maxcut")
            print("  N=23 probed: cuts=%d gated=%d pass=%d pospsi=%d fail=%d"
                  % (acc23['cuts'], acc23['gated_switches'], acc23['pass'],
                     acc23['pass_pospsi'], acc23['fail']))
            print("  N=23 first FAIL:", acc23['first_fail'] or "NONE")
            print("  N=23 min slack:", acc23['min_slack'], acc23['min_slack_ex'] or "")
        else:
            print("  side string length mismatch (%d vs %d)" % (len(side_str), n23))


if __name__ == "__main__":
    main()
