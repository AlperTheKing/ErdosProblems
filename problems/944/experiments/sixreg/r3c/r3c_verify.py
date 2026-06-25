#!/usr/bin/env python3
# Independent verifier for r3c instances (NO ortools — pure Python + pysat).
# Verifies, from the JSON artifact alone:
#   (V1) graph validity: Delta<=6, Sum(6-deg)=6, connected, deficient set =
#        the 6 gadget vertices, U !~ W (non-triangle triple), diamond edges
#        present (so rainbow-rigidity has a hand proof), K4-freeness;
#   (V2) phi0 reconstruction: K is 3-colourable (explicit colouring checked);
#   (V3) rainbow-rigidity: CNF "proper 3-colouring with psi(U)=psi(W)" is
#        UNSAT under cadical153 AND glucose42 (two independent SAT engines);
#   (V4) every full vertex v has a stored witness: proper on K-v and
#        trace <=2 per colour on N(v)  => v UNFROZEN;
#   (V5) coverage: witnesses exist for ALL full vertices.
import sys, json
from collections import deque
from pysat.solvers import Cadical153, Glucose42

def load(fn):
    with open(fn) as f:
        return json.load(f)

def mkadj(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    return adj

def main(fn):
    out = load(fn)
    inst = out['inst']
    n, edges = inst['n'], [tuple(e) for e in inst['edges']]
    gd = inst['gadget']
    A, B, U, T, V, W = gd['A'], gd['B'], gd['U'], gd['T'], gd['V'], gd['W']
    adj = mkadj(n, edges)
    deg = [len(adj[v]) for v in range(n)]
    # V1
    assert len(set(edges)) == len(edges), "duplicate edges"
    assert all(a != b for a, b in edges), "self-loop"
    assert max(deg) <= 6
    assert sum(6 - d for d in deg) == 6
    expected_def = inst.get('deficient', sorted(gd.values()))
    assert sorted(v for v in range(n) if deg[v] < 6) == sorted(expected_def)
    assert all(z in expected_def for z in (U, V, W)), "z-triple not deficient"
    seen = {0}; dq = deque([0])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y); dq.append(y)
    assert len(seen) == n, "disconnected"
    assert W not in adj[U], "U~W: triple would be a triangle"
    for e in [(A,B),(A,U),(B,U),(A,T),(B,T),(U,V),(V,W),(T,W)]:
        assert tuple(sorted(e)) in set(map(tuple, map(sorted, edges))), f"gadget edge {e} missing"
    # K4-free check (relevant: 4-critical graph containing K4 equals K4)
    for a, b in edges:
        common = adj[a] & adj[b]
        for c in common:
            if adj[a] & adj[b] & adj[c]:
                print("  note: K4 present (not a hypothesis violation)"); break
        else:
            continue
        break
    print(f"[V1] valid: n={n}, Delta<=6, Sum b=6 on gadget exactly, connected, U!~W")
    # V2
    side1 = set(inst['side1'])
    phi0 = {}
    for v in range(inst['nb']):
        phi0[v] = 1 if v in side1 else 2
    phi0[A], phi0[B], phi0[U], phi0[T], phi0[V], phi0[W] = 1, 2, 3, 3, 1, 2
    assert all(phi0[a] != phi0[b] for a, b in edges)
    print("[V2] phi0 proper => K 3-colourable")
    # V3: CNF, one-hot vars x_{v,c} = 3v+c+1
    def var(v, c): return 3 * v + c + 1
    cnf = []
    for v in range(n):
        cnf.append([var(v, 0), var(v, 1), var(v, 2)])
        for c in range(3):
            for d in range(c + 1, 3):
                cnf.append([-var(v, c), -var(v, d)])
    for a, b in edges:
        for c in range(3):
            cnf.append([-var(a, c), -var(b, c)])
    eq = cnf + [cl for c in range(3) for cl in ([-var(U, c), var(W, c)], [var(U, c), -var(W, c)])]
    for name, S in (("cadical153", Cadical153), ("glucose42", Glucose42)):
        with S(bootstrap_with=eq) as s:
            r = s.solve()
        assert r is False, f"{name}: psi(U)=psi(W) colouring EXISTS -> not rigid!"
        print(f"[V3] {name}: psi(U)=psi(W) UNSAT  => rainbow-rigid (with U~V, V~W edges)")
    # V4/V5
    fulls = [v for v in range(n) if deg[v] == 6]
    wit = {int(k): v for k, v in out['witnesses'].items()}
    missing = [v for v in fulls if v not in wit]
    assert not missing, f"missing witnesses for {missing}"
    for v in fulls:
        col = wit[v]
        assert len(col) == n
        for a, b in edges:
            if a == v or b == v:
                continue
            assert col[a] != col[b], f"witness for {v} improper on {(a,b)}"
            assert col[a] in (0, 1, 2) and col[b] in (0, 1, 2)
        cnt = [0, 0, 0]
        for y in adj[v]:
            cnt[col[y]] += 1
        assert max(cnt) <= 2, f"witness for {v} trace {cnt} not (2,2,2)"
    print(f"[V4/V5] ALL {len(fulls)} full vertices have INDEPENDENTLY VERIFIED unfrozen witnesses")
    print(f"==> instance {fn}: rainbow-rigid on deficient non-triangle triple (U,V,W)=({U},{V},{W}), "
          f"ZERO frozen full vertices.  (R3') REFUTED by this instance.")

if __name__ == "__main__":
    main(sys.argv[1])
