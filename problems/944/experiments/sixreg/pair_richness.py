"""LEMMA E test: which (colour(p), colour(l)) pairs are realizable by proper
3-colourings of the PG-repair shore A? If ALL 9: A can never be the 3+3 shore
of a 6-regular (4,1)-graph (new criticality filter [P]); pair-poor would be
the only escape."""
import itertools, random
rng = random.Random(944)
pts = [(x,y,1) for x in range(5) for y in range(5)] + [(x,1,0) for x in range(5)] + [(1,0,0)]
N = 62
adj = [set() for _ in range(N)]
for a in range(31):
    for b in range(31):
        if (pts[a][0]*pts[b][0] + pts[a][1]*pts[b][1] + pts[a][2]*pts[b][2]) % 5 == 0:
            adj[a].add(31+b); adj[31+b].add(a)
# surgery p=0, l=10 with seed 944 (same as C++ instance 1): emulate
p, lv = 0, 31+10
Ls = rng.sample(sorted(adj[p]), 3); Ps = rng.sample(sorted(adj[lv]), 3)
for L in Ls: adj[p].discard(L); adj[L].discard(p)
for Q in Ps: adj[lv].discard(Q); adj[Q].discard(lv)
done = False
for perm in itertools.permutations(range(3)):
    if all(Ls[perm[j]] not in adj[Ps[j]] for j in range(3)):
        for j in range(3): adj[Ps[j]].add(Ls[perm[j]]); adj[Ls[perm[j]]].add(Ps[j])
        done = True; break
assert done
b = [6-len(adj[v]) for v in range(N)]
assert sum(b) == 6 and b[p] == 3 and b[lv] == 3
def colour_with(cp, cl, cap=3_000_000):
    """exists proper 3-colouring with col(p)=cp, col(lv)=cl?"""
    order = [p, lv] + sorted((u for u in range(N) if u not in (p,lv)), key=lambda u: -len(adj[u]))
    col = {}; nodes = [0]
    def bt(i):
        nodes[0] += 1
        if nodes[0] > cap: return None
        if i == len(order): return True
        w = order[i]
        opts = [cp] if w == p else [cl] if w == lv else range(3)
        for c in opts:
            if any(col.get(u) == c for u in adj[w]): continue
            col[w] = c
            r = bt(i+1)
            if r: return True
            del col[w]
            if r is None: return None
        return False
    return bt(0)
res = {}
for cp in range(3):
    for cl in range(3):
        res[(cp,cl)] = colour_with(cp, cl)
print("realizable (colour(p),colour(l)) pairs:")
for k in sorted(res): print(f"  {k}: {res[k]}")
n_yes = sum(1 for v in res.values() if v)
print(f"pairs realized: {n_yes}/9  (None=cap-unresolved)")
if n_yes == 9:
    print("PAIR-RICH: by LEMMA E, this shore CANNOT sit in any (4,1)-graph — new filter [P] kills PG-repair.")
