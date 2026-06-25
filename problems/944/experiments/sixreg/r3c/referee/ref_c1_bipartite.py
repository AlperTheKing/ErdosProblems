# LEMMA C1 stress test: in every connected bipartite graph, NO non-adjacent
# pair is difference-forced under proper 3-colourings.
# Exhaustive over all connected bipartite graphs on n <= 9 vertices (geng -c -b).
import subprocess, sys, itertools

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"

def parse_g6(line):
    s = line.strip()
    data = [ord(c) - 63 for c in s]
    n = data[0]
    assert n < 63
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]: adj[i].add(j); adj[j].add(i)
            idx += 1
    return n, adj

def three_col_exists(n, adj, force_eq=None):
    """exact backtracking; force_eq=(u,w) -> require same colour (merge)."""
    rep = list(range(n))
    if force_eq:
        u, w = force_eq
        rep[w] = u
        if u in adj[w]: return False
    verts = [v for v in range(n) if rep[v] == v]
    madj = {v: set() for v in verts}
    for x in range(n):
        rx = rep[x]
        for y in adj[x]:
            ry = rep[y]
            if rx != ry: madj[rx].add(ry); madj[ry].add(rx)
    col = {}
    def bt(i):
        if i == len(verts): return True
        v = verts[i]
        used = {col[y] for y in madj[v] if y in col}
        for c in (0, 1, 2):
            if c not in used:
                col[v] = c
                if bt(i + 1): return True
                del col[v]
        return False
    return bt(0)

def main(nmax=9):
    total_graphs = 0; total_pairs = 0; violations = []
    for n in range(2, nmax + 1):
        r = subprocess.run([GENG, '-q', '-c', '-b', str(n)], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if not line.strip(): continue
            nn, adj = parse_g6(line)
            total_graphs += 1
            for u, w in itertools.combinations(range(nn), 2):
                if w in adj[u]: continue
                total_pairs += 1
                if not three_col_exists(nn, adj, force_eq=(u, w)):
                    violations.append((line.strip(), u, w))
    print(f"connected bipartite graphs n<=({nmax}): {total_graphs}; "
          f"non-adjacent pairs tested: {total_pairs}; difference-forced pairs found: {len(violations)}")
    if violations: print("VIOLATIONS:", violations[:10])

if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
