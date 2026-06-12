"""v3: tripartite candidate shores via unions of random matchings.

Between each ordered part pair, every non-support vertex needs 3 edges to each other
part; support vertices need 2 to each other part (1 triangle edge + 1 extra).
Realize each inter-part bipartite graph as a union of random near-perfect matchings
with collision repair, then test [T] and [K]. All graphs 3-colourable by
construction; the intact support triangle forces boundary vector (2,2,2) in every
colouring, so [C] passes.
usage: python gadget_shore_search_v3.py <a> <samples> [seed]   (a divisible by 3)
"""
import random, sys

a = int(sys.argv[1]); SAMPLES = int(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 944
rng = random.Random(seed)
assert a % 3 == 0
q = a // 3
parts = [list(range(i*q, (i+1)*q)) for i in range(3)]
SUP = [parts[i][0] for i in range(3)]

def sample_graph():
    adj = [set() for _ in range(a)]
    def add(u, v):
        if v in adj[u]: return False
        adj[u].add(v); adj[v].add(u); return True
    # support triangle
    add(SUP[0], SUP[1]); add(SUP[1], SUP[2]); add(SUP[0], SUP[2])
    # between parts i<j: bipartite degrees: support vertex needs 1 more (after triangle), others 3
    for i in range(3):
        for j in range(i+1, 3):
            need = {v: (1 if v in SUP else 3) for v in parts[i] + parts[j]}
            # repeated random matching rounds until all needs met
            for rounds in range(60):
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

hits = 0; tried = 0; failT = 0; failK = 0; firstfailv = {}
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
        if not K_ok_at(adj, v):
            okK = False
            firstfailv[v] = firstfailv.get(v, 0) + 1
            break
    if not okK: failK += 1; continue
    hits += 1
    edges = sorted((u,v) for u in range(a) for v in adj[u] if u < v)
    print(f"VALID SHORE FOUND a={a} sample={s}: {edges}", flush=True)
    if hits >= 3: break
print(f"a={a} samples={SAMPLES} realized={tried} failT={failT} failK={failK} validShores={hits} Kfail-vertex-hist={dict(sorted(firstfailv.items())[:6])}", flush=True)
