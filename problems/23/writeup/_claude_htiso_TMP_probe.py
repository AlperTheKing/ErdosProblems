import sys
from collections import Counter
import _codex_ht_isolation_gate as G
from _codex_length_tier_matching_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges

# Monkeypatch enumerate_min_matchings to record the true count even when capped.
import _codex_stage0_all_min_gate as S0
_orig = S0.enumerate_min_matchings
COUNTS = []
def _true_count(F0, E0, witnesses, deg_f1, ceil):
    # count minimum-cost matchings without storing, up to ceil
    F0 = tuple(F0); best = [None]; cnt = [0]
    def rec(i, used, cost):
        if cnt[0] > ceil:
            return
        if best[0] is not None and cost > best[0]:
            return
        if i == len(F0):
            if best[0] is None or cost < best[0]:
                best[0] = cost; cnt[0] = 0
            cnt[0] += 1
            return
        f = F0[i]
        for e in E0:
            if e in used or f not in witnesses[e]:
                continue
            used.add(e); rec(i + 1, used, cost + deg_f1[e]); used.remove(e)
    rec(0, set(), 0)
    return cnt[0], best[0]

def _wrap(F0, E0, witnesses, deg_f1, cap):
    res = _orig(F0, E0, witnesses, deg_f1, cap)
    matchings, status, best_cost, count = res
    if status == "too_many":
        tc, bc = _true_count(F0, E0, witnesses, deg_f1, 200_000_000)
        COUNTS.append((status, tc, len(F0), len(E0)))
    else:
        COUNTS.append((status, count, len(F0), len(E0)))
    return res
# patch in both modules' namespaces
S0.enumerate_min_matchings = _wrap
G.enumerate_min_matchings = _wrap


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


CAP = 3_000_000
MAX_ADD = 2

t = int(sys.argv[1])
mode = sys.argv[2]  # 'inherited' or 'allmax'
n, edges, side = h_blowup(t)
tri_free(n, edges)
adj = adj_from_edges(n, edges)
acc = new_acc()
COUNTS.clear()
if mode == 'inherited':
    G.scan_selected_cut("H%d-inh" % t, n, adj, side, acc, MAX_ADD, True, CAP)
else:
    G.scan_selected_allmax("H%d-all" % t, n, edges, acc, MAX_ADD, True, CAP)

print("t=%d n=%d mode=%s" % (t, n, mode))
print("TESTED", acc["tested"], "NO_SWITCH", acc["no_switch"], "BAD_TERMINAL", acc["bad_terminal"])
print("STATUS", dict(acc["status"]))
print("STATS", dict(acc["stats"]))
print("FIRST", acc["first"])
tm = [c for c in COUNTS if c[0] == "too_many"]
oks = [c for c in COUNTS if c[0] == "ok"]
print("min-matching-enum calls:", len(COUNTS), "ok:", len(oks), "too_many:", len(tm))
if tm:
    print("too_many TRUE counts (cap=%d):" % CAP, sorted(set(c[1] for c in tm)))
if oks:
    print("ok counts max:", max(c[1] for c in oks))
sys.stdout.flush()
