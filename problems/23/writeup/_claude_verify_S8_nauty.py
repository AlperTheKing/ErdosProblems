r"""INDEPENDENT re-verification of the proof-attack workflow's |S|<=8 claim (2026-07-08).

The workflow's minimal-counterexample structure theorem: a minimal Hall violator S of Ell5SupportExpansion has
|E_short(S)| = |S|-1 = m, its geodesic graph F is CONNECTED with m edges, and S is m+1 distinct vertex-pairs at
F-distance EXACTLY 4; hence m+1 <= D4(F) := #{unordered vertex pairs at graph-distance exactly 4 in F}.

WORKFLOW CLAIM (computer-assisted, HERE INDEPENDENTLY RE-CHECKED): for EVERY connected graph F with m edges and m<=7
(hence <=8 vertices), D4(F) <= m-1. Therefore a minimal violator would need m+1 <= D4(F) <= m-1, impossible => no
minimal violator with |S| = m+1 <= 8. So Ell5SupportExpansion holds for all |S| <= 8. The workflow also claims the
counting SATURATES at m=8: the double-star tree (2 centers, 1 shared leaf, 3 private leaves each; 9 vertices, 8 edges)
has D4 = 9 = m+1.

This script enumerates ALL connected graphs on 2..9 vertices via nauty geng, computes e=#edges and D4 for each, and
reports max(D4 - e) bucketed by e. Verifies: (a) max(D4-e) = -1 (i.e. D4<=e-1) for every connected graph with e<=7;
(b) the FIRST e with max(D4-e) = +1 is e=8 (saturation). EXACT (integer BFS). Run from problems/23/writeup.
"""
import subprocess
from collections import deque
from _h import dec, GENG
from _codex_k2t_switch_probe import adj_from_edges


def d4_count(n, adj):
    """number of unordered vertex pairs at graph-distance EXACTLY 4."""
    cnt = 0
    for s in range(n):
        dist = [-1] * n; dist[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for w in adj[u]:
                if dist[w] < 0:
                    dist[w] = dist[u] + 1; q.append(w)
        for t in range(s + 1, n):
            if dist[t] == 4:
                cnt += 1
    return cnt


def main():
    print("INDEPENDENT re-verification of |S|<=8 (workflow: connected F with e<=7 edges => D4(F) <= e-1).")
    print("=" * 92)
    # bucket[e] = max (D4 - e) over connected graphs with that many edges
    bucket = {}
    ex_pos = {}  # first witness with D4-e >= +1 per e
    for k in range(2, 10):
        out = subprocess.run([GENG, '-c', str(k)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, E = dec(g6); adj = adj_from_edges(n, E)
            e = len(E)
            d4 = d4_count(n, adj)
            diff = d4 - e
            if e not in bucket or diff > bucket[e]:
                bucket[e] = diff
                if diff >= 1 and e not in ex_pos:
                    ex_pos[e] = (g6, n, e, d4)
        print("  done geng -c %d (%d graphs); running max(D4-e) per e so far: %s"
              % (k, len(out), {ee: bucket[ee] for ee in sorted(bucket)}), flush=True)
    print("=" * 92)
    print("max(D4 - e) bucketed by edge count e:")
    for e in sorted(bucket):
        tag = ""
        if e <= 7 and bucket[e] >= 0:
            tag = "  <== VIOLATES workflow claim (D4-e should be <=-1 for e<=7)!"
        if bucket[e] >= 1 and e in ex_pos:
            tag += "  saturation witness %s" % (ex_pos[e],)
        print("  e=%2d: max(D4-e) = %+d%s" % (e, bucket[e], tag))
    # verdict
    e7_ok = all(bucket.get(e, -99) <= -1 for e in range(1, 8))
    first_sat = min((e for e in sorted(bucket) if bucket[e] >= 1), default=None)
    print("=" * 92)
    if e7_ok and first_sat == 8:
        print("VERDICT: CONFIRMED. For every connected graph with e<=7 edges, D4 <= e-1 (max D4-e = -1); first saturation")
        print("  (D4-e >= +1) is at e=8. => the workflow's |S|<=8 Hall proof is INDEPENDENTLY VERIFIED: a minimal violator")
        print("  would need m+1 <= D4(F) <= m-1 for m<=7, impossible. Ell5SupportExpansion holds for all |S| <= 8.")
    elif not e7_ok:
        bad = [e for e in range(1, 8) if bucket.get(e, -99) >= 0]
        print("VERDICT: *** REFUTED. Some connected graph with e<=7 edges has D4 >= e (edges %s) -- the workflow's |S|<=8" % bad)
        print("  claim is WRONG; a minimal violator of that size is NOT excluded by pure counting. Re-examine. ***")
    else:
        print("VERDICT: e<=7 bound holds but first saturation is at e=%s (workflow said 8). Note the discrepancy." % first_sat)


if __name__ == '__main__':
    main()
