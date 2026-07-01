import sys, time
from collections import Counter
from _codex_ht_isolation_gate import scan_selected_allmax, scan_selected_cut
from _codex_length_tier_matching_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges


def blowup(parts):
    mm = len(parts); off = [0] * (mm + 1)
    for i in range(mm):
        off[i + 1] = off[i] + parts[i]
    nn = off[mm]; EE = []
    for i in range(mm):
        j = (i + 1) % mm
        for a in range(off[i], off[i + 1]):
            for b in range(off[j], off[j + 1]):
                EE.append((min(a, b), max(a, b)))
    return nn, sorted(set(EE))


def tri_free(n, edges):
    adjset = [set() for _ in range(n)]
    for u, v in edges:
        adjset[u].add(v); adjset[v].add(u)
    for a in range(n):
        for b in adjset[a]:
            assert not (adjset[a] & adjset[b]), ("TRIANGLE", a, b)


def new_acc():
    return {"tested": 0, "no_switch": 0, "bad_terminal": 0,
            "status": Counter(), "stats": Counter(), "first": None}


def report(tag, acc, dt):
    print("==== %s  (%.1fs) ====" % (tag, dt))
    print("TESTED", acc["tested"], "NO_SWITCH", acc["no_switch"], "BAD_TERMINAL", acc["bad_terminal"])
    print("STATUS", dict(acc["status"]))
    print("STATS", dict(acc["stats"]))
    print("FIRST", acc["first"])
    print(flush=True)
    if acc["first"] is not None:
        print("!!!! FAIL WITNESS !!!!", acc["first"], flush=True)
        raise SystemExit(1)


CAP = 3_000_000
MAX_ADD = 2
which = sys.argv[1] if len(sys.argv) > 1 else "inh"

if which == "inh":
    # inherited-side balanced C5[t] blowups, t=3..8
    for t in [3, 4, 5, 6, 7, 8]:
        n, edges, side = h_blowup(t)
        tri_free(n, edges)
        adj = adj_from_edges(n, edges)
        acc = new_acc()
        t0 = time.time()
        scan_selected_cut("H%d-inh" % t, n, adj, side, acc, MAX_ADD, True, CAP)
        report("H%d inherited t=%d n=%d" % (t, t, n), acc, time.time() - t0)

elif which == "allsmall":
    # all-maxcut for the smaller balanced blowups t=3,4
    for t in [3, 4]:
        n, edges, side = h_blowup(t)
        tri_free(n, edges)
        acc = new_acc()
        t0 = time.time()
        scan_selected_allmax("H%d-all" % t, n, edges, acc, MAX_ADD, True, CAP)
        report("H%d allmax t=%d n=%d" % (t, t, n), acc, time.time() - t0)

elif which == "unbal":
    unbal = [
        [2, 2, 2, 2, 1], [3, 2, 2, 2, 2], [3, 3, 2, 2, 2], [4, 2, 2, 2, 2],
        [1, 3, 1, 3, 1], [2, 3, 2, 3, 2], [3, 3, 3, 2, 2], [4, 3, 2, 3, 2],
    ]
    for parts in unbal:
        n, edges = blowup(parts)
        tri_free(n, edges)
        acc = new_acc()
        t0 = time.time()
        scan_selected_allmax("unbal%s" % parts, n, edges, acc, MAX_ADD, True, CAP)
        report("unbal parts=%s n=%d" % (parts, n), acc, time.time() - t0)

print("SECTION %s DONE, no FAIL" % which, flush=True)
