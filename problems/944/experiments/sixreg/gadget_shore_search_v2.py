"""v2: sample candidate shores INSIDE the 3-colourable family (tripartite by
construction). Parts P0,P1,P2 of sizes ~a/3; only cross edges; support triangle =
one degree-4 vertex per part (intact triangle => rainbow in every colouring =>
filter [C] passes for the boundary vector (2,2,2)). All other vertices degree 6.
Test [T] localized and [K] boundary-shortfall (over ALL colourings of H-v, not just
the construction partition). A hit at size a = the machine terminates at a.
usage: python gadget_shore_search_v2.py <a> <samples> [seed]
"""
import random, sys

a = int(sys.argv[1]); SAMPLES = int(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 944
rng = random.Random(seed)

q, r = divmod(a, 3)
sizes = [q + (1 if i < r else 0) for i in range(3)]
parts = []
x = 0
for s in sizes:
    parts.append(list(range(x, x + s))); x += s
SUP = [parts[0][0], parts[1][0], parts[2][0]]
DEG = {v: (4 if v in SUP else 6) for v in range(a)}
part_of = {}
for i, P in enumerate(parts):
    for v in P: part_of[v] = i

def sample_graph():
    adj = [set() for _ in range(a)]
    def can(u, v): return part_of[u] != part_of[v] and v not in adj[u] and u != v
    def add(u, v): adj[u].add(v); adj[v].add(u)
    add(SUP[0], SUP[1]); add(SUP[1], SUP[2]); add(SUP[0], SUP[2])
    stubs = []
    for v in range(a):
        stubs += [v] * (DEG[v] - len(adj[v]))
    for attempt in range(400):
        rng.shuffle(stubs)
        test = [set(s) for s in adj]
        ok = True
        for i in range(0, len(stubs), 2):
            u, v = stubs[i], stubs[i+1]
            if part_of[u] == part_of[v] or u == v or v in test[u]: ok = False; break
            test[u].add(v); test[v].add(u)
        if ok: return test
    return None

def connected(adj):
    seen = {0}; st = [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    return len(seen) == a

def K_ok_at(adj, v):
    verts = [u for u in range(a) if u != v]
    b = 6 - len(adj[v])
    col = {}
    found = [False]
    def bt(i):
        if found[0]: return
        if i == len(verts):
            cnt = [0,0,0]
            for u in adj[v]: cnt[col[u]] += 1
            if sum(max(0, 2-c) for c in cnt) <= b: found[0] = True
            return
        w = verts[i]
        used = {col[u] for u in adj[w] if u in col}
        for c in range(3):
            if c not in used:
                col[w] = c; bt(i+1); del col[w]
                if found[0]: return
    bt(0)
    return found[0]

hits = 0; tried = 0; failT = 0; failK = 0
for s in range(SAMPLES):
    adj = sample_graph()
    if adj is None or not connected(adj): continue
    tried += 1
    badT = False
    for u in range(a):
        if len(adj[u]) != 6: continue
        for v in range(a):
            if v == u or v in adj[u]: continue
            if adj[u] - {v} <= adj[v]: badT = True; break
        if badT: break
    if badT: failT += 1; continue
    okK = True
    for v in range(a):
        if not K_ok_at(adj, v): okK = False; break
    if not okK: failK += 1; continue
    hits += 1
    edges = sorted((u,v) for u in range(a) for v in adj[u] if u < v)
    print(f"VALID SHORE FOUND a={a} sample={s} parts={sizes}: {edges}", flush=True)
    if hits >= 3: break
print(f"a={a} samples={SAMPLES} simple+connected={tried} failT={failT} failK={failK} validShores={hits}", flush=True)
