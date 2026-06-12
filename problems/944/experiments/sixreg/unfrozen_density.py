"""Random search: how dense can deletion-unfrozen vertices get in connected
6-regular 3-colourable graphs? Tracks max unfrozen count per n; any graph with
ALL vertices unfrozen refutes the reduced kernel (and likely the bridge).
usage: python unfrozen_density.py <n> <samples> [seed]
"""
import random, sys
n = int(sys.argv[1]); SAMPLES = int(sys.argv[2])
rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 944)
def rand_6reg_3col(n):
    assert n % 3 == 0
    q = n // 3
    parts = [list(range(i*q, (i+1)*q)) for i in range(3)]
    adj = [set() for _ in range(n)]
    def add(u, v):
        if v in adj[u]: return False
        adj[u].add(v); adj[v].add(u); return True
    for i in range(3):
        for j in range(i+1, 3):
            need = {v: 3 for v in parts[i] + parts[j]}
            for rounds in range(80):
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
    return len(seen) == n
def unfrozen_at(adj, v):
    verts = [u for u in range(n) if u != v]
    col = {}; found = [False]
    def bt(i):
        if found[0]: return
        if i == len(verts):
            cnt = [0,0,0]
            for u in adj[v]: cnt[col[u]] += 1
            if cnt == [2,2,2]: found[0] = True
            return
        w = verts[i]
        used = {col[u] for u in adj[w] if u in col}
        for c in range(3):
            if c not in used:
                col[w] = c; bt(i+1); del col[w]
                if found[0]: return
    bt(0)
    return found[0]
best = -1; bestg = None; tried = 0; hist = {}
for s in range(SAMPLES):
    adj = rand_6reg_3col(n)
    if adj is None or not connected(adj): continue
    tried += 1
    cnt = sum(1 for v in range(n) if unfrozen_at(adj, v))
    hist[cnt] = hist.get(cnt, 0) + 1
    if cnt > best:
        best = cnt
        bestg = sorted((u,v) for u in range(n) for v in adj[u] if u < v)
print(f"n={n} samples={SAMPLES} realized={tried} hist={dict(sorted(hist.items()))} MAXunfrozen={best}/{n}")
if best >= n - 2:
    print("NEAR-FULL UNFROZEN GRAPH:", bestg)
