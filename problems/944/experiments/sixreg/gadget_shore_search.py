"""Constructive search for a VALID 6-cut shore at larger a (machine-termination test).

Target: connected H on a vertices, degree sequence (4,4,4,6,...,6) with the three
degree-4 vertices forming an INTACT triangle (the support gadget: every proper
3-colouring colours them rainbow, so the deficiency-weighted boundary vector is
(2,2,2) for every colouring => filter [C] passes automatically). Then H is a valid
shore iff it is 3-colourable and passes [T] (localized comparable nonneighbours at
b=0 vertices) and [K] (boundary-shortfall at every vertex).

A hit at size a proves the shore-exclusion machine terminates at a (the candidate
family is realizable); persistent failure is evidence for the rigidity-bridge
conjecture. Sampling: pairing-model with fixed degree sequence + forced triangle,
then local edge-swap repair for simplicity/connectivity.
usage: python gadget_shore_search.py <a> <samples> [seed]
"""
import random, sys
from itertools import combinations

a = int(sys.argv[1]); SAMPLES = int(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 944
rng = random.Random(seed)
SUP = [0, 1, 2]   # support triangle, degree 4 each (2 slots besides the triangle)
DEG = {v: (4 if v in SUP else 6) for v in range(a)}

def sample_graph():
    """random simple graph with the fixed degree sequence containing triangle 0-1-2."""
    adj = [set() for _ in range(a)]
    def add(u, v): adj[u].add(v); adj[v].add(u)
    add(0,1); add(1,2); add(0,2)
    stubs = []
    for v in range(a):
        need = DEG[v] - len(adj[v])
        stubs += [v]*need
    for _ in range(200):
        rng.shuffle(stubs)
        ok = True
        test = [set(s) for s in adj]
        for i in range(0, len(stubs), 2):
            u, v = stubs[i], stubs[i+1]
            if u == v or v in test[u]: ok = False; break
            test[u].add(v); test[v].add(u)
        if ok:
            return test
    return None

def connected(adj):
    seen = {0}; st = [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    return len(seen) == a

def colourings(adj, skip=-1, collect=False, need_222_at=None):
    verts = [v for v in range(a) if v != skip]
    out = []
    col = {}
    found = [False]
    def bt(i):
        if found[0] and not collect: return
        if i == len(verts):
            if need_222_at is not None:
                cnt = [0,0,0]
                for u in adj[need_222_at]:
                    if u != skip: cnt[col[u]] += 1
                b = 6 - len(adj[need_222_at])
                short = sum(max(0, 2-c) for c in cnt)
                if short <= b: found[0] = True
            else:
                found[0] = True
                if collect: out.append(dict(col))
            return
        v = verts[i]
        used = {col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v] = c; bt(i+1)
                del col[v]
                if found[0] and not collect: return
    bt(0)
    return found[0], out

hits = 0; tried = 0; threecol = 0; passK = 0
for s in range(SAMPLES):
    adj = sample_graph()
    if adj is None or not connected(adj): continue
    tried += 1
    ok3, _ = colourings(adj)
    if not ok3: continue
    threecol += 1
    # [T]: localized comparable nonneighbours at full-degree vertices
    badT = False
    for u in range(a):
        if len(adj[u]) != 6: continue
        for v in range(a):
            if v == u or v in adj[u]: continue
            if adj[u] - {v} <= adj[v]: badT = True; break
        if badT: break
    if badT: continue
    # [K] at every vertex
    okK = True
    for v in range(a):
        ok, _ = colourings(adj, skip=v, need_222_at=v)
        if not ok: okK = False; break
    if not okK: continue
    passK += 1
    hits += 1
    edges = sorted((u,v) for u in range(a) for v in adj[u] if u < v)
    print(f"VALID SHORE FOUND a={a} sample={s}: {edges}", flush=True)
    if hits >= 3: break
print(f"a={a} samples={SAMPLES} simple+connected={tried} threecol={threecol} validShores={hits}", flush=True)
