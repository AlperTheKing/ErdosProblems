"""G8: structural facts about And(k).

(1) And(k) is isomorphic to the circular complete graph K_{(3k-1)/k}
    (vertices Z_{3k-1}, i~j iff k <= |i-j| <= 2k-1), via the multiplier k.
(2) hence And(2) -> And(3) -> And(4) -> ... (K_{p/q} -> K_{p'/q'} iff p/q <= p'/q'),
    so max_x psi(And(k),x) is NONDECREASING in k.
(3) which induced subgraphs of And(k) admit a homomorphism to C5.
All checks are exact / combinatorial.
"""
import itertools, sys
from G8_graphs import andrasfai


def circular_complete(p, q):
    adj = [[False] * p for _ in range(p)]
    for i in range(p):
        for j in range(p):
            if i == j:
                continue
            d = (i - j) % p
            if q <= d <= p - q:
                adj[i][j] = True
    return adj


def iso_via_multiplier(k):
    n = 3 * k - 1
    _, conn, adj, _ = andrasfai(k)
    adjc = circular_complete(n, k)
    # map v -> k*v mod n
    ok = True
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if adj[u][v] != adjc[(k * u) % n][(k * v) % n]:
                ok = False
    return ok, sorted(set((k * c) % n for c in conn))


def hom_exists(nodes, edges_sub, target_adj, tsize):
    """backtracking homomorphism search from the graph (nodes, edges_sub) to target."""
    nodes = list(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    nbr = {v: [] for v in nodes}
    for (u, v) in edges_sub:
        nbr[u].append(v)
        nbr[v].append(u)
    # order by degree desc
    order = sorted(nodes, key=lambda v: -len(nbr[v]))
    assign = {}

    def rec(i):
        if i == len(order):
            return True
        v = order[i]
        for c in range(tsize):
            ok = True
            for u in nbr[v]:
                if u in assign and not target_adj[c][assign[u]]:
                    ok = False
                    break
            if ok:
                assign[v] = c
                if rec(i + 1):
                    return True
                del assign[v]
        return False

    return rec(0), dict(assign)


C5adj = [[False] * 5 for _ in range(5)]
for i in range(5):
    C5adj[i][(i + 1) % 5] = C5adj[(i + 1) % 5][i] = True


if __name__ == "__main__":
    for k in range(2, 8):
        ok, cs = iso_via_multiplier(k)
        n = 3 * k - 1
        print(f"And({k}) == K_{{{n}/{k}}} via v->{k}v : {ok}  (image connection set {cs}, "
              f"expected {list(range(k, 2*k))})")

    print()
    for k in (3, 4, 5):
        n, conn, adj, edges = andrasfai(k)
        # smallest induced subgraphs with NO hom to C5
        bad = []
        for size in range(5, n + 1):
            found = []
            for S in itertools.combinations(range(n), size):
                Sset = set(S)
                sub = [(u, v) for (u, v) in edges if u in Sset and v in Sset]
                h, _ = hom_exists(S, sub, C5adj, 5)
                if not h:
                    found.append(S)
            print(f"And({k}) induced subgraphs on {size} vertices with NO hom to C5: {len(found)}"
                  + (f"  e.g. {found[0]}" if found else ""))
            if found:
                bad = found
                break
        sys.stdout.flush()
