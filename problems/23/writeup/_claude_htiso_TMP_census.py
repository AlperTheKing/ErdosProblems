"""Instrumented HT-isolation census: capture the true min-matching count of every
instance the gate feeds, so we can characterize the 43 too_many and pick a cap.

We monkeypatch enumerate_min_matchings to record the real count. The real
enumerator bails once len(out) > cap; to learn the TRUE count for capped
instances we run the recursion counting only (no dict materialization) up to a
hard ceiling, so memory stays flat.
"""
import sys, subprocess
from collections import Counter

import _codex_stage0_all_min_gate as stg
import _codex_ht_isolation_gate as G
from _h import GENG, dec

COUNTS = Counter()          # bucketed true counts
import os
CAP_FEED = int(os.environ.get("CAP_FEED", "200000"))   # materialize <= this for gate logic
TRUE_CEIL = 60_000_000      # hard ceiling for the pure count (avoid infinite)

_orig = stg.enumerate_min_matchings

def counting_enumerate(F0, E0, witnesses, deg_f1, cap):
    # First: pure count of minimum-cost matchings (no materialization).
    F0 = tuple(F0)
    best = [None]
    cnt = [0]
    hit_ceiling = [False]
    def rec(i, used, cost):
        if hit_ceiling[0]:
            return
        if best[0] is not None and cost > best[0]:
            return
        if i == len(F0):
            if best[0] is None or cost < best[0]:
                best[0] = cost
                cnt[0] = 0
            cnt[0] += 1
            if cnt[0] > TRUE_CEIL:
                hit_ceiling[0] = True
            return
        f = F0[i]
        for e in E0:
            if e in used or f not in witnesses[e]:
                continue
            used.add(e); rec(i+1, used, cost+deg_f1[e]); used.remove(e)
    rec(0, set(), 0)
    true_count = cnt[0]
    if hit_ceiling[0]:
        COUNTS[">%d" % TRUE_CEIL] += 1
    else:
        # bucket
        if true_count <= 100000: b = "<=1e5"
        elif true_count <= 200000: b = "1e5-2e5"
        elif true_count <= 1000000: b = "2e5-1e6"
        elif true_count <= 5000000: b = "1e6-5e6"
        elif true_count <= 20000000: b = "5e6-2e7"
        else: b = "2e7-6e7"
        COUNTS[b] += 1
    # Now delegate to the original with the FEED cap so gate logic still runs
    # (materializing at most CAP_FEED matchings keeps memory bounded).
    return _orig(F0, E0, witnesses, deg_f1, min(cap, CAP_FEED))

stg.enumerate_min_matchings = counting_enumerate
G.enumerate_min_matchings = counting_enumerate  # G imported the name directly

def run_range(lo, hi, max_add):
    acc = {"tested":0,"no_switch":0,"bad_terminal":0,"status":Counter(),"stats":Counter(),"first":None}
    for nn in range(lo, hi+1):
        for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split():
            n, edges = dec(g6)
            G.scan_selected_allmax("cen%d"%nn, n, edges, acc, max_add, True, CAP_FEED)
            if acc["first"] is not None: break
        if acc["first"] is not None: break
    from _codex_length_tier_matching_gate import h_blowup
    from _codex_k2t_switch_probe import adj_from_edges
    # H2-allmax
    if acc["first"] is None:
        n, edges, _s = h_blowup(2)
        G.scan_selected_allmax("H2-allmax", n, edges, acc, max_add, True, CAP_FEED)
    # H-inherited 2..4
    if acc["first"] is None:
        for t in range(2, 5):
            n, edges, side = h_blowup(t)
            G.scan_selected_cut("H%d-inherited"%t, n, adj_from_edges(n, edges), side, acc, max_add, True, CAP_FEED)
            if acc["first"] is not None: break
    return acc

if __name__ == "__main__":
    max_add = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    acc = run_range(5, 10, max_add)
    print("MAX_ADD", max_add)
    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("TRUE_COUNT_BUCKETS:", dict(COUNTS))
    print("no_contact_miss_count:", {k:v for k,v in acc["stats"].items() if isinstance(k,tuple) and k[0]=="no_contact_miss_count"})
    print("first:", acc["first"])
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")
