# Exact frozen check: vertex v is frozen iff for ALL 90 balanced (2,2,2)
# patterns on N(v), the precoloured 3-colouring of K-v is UNSAT.
# Exhaustive backtracking with MRV+DSATUR; exact if no timeout.
import json, sys, itertools

def load(path):
    d = json.load(open(path)); inst = d['inst']; n = inst['n']
    E = {(min(int(a),int(b)), max(int(a),int(b))) for a, b in inst['edges']}
    adj = [set() for _ in range(n)]
    for a, b in E: adj[a].add(b); adj[b].add(a)
    return d, inst, n, E, adj

def sat_with_precolour(n, adj, exclude, pre, budget=8_000_000):
    verts = [v for v in range(n) if v != exclude]
    avail = {}
    for v in verts:
        if v in pre: avail[v] = {pre[v]}
        else: avail[v] = {0,1,2}
    col = {}
    # initial propagation from precoloured
    nodes = [0]
    def pick():
        best, bv = None, None
        for v in verts:
            if v in col: continue
            l = len(avail[v])
            if l == 0: return v
            sat = sum(1 for y in adj[v] if y in col or (y != exclude and y in pre))
            key = (l, -sat, -len(adj[v]))
            if best is None or key < best: best, bv = key, v
        return bv
    def bt():
        nodes[0] += 1
        if nodes[0] > budget: raise RuntimeError
        v = pick()
        if v is None: return True
        for c in sorted(avail[v]):
            col[v] = c
            changed = []; ok = True
            for y in adj[v]:
                if y != exclude and y not in col and c in avail[y]:
                    avail[y].discard(c); changed.append(y)
                    if not avail[y]: ok = False
            if ok and bt(): return True
            for y in changed: avail[y].add(c)
            del col[v]
        return False
    try:
        return 'SAT' if bt() else 'UNSAT'
    except RuntimeError:
        return 'TIMEOUT'

def frozen_status(path, v):
    d, inst, n, E, adj = load(path)
    nbrs = sorted(adj[v])
    assert len(nbrs) == 6
    n_unsat = n_sat = n_to = 0
    for pat in set(itertools.permutations([0,0,1,1,2,2])):
        pre = dict(zip(nbrs, pat))
        r = sat_with_precolour(n, adj, v, pre)
        if r == 'SAT': n_sat += 1
        elif r == 'UNSAT': n_unsat += 1
        else: n_to += 1
    verdict = 'FROZEN (exact)' if (n_sat == 0 and n_to == 0) else ('UNFROZEN' if n_sat else 'INCONCLUSIVE')
    print(f"{path} v={v}: patterns SAT={n_sat} UNSAT={n_unsat} TIMEOUT={n_to} -> {verdict}")

if __name__ == '__main__':
    frozen_status(sys.argv[1], int(sys.argv[2]))
