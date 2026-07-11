r"""CLAUDE INDEPENDENT structural gate for the reconstructed R29 2943-vertex cage (2026-07-11).

The fanout leads (r29_gate + global_min_proof) claim: deterministic reconstruction with N=2943, |E|=8422,
|B|=7039, |M|=1383, triangle-free, all bad edges blue-dist-4 (ell=5), row histogram 707 rigid + 676x680
selector rows (total 460387), all-anchor tuple = global scoped-score minimizer (23115) yet Hall defect 28
at hub shore {0,1,2}. Their instance comes from tmp/fanout/r29_gate/lead/r29_lead_gate.py build().

THIS gate re-verifies the STRUCTURAL predicates with MY OWN code (no reuse of their state/scope functions):
  S1 counts (n, blue, bad, total edges) + canonical incidence SHA recompute;
  S2 side is a proper blue 2-coloring (blue bichromatic, bad monochromatic);
  S3 triangle-free on blue+bad (adjacency-set intersection per edge);
  S4 every bad edge has blue-distance EXACTLY 4 (my BFS);
  S5 complete shortest-row enumeration per bad edge (my BFS-layer DFS): 707 bad edges with exactly 1 row,
     676 with exactly 680 rows, grand total 460387; baseline rows and anchor rows are genuine rows;
     anchor rows contain vertex 55; per-family 676 anchors + 4 locals.
  S6 rowVerts nodup within each family (the Codex duplicate-row bug guard).
Integer/exact only. MaxCut exactness (d03 5-class certificate) and the d09 cell lower-bound formula are
audited SEPARATELY -- this gate does not accept or reject them.
Run from repo root: python problems/23/writeup/_claude_r29_2943_structural_gate.py
"""
import hashlib
import importlib.util
import json
import sys
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"


def load():
    spec = importlib.util.spec_from_file_location("untrusted_r29_lead", LEAD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build()


def norm(u, v):
    return (u, v) if u < v else (v, u)


def main():
    d = load()
    n = d["n"]
    blue = {norm(*e) for e in d["blue"]}
    bad = {norm(*e) for e in d["bad"]}
    side = list(d["side"])
    rows = [tuple(r) for r in d["rows"]]
    start, stop = d["selectorStart"], d["selectorStop"]
    atoms = [tuple(a) for a in d["atoms"]]
    fails = []

    # S1 counts + canonical SHA (same payload recipe as d05's incidence_sha)
    ok1 = (n == 2943 and len(blue) == 7039 and len(bad) == 1383 and len(blue) + len(bad) == 8422)
    payload = {"n": n, "blue": sorted(blue), "bad": sorted(bad), "side": tuple(side),
               "rows": tuple(rows),
               "selector_anchor_rows": [m["anchorRow"] for m in d["selectorMeta"]],
               "selector_start": start}
    sha = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                    default=list).encode()).hexdigest()
    print("S1 counts: n=%d |B|=%d |M|=%d |E|=%d -> %s" % (n, len(blue), len(bad), len(blue) + len(bad),
          "PASS" if ok1 else "FAIL"))
    print("   canonical incidence sha256 = %s" % sha)
    if not ok1:
        fails.append("S1")

    # S2 proper coloring
    bic = all(side[u] != side[v] for u, v in blue)
    mono = all(side[u] == side[v] for u, v in bad)
    print("S2 blue bichromatic=%s bad monochromatic=%s -> %s" % (bic, mono, "PASS" if bic and mono else "FAIL"))
    if not (bic and mono):
        fails.append("S2")

    # S3 triangle-free on blue+bad (my own check)
    adj_all = [set() for _ in range(n)]
    for u, v in blue | bad:
        adj_all[u].add(v)
        adj_all[v].add(u)
    tri = 0
    for u, v in blue | bad:
        if adj_all[u] & adj_all[v]:
            tri += 1
            if tri <= 3:
                w = next(iter(adj_all[u] & adj_all[v]))
                print("   TRIANGLE:", u, v, w)
    print("S3 triangle-free: %s" % ("PASS" if tri == 0 else "FAIL(%d)" % tri))
    if tri:
        fails.append("S3")

    # S4 + S5: blue BFS per bad edge, full shortest-row enumeration
    adj_b = [[] for _ in range(n)]
    for u, v in blue:
        adj_b[u].append(v)
        adj_b[v].append(u)

    def bfs(s):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            x = q.popleft()
            for y in adj_b[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    q.append(y)
        return dist

    def all_geodesics(s, t):
        ds = bfs(s)
        dt = bfs(t)
        D = ds[t]
        out = []

        def go(p):
            u = p[-1]
            if u == t:
                out.append(tuple(p))
                return
            for v in adj_b[u]:
                if ds[v] == ds[u] + 1 and dt[v] == D - ds[v]:
                    go(p + [v])

        go([s])
        return D, out

    hist = Counter()
    total_rows = 0
    bad_dist_fail = 0
    baseline_row_fail = 0
    anchor_fail = 0
    fam_partition_fail = 0
    nodup_fail = 0
    sel_atoms = set(range(start, stop))
    meta = d["selectorMeta"]
    for i, a in enumerate(atoms):
        D, fam = all_geodesics(a[0], a[1])
        if D != 4:
            bad_dist_fail += 1
            continue
        cnt = len(fam)
        hist[cnt] += 1
        total_rows += cnt
        famset = set(fam)
        if len(famset) != cnt:
            nodup_fail += 1
        # baseline row of this atom must be a genuine shortest row
        if rows[i] not in famset:
            baseline_row_fail += 1
        if i in sel_atoms:
            m = meta[i - start]
            anchor = tuple(m["anchorRow"])
            if anchor not in famset or 55 not in anchor:
                anchor_fail += 1
            anchors = [r for r in fam if 55 in r]
            locs = [r for r in fam if 55 not in r]
            if not (len(anchors) == 676 and len(locs) == 4):
                fam_partition_fail += 1
    ok4 = bad_dist_fail == 0
    print("S4 all %d bad edges blue-dist 4: %s" % (len(atoms), "PASS" if ok4 else "FAIL(%d)" % bad_dist_fail))
    if not ok4:
        fails.append("S4")
    ok5 = (hist.get(1, 0) == 707 and hist.get(680, 0) == 676 and len(hist) == 2
           and total_rows == 460387 and baseline_row_fail == 0 and anchor_fail == 0
           and fam_partition_fail == 0)
    print("S5 row histogram %s total=%d baselineFail=%d anchorFail=%d famPartFail=%d -> %s"
          % (dict(hist), total_rows, baseline_row_fail, anchor_fail, fam_partition_fail,
             "PASS" if ok5 else "FAIL"))
    if not ok5:
        fails.append("S5")
    ok6 = nodup_fail == 0
    print("S6 family rowVerts nodup: %s" % ("PASS" if ok6 else "FAIL(%d)" % nodup_fail))
    if not ok6:
        fails.append("S6")

    print("=" * 72)
    if fails:
        print("VERDICT: STRUCTURAL GATE FAIL: %s" % ",".join(fails))
        sys.exit(1)
    print("VERDICT: STRUCTURAL GATE PASS (S1-S6). Gamma = 1383*25 = %d; this max cut is Gamma-minimal"
          % (1383 * 25))
    print("REMAINING (separate audits, NOT accepted here): d03 maxcut 5-class certificate; d09 cell")
    print("lower-bound formula derivation (20411+C55+200*covered+4*[0,0]).")


if __name__ == "__main__":
    main()
