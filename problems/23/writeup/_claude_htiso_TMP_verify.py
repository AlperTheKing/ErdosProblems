from collections import Counter
from _codex_ht_isolation_gate import scan_selected_cut
from _codex_length_tier_matching_gate import h_blowup, residuals
from _codex_k2t_switch_probe import adj_from_edges

n, edges, _side = h_blowup(3)
assert n == 27

# triangle-free check
adjset = [set() for _ in range(n)]
for u, v in edges:
    adjset[u].add(v); adjset[v].add(u)
for a in range(n):
    for b in adjset[a]:
        assert not (adjset[a] & adjset[b]), ("TRIANGLE", a, b)
print("triangle-free OK, n=27, |E|=", len(edges))

side = [int(c) for c in "111111111111111100000000000"]
adj = adj_from_edges(n, edges)
from _h import Bconn
print("Bconn:", Bconn(n, adj, side))
R = residuals(n, adj, side)
print("R[18] =", R[18], " (negative required)")
print("negative-residual vertices:", [i for i, r in enumerate(R) if r < 0])

acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0,
       "status": Counter(), "stats": Counter(), "first": None}
scan_selected_cut("H3-verify", n, adj, side, acc, 2, True, 3_000_000)
print("TESTED", acc["tested"], "STATUS", dict(acc["status"]))
print("FIRST", acc["first"])
print("VERDICT:", "FAIL (reproduced)" if acc["first"] is not None else "PASS/none-on-this-side")
