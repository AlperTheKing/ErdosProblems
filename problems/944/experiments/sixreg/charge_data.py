"""Kempe-component cut-charge data collector (referee Q3 instrumentation).

On random 6-regular chi>=4 graphs, for every vertex v and proper 3-colouring of G-v
whose N(v)-split is 2+2+2, record for each colour pair {i,j} (third colour k):
  c_ij  = number of connected components of G[V_i u V_j] (v excluded),
  pattern of the four boundary vertices among components:
     '22'   = all four in one component        (sigma=0)
     '11'   = two components, each with one i and one j  (sigma=1)
     'viol' = anything else (single-colour boundary component etc. -- implies a
              critical edge by the tether lemma; expected on non-targets)
Compare csum = c_12+c_13+c_23 against n-1 and n-1-Sigma.
"""
import random, sys
from collections import Counter

def random_6regular(n, rng):
    # pairing model with retry
    while True:
        stubs = [v for v in range(n) for _ in range(6)]
        rng.shuffle(stubs)
        adj = [set() for _ in range(n)]
        ok = True
        for i in range(0, len(stubs), 2):
            a, b = stubs[i], stubs[i+1]
            if a == b or b in adj[a]: ok = False; break
            adj[a].add(b); adj[b].add(a)
        if ok: return adj

def col3_exists(n, adj, skip=-1):
    verts = [v for v in range(n) if v != skip]
    col = {}
    def bt(i):
        if i == len(verts): return True
        v = verts[i]
        used = {col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v] = c
                if bt(i+1): return True
                del col[v]
        return False
    return bt(0)

def colourings(n, adj, skip, limit=200):
    verts = [v for v in range(n) if v != skip]
    out = []; col = {}
    def bt(i):
        if len(out) >= limit: return
        if i == len(verts): out.append(dict(col)); return
        v = verts[i]
        used = {col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v] = c; bt(i+1)
                if v in col: del col[v]
    bt(0)
    return out

def components(vset, adj):
    comps = []; left = set(vset)
    while left:
        s = left.pop(); comp = {s}; st = [s]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y in left: left.discard(y); comp.add(y); st.append(y)
        comps.append(comp)
    return comps

rng = random.Random(944944)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 14
TRIALS = int(sys.argv[2]) if len(sys.argv) > 2 else 400
stats = Counter(); satur = Counter(); examples = []
n_inst = 0
for t in range(TRIALS):
    adj = random_6regular(n, rng)
    if col3_exists(n, adj): continue          # need chi >= 4
    for v in range(n):
        for phi in colourings(n, adj, v, limit=60):
            cls = {c: [u for u in adj[v] if phi[u] == c] for c in range(3)}
            if sorted(len(x) for x in cls.values()) != [2,2,2]: continue
            n_inst += 1
            csum = 0; Sigma = 0; viol = False
            for i in range(3):
                for j in range(i+1, 3):
                    Vij = [u for u in phi if phi[u] in (i,j)]
                    comps = components(Vij, adj)
                    csum += len(comps)
                    bnd = cls[i] + cls[j]
                    bcomps = [c for c in comps if any(u in c for u in bnd)]
                    if len(bcomps) == 1 and all(u in bcomps[0] for u in bnd):
                        pass  # (2,2): sigma 0
                    elif len(bcomps) == 2 and all(
                            sum(1 for u in cls[i] if u in bc) == 1 and
                            sum(1 for u in cls[j] if u in bc) == 1 for bc in bcomps):
                        Sigma += 1
                    else:
                        viol = True
            key = ('viol' if viol else 'ok', csum - (n - 1), Sigma)
            stats[key] += 1
            if not viol:
                satur[csum - (n - 1 - Sigma)] += 1   # >0 would CONTRADICT the charge bound (if G were a target)
                if csum >= n - 1 and len(examples) < 3:
                    examples.append((csum, Sigma))
print(f"n={n} trials={TRIALS} chi4-instances(v,phi) with 2+2+2: {n_inst}")
print("key=(tether, csum-(n-1), Sigma) counts:", dict(sorted(stats.items())))
print("csum - (n-1-Sigma) distribution on tether-ok instances:", dict(sorted(satur.items())))
print("examples csum>=n-1:", examples)
