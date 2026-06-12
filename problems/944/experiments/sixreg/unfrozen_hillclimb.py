"""Hill-climb from GPT's B (1/15 unfrozen) maximizing deletion-unfrozen vertex count
over connected 6-regular 3-colourable graphs on n=15 via degree-preserving 2-swaps.
Reaching 15/15 would refute the reduced kernel ("at least one frozen vertex").
usage: python unfrozen_hillclimb.py <steps> [seed]
"""
import random, sys
n = 15
STEPS = int(sys.argv[1]); rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 944)
E0 = [(0,1),(0,7),(0,9),(0,10),(0,13),(0,14),(1,2),(1,3),(1,8),(1,11),(1,14),
      (2,6),(2,7),(2,9),(2,11),(2,13),(3,6),(3,7),(3,8),(3,13),(3,14),
      (4,6),(4,7),(4,8),(4,10),(4,11),(4,13),(5,7),(5,8),(5,10),(5,11),(5,13),(5,14),
      (6,9),(6,10),(6,12),(7,9),(8,9),(8,12),(9,14),(10,11),(10,12),(11,12),(12,13),(12,14)]
adj = [set() for _ in range(n)]
for u,v in E0: adj[u].add(v); adj[v].add(u)
def connected(a):
    seen={0}; st=[0]
    while st:
        x=st.pop()
        for y in a[x]:
            if y not in seen: seen.add(y); st.append(y)
    return len(seen)==n
def col3(a):
    col={}
    def bt(i):
        if i==n: return True
        used={col[u] for u in a[i] if u in col}
        for c in range(3):
            if c not in used:
                col[i]=c
                if bt(i+1): return True
                del col[i]
        return False
    return bt(0)
def unfrozen_at(a, v):
    verts=[u for u in range(n) if u!=v]
    col={}; found=[False]
    def bt(i):
        if found[0]: return
        if i==len(verts):
            cnt=[0,0,0]
            for u in a[v]: cnt[col[u]]+=1
            if cnt==[2,2,2]: found[0]=True
            return
        w=verts[i]
        used={col[u] for u in a[w] if u in col}
        for c in range(3):
            if c not in used:
                col[w]=c; bt(i+1); del col[w]
                if found[0]: return
    bt(0)
    return found[0]
def score(a): return sum(1 for v in range(n) if unfrozen_at(a, v))
cur = score(adj); best = cur
print("start score:", cur, flush=True)
for step in range(STEPS):
    edges = [(u,v) for u in range(n) for v in adj[u] if u<v]
    (a,b) = rng.choice(edges); (c,d) = rng.choice(edges)
    if len({a,b,c,d}) != 4: continue
    if rng.random() < 0.5: c,d = d,c
    if c in adj[a] or d in adj[b]: continue
    adj[a].discard(b); adj[b].discard(a); adj[c].discard(d); adj[d].discard(c)
    adj[a].add(c); adj[c].add(a); adj[b].add(d); adj[d].add(b)
    if not (connected(adj) and col3(adj)):
        ok = False
    else:
        s = score(adj)
        ok = s >= cur
        if ok: cur = s
    if not ok:
        adj[a].discard(c); adj[c].discard(a); adj[b].discard(d); adj[d].discard(b)
        adj[a].add(b); adj[b].add(a); adj[c].add(d); adj[d].add(c)
    if cur > best:
        best = cur
        print(f"step {step}: new best {best}/{n}", flush=True)
        if best == n:
            print("FULL UNFROZEN GRAPH:", sorted((u,v) for u in range(n) for v in adj[u] if u<v), flush=True)
            break
print(f"final best={best}/{n} after {STEPS} steps", flush=True)
