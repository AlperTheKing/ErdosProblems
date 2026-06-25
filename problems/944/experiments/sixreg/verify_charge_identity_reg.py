"""Referee check of the (FK) charge identities, deficiency-0 variant, on the
REAL unfrozen vertices found by the n=14 census (high_unfrozen_n14.txt).

For a 6-regular graph (b == 0) and unfrozen v with witness psi:
  (I1') e_ij = 3(|X_i|+|X_j|-|X_k|) - 1
  (I2') sum_C kappa(C) = 6|X_k| + 2     (kappa(C) = |boundary| since b=0)
  (I3') singleton components have kappa = 6
  (I4') complement of H[N(v)] has a perfect matching
Identical double-counting derivation as GPT's deficiency-6 boxed identities;
constants differ because sum b = 0 here and B_i = 0.
usage: python verify_charge_identity_reg.py < high_unfrozen_n14.txt
"""
import sys
from itertools import combinations

def g6decode(s):
    n = ord(s[0]) - 63
    adj = [set() for _ in range(n)]
    bit = 0
    for j in range(1, n):
        for i in range(j):
            byte = 1 + bit // 6; off = 5 - bit % 6
            if (ord(s[byte]) - 63) >> off & 1:
                adj[i].add(j); adj[j].add(i)
            bit += 1
    return n, adj

def witness_222(n, adj, v):
    verts = sorted((u for u in range(n) if u != v),
                   key=lambda u: (u not in adj[v], -len(adj[u])))
    nv = set(adj[v]); col = {}; cnt = [0, 0, 0]
    def bt(i):
        if i == len(verts): return dict(col)
        w = verts[i]
        used = {col[u] for u in adj[w] if u in col}
        for c in range(3):
            if c in used: continue
            if w in nv and cnt[c] >= 2: continue
            col[w] = c
            if w in nv: cnt[c] += 1
            r = bt(i + 1)
            if w in nv: cnt[c] -= 1
            del col[w]
            if r is not None: return r
        return None
    return bt(0)

instances = 0; fails = []
for line in sys.stdin:
    line = line.strip()
    if not line.startswith('HIGH_UNFROZEN_G6:'): continue
    parts = line.split()
    g6 = parts[1]; uset = int(parts[3].split('=')[1])
    n, adj = g6decode(g6)
    for v in range(n):
        if not (uset >> v) & 1: continue
        wit = witness_222(n, adj, v)
        if wit is None:
            fails.append((g6, v, 'NO_WITNESS — census bitmask wrong!')); continue
        instances += 1
        X = [[u for u in wit if wit[u] == c] for c in range(3)]
        sz = [len(X[c]) for c in range(3)]
        e = {}
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                e[(c1, c2)] = sum(1 for u in X[c1] for w in adj[u] if wit.get(w) == c2)
        for (i, j) in [(0,1),(0,2),(1,2)]:
            k = 3 - i - j
            if e[(i,j)] != 3*(sz[i]+sz[j]-sz[k]) - 1:
                fails.append((g6, v, 'I1', (i,j), e[(i,j)], 3*(sz[i]+sz[j]-sz[k])-1))
            pool = set(X[i]) | set(X[j])
            seen = set(); tot = 0
            for s in pool:
                if s in seen: continue
                comp = {s}; st = [s]
                while st:
                    x = st.pop()
                    for y in adj[x]:
                        if y in pool and y not in comp: comp.add(y); st.append(y)
                seen |= comp
                bd = sum(1 for x in comp for y in adj[x] if y not in comp)
                if len(comp) == 1 and bd != 6:
                    fails.append((g6, v, 'I3', bd))
                tot += bd
            if tot != 6*sz[k] + 2:
                fails.append((g6, v, 'I2', (i,j), tot, 6*sz[k]+2))
        nv = sorted(adj[v]); pm = False
        for (a1, b1) in [(x,y) for x,y in combinations(nv,2) if y not in adj[x]]:
            r1 = [x for x in nv if x not in (a1, b1)]
            for (a2, b2) in combinations(r1, 2):
                if b2 in adj[a2]: continue
                a3, b3 = [x for x in r1 if x not in (a2, b2)]
                if b3 not in adj[a3]: pm = True; break
            if pm: break
        if not pm: fails.append((g6, v, 'I4'))
print(f"unfrozenInstances={instances} FAILS={len(fails)}")
for f in fails[:8]: print("FAIL:", f)
