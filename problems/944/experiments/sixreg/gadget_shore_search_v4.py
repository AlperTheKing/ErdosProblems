"""v4: SECOND gadget family — support = K_{2,2,2} (octahedron) with b=1 on each of
its six vertices; all other vertices degree 6. K_{2,2,2} is uniquely 3-colourable
(its colour classes are the three antipodal pairs), so every proper colouring of H
gives the six support vertices colours in pairs => deficiency-weighted boundary
vector (2,2,2) for every colouring => filter [C] passes automatically.

Construction: tripartite parts P0,P1,P2 (3-colourable by construction); the support
pairs are {p_i, q_i} in part i; support cross edges realize K_{2,2,2} (all pairs in
different parts adjacent: 12 edges); support vertices need degree 5 (b=1), i.e.
5 - 4 = 1 extra cross edge each; non-support vertices need degree 6 (3+3).
Test [T] localized and [K] boundary-shortfall.
usage: python gadget_shore_search_v4.py <a> <samples> [seed]   (a div by 3, a>=12)
"""
import random, sys

a = int(sys.argv[1]); SAMPLES = int(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 944
rng = random.Random(seed)
assert a % 3 == 0 and a >= 12
q = a // 3
parts = [list(range(i*q, (i+1)*q)) for i in range(3)]
SUP = [(parts[i][0], parts[i][1]) for i in range(3)]   # pair per part
SUPV = [v for pr in SUP for v in pr]

def sample_graph():
    adj = [set() for _ in range(a)]
    def add(u, v):
        if v in adj[u] or u == v: return False
        adj[u].add(v); adj[v].add(u); return True
    # K_{2,2,2} on the support: all cross-part support pairs adjacent
    for i in range(3):
        for j in range(i+1, 3):
            for u in SUP[i]:
                for v in SUP[j]:
                    add(u, v)
    # degree targets: support 5 (b=1), others 6; support already has 4
    for i in range(3):
        for j in range(i+1, 3):
            need = {}
            for v in parts[i] + parts[j]:
                if v in SUPV:
                    # one extra cross edge total; give it to the lexicographically
                    # first pair (i,j) combination the vertex participates in
                    pass
            # support extras: each support vertex needs exactly 1 more cross edge
            # overall; assign it to a RANDOM other part per vertex (decided below)
            pass
    # decide support extra-edge part assignment first
    extra_part = {}
    for v in SUPV:
        myp = next(i for i in range(3) if v in parts[i])
        extra_part[v] = rng.choice([j for j in range(3) if j != myp])
    for i in range(3):
        for j in range(i+1, 3):
            need = {}
            for v in parts[i]:
                if v in SUPV: need[v] = 1 if extra_part[v] == j else 0
                else: need[v] = 3
            for v in parts[j]:
                if v in SUPV: need[v] = 1 if extra_part[v] == i else 0
                else: need[v] = 3
            for rounds in range(80):
                left = [v for v in parts[i] if need[v] > 0]
                right = [v for v in parts[j] if need[v] > 0]
                if not left and not right: break
                rng.shuffle(left); rng.shuffle(right)
                for u, v in zip(left, right):
                    if need[u] > 0 and need[v] > 0 and v not in adj[u]:
                        if add(u, v): need[u] -= 1; need[v] -= 1
            if any(need[v] > 0 for v in parts[i] + parts[j]):
                return None
    return adj

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
    # sanity: degree check
    if any(len(adj[v]) != (5 if v in SUPV else 6) for v in range(a)): continue
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
    print(f"VALID SHORE FOUND a={a} sample={s}: {edges}", flush=True)
    if hits >= 3: break
print(f"a={a} samples={SAMPLES} realized={tried} failT={failT} failK={failK} validShores={hits}", flush=True)
