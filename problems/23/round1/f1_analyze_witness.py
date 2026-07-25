"""Independent (Python) verification + structural analysis of the extremal
witnesses found by f1_exact_a.exe.  Exact integer arithmetic."""
import sys
from itertools import combinations
from f1_bip import g6_decode, bip_bruteforce, is_triangle_free

WIT = {
    5: "DUW", 6: "ECxo", 7: "F?bro", 8: "G?rF`w", 9: "H?BEFo}",
    10: "I?rFf_{N?", 11: "J?BEFo}}@{?", 12: "K?ABBBwerwBw",
    13: "L??FFB_~?~^_Fw", 14: "M?AE@bH{AYN_LgBs?",
}


def canon_profile(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    deg = sorted(len(a) for a in adj)
    # twin classes (same neighbourhood) => blow-up structure
    classes = {}
    for v in range(n):
        classes.setdefault(frozenset(adj[v]), []).append(v)
    # independence number
    best = 0
    verts = list(range(n))
    def ext(cur, cand):
        nonlocal best
        if len(cur) + len(cand) <= best:
            return
        if not cand:
            best = max(best, len(cur))
            return
        v = cand[0]
        ext(cur + [v], [u for u in cand[1:] if u not in adj[v]])
        ext(cur, cand[1:])
    ext([], verts)
    return deg, sorted(len(c) for c in classes.values()), len(classes), best


for n in sorted(WIT):
    g6 = WIT[n]
    nn, E = g6_decode(g6)
    assert nn == n, (nn, n)
    tf = is_triangle_free(n, E)
    b = bip_bruteforce(n, E)
    deg, cls, ncls, alpha = canon_profile(n, E)
    print(f"N={n:3d} g6={g6:18s} tf={tf} e={len(E):3d} bip={b:2d} "
          f"floor(N^2/25)={n*n//25:2d}  deg={deg} twinclasses={cls} "
          f"#classes={ncls} alpha={alpha}")
