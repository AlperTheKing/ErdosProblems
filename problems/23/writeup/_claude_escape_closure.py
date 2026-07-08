r"""Compute the ESCAPE CLOSURE of the lens W in GPT-Pro's 11-vtx max-cut counterpattern.
GPT-Pro's def: D_0 = W; D_{k+1} = D_k union {shortest-support of every bad edge h whose support meets BOTH D_k and
V\D_k}. If the closure D = whole cage C, then GPT-Pro's example concretely realizes the FULL-closure branch of
EscapingClosureDichotomy at a genuine maximum cut (it is non-deficient, so minimality does not apply). Exact BFS.
Run from problems/23/writeup."""
from collections import deque

V = ['p','q','a','b','bb','c','y','w','r1','r2','r3']
B = [('p','a'),('a','b'),('b','c'),('c','y'),('q','c'),('c','bb'),('bb','a'),('a','w'),
     ('p','r1'),('r1','r2'),('r2','r3'),('r3','q')]
M = [('p','y'),('q','w'),('p','q')]
adjB = {v:set() for v in V}
for u,w in B: adjB[u].add(w); adjB[w].add(u)

def geo_support(s,t):
    ds={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for w in adjB[u]:
            if w not in ds: ds[w]=ds[u]+1; q.append(w)
    D=ds.get(t)
    if D is None: return set()
    dt={t:0}; q=deque([t])
    while q:
        u=q.popleft()
        for w in adjB[u]:
            if w not in dt: dt[w]=dt[u]+1; q.append(w)
    return {v for v in V if ds.get(v) is not None and dt.get(v) is not None and ds[v]+dt[v]==D}

supp = {m: geo_support(*m) for m in M}
print("=== escape closure of the lens W (GPT-Pro 11-vtx counterpattern) ===")
for m in M:
    print("  support(%s-%s) = %s"%(m[0],m[1],sorted(supp[m])))

W = {'a','b','bb','c','y','w'}
D = set(W)
step = 0
while True:
    added = set()
    for m in M:
        s = supp[m]
        if (s & D) and (s - D):   # support meets both D and V\D
            added |= (s - D)
    if not added:
        break
    D |= added
    step += 1
    print("  step %d: added %s -> |D|=%d"%(step, sorted(added), len(D)))

print("="*60)
print("ESCAPE CLOSURE D = %s (|D|=%d, |C|=%d)"%(sorted(D), len(D), len(V)))
if D == set(V):
    print("=> D = C (the WHOLE cage). GPT-Pro's counterpattern concretely realizes the FULL-closure branch of")
    print("   EscapingClosureDichotomy AT A GENUINE MAXIMUM CUT. Since it is NON-deficient (Gamma=75<N^2=121),")
    print("   minimality does not apply -- consistent with the conjecture. The open question is whether a DEFICIENT")
    print("   full-closure can exist: that is the full-bank Hall / reduced-minimal-ledger core.")
else:
    print("=> D < C (proper). Then in a min-neg cage minimality would kill it; re-examine whether the escape closure")
    print("   is really full for this example.")
