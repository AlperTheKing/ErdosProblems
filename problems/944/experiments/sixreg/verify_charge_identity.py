"""Referee check of GPT's 2026-06-12 (FK) charge identities on random
deficiency-6 graphs (Delta<=6, sum b = 6, e = 3n-3, connected, 3-colourable).

For each full-degree unfrozen vertex v with witness psi (classes X1,X2,X3,
|N(v) cap X_i| = 2):
  (I1) e_ij = 3(|X_i|+|X_j|-|X_k|) + B_k - 4          (pair identity)
  (I2) sum_{C in comps H[X_i u X_j]} kappa(C) = 6|X_k| + 8 - 2 B_k
       where kappa(C) = |boundary_H(C)| + sum_{x in C} b(x)
  (I3) kappa({x}) = 6 for every singleton component
  (I4) complement of H[N(v)] has a perfect matching on the 6 nbrs
usage: python verify_charge_identity.py <n> <trials> [seed]
"""
import random, sys
from itertools import combinations

n = int(sys.argv[1]); TRIALS = int(sys.argv[2])
rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 944)
assert n % 3 == 0

def rand_6reg_3col(n):
    q = n // 3
    parts = [list(range(i*q, (i+1)*q)) for i in range(3)]
    adj = [set() for _ in range(n)]
    def add(u, v):
        if v in adj[u]: return False
        adj[u].add(v); adj[v].add(u); return True
    for i in range(3):
        for j in range(i+1, 3):
            need = {v: 3 for v in parts[i] + parts[j]}
            for rounds in range(120):
                left = [v for v in parts[i] if need[v] > 0]
                right = [v for v in parts[j] if need[v] > 0]
                if not left and not right: break
                rng.shuffle(left); rng.shuffle(right)
                for u, v in zip(left, right):
                    if need[u] > 0 and need[v] > 0 and v not in adj[u]:
                        add(u, v); need[u] -= 1; need[v] -= 1
            if any(need[v] > 0 for v in parts[i] + parts[j]):
                return None
    return adj

def connected(adj, skip=None):
    verts = [u for u in range(n) if u != skip]
    seen = {verts[0]}; st = [verts[0]]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y != skip and y not in seen: seen.add(y); st.append(y)
    return len(seen) == len(verts)

def all_colourings_with_222(adj, v):
    """yield proper 3-colourings of H-v with N(v) counts (2,2,2); stop at first"""
    verts = sorted((u for u in range(n) if u != v),
                   key=lambda u: (u not in adj[v], -len(adj[u])))
    nv = set(adj[v])
    col = {}
    cnt = [0, 0, 0]
    def bt(i):
        if i == len(verts):
            yield dict(col); return
        w = verts[i]
        used = {col[u] for u in adj[w] if u in col}
        for c in range(3):
            if c in used: continue
            if w in nv and cnt[c] >= 2: continue
            col[w] = c
            if w in nv: cnt[c] += 1
            yield from bt(i + 1)
            if w in nv: cnt[c] -= 1
            del col[w]
    yield from bt(0)

checked = 0; vchecked = 0; fails = []
for t in range(TRIALS):
    adj = rand_6reg_3col(n)
    if adj is None: continue
    # delete 3 random edges -> sum b = 6 (Delta stays <= 6)
    edges = [(u, w) for u in range(n) for w in adj[u] if u < w]
    rng.shuffle(edges)
    dele = edges[:3]
    for u, w in dele: adj[u].discard(w); adj[w].discard(u)
    if not connected(adj): continue
    b = [6 - len(adj[u]) for u in range(n)]
    assert sum(b) == 6
    checked += 1
    fulls = [u for u in range(n) if b[u] == 0]
    rng.shuffle(fulls)
    for v in fulls:                      # a few full vertices per graph
        if not connected(adj, skip=v): continue
        wit = next(all_colourings_with_222(adj, v), None)
        if wit is None: continue             # frozen; identity says nothing
        vchecked += 1
        X = [[u for u in wit if wit[u] == c] for c in range(3)]
        B = [sum(b[u] for u in X[c]) for c in range(3)]
        sz = [len(X[c]) for c in range(3)]
        e = {}
        for c1 in range(3):
            for c2 in range(c1+1, 3):
                e[(c1, c2)] = sum(1 for u in X[c1] for w in adj[u] if wit.get(w) == c2)
        ok = True
        for (i, j) in [(0,1),(0,2),(1,2)]:
            k = 3 - i - j
            if e[(i,j)] != 3*(sz[i]+sz[j]-sz[k]) + B[k] - 4:
                ok = False; fails.append((t, v, 'I1', (i,j))); break
        # I2/I3 per pair
        for (i, j) in [(0,1),(0,2),(1,2)]:
            k = 3 - i - j
            pool = set(X[i]) | set(X[j])
            seenp = set(); comps = []
            for s in pool:
                if s in seenp: continue
                comp = {s}; st = [s]
                while st:
                    x = st.pop()
                    for y in adj[x]:
                        if y in pool and y not in comp: comp.add(y); st.append(y)
                seenp |= comp; comps.append(comp)
            tot = 0
            for C in comps:
                bd = sum(1 for x in C for y in adj[x] if y not in C)
                kap = bd + sum(b[x] for x in C)
                if len(C) == 1 and kap != 6:
                    ok = False; fails.append((t, v, 'I3', len(C), kap))
                tot += kap
            if tot != 6*sz[k] + 8 - 2*B[k]:
                ok = False; fails.append((t, v, 'I2', (i,j), tot, 6*sz[k]+8-2*B[k]))
        # I4 perfect matching in complement of N(v)
        nv = sorted(adj[v])
        pairs = [(x, y) for x, y in combinations(nv, 2) if y not in adj[x]]
        pm = False
        for (a1, b1) in pairs:
            r1 = [x for x in nv if x not in (a1, b1)]
            for (a2, b2) in combinations(r1, 2):
                if b2 in adj[a2]: continue
                a3, b3 = [x for x in r1 if x not in (a2, b2)]
                if b3 not in adj[a3]: pm = True; break
            if pm: break
        if not pm:
            ok = False; fails.append((t, v, 'I4'))
        if not ok: break
    if fails: break
print(f"graphs={checked} unfrozenVerticesChecked={vchecked} FAILS={len(fails)}")
for f in fails[:5]: print("FAIL:", f)
