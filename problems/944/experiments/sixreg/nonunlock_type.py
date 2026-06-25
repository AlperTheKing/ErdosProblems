"""For each always-balanced B, characterize the NON-UNLOCKING vertices: their
deficiency b(w), whether they are in the deficiency support, and how many of the
6 cut units lie in their closed neighbourhood. Aggregates the pattern to guide
an all-sizes proof of the candidate theorem.
usage: geng -c -D6 n e:e | python nonunlock_type.py n
"""
import sys
n = int(sys.argv[1])
def g6decode(s):
    nn = ord(s[0]) - 63
    adj = [set() for _ in range(nn)]
    bit = 0
    for j in range(1, nn):
        for i in range(j):
            byte = 1 + bit // 6; off = 5 - bit % 6
            if (ord(s[byte]) - 63) >> off & 1:
                adj[i].add(j); adj[j].add(i)
            bit += 1
    return nn, adj
def all_colourings(nn, adj, skip=-1):
    verts = [v for v in range(nn) if v != skip]
    verts.sort(key=lambda v: -len(adj[v]))
    col = {}
    def bt(i):
        if i == len(verts):
            yield dict(col); return
        v = verts[i]
        used = {col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c in used: continue
            col[v] = c
            yield from bt(i+1)
            del col[v]
    yield from bt(0)
def always_balanced(nn, adj, b):
    any_c=False
    for col in all_colourings(nn, adj):
        w=[0,0,0]
        for v in range(nn): w[col[v]] += b[v]
        if tuple(sorted(w)) != (2,2,2): return False
        any_c=True
    return any_c
def unlocks(nn, adj, w, units):
    for col in all_colourings(nn, adj, skip=w):
        pres=[0,0,0]
        for v in units:
            if v==w: continue
            pres[col[v]]=1
        if not all(pres): return True
    return False
from collections import Counter
btype = Counter(); supp_cnt = Counter(); ncount = Counter()
graphs=0
for line in sys.stdin:
    line=line.strip()
    if not line or line[0]=='>': continue
    nn, adj = g6decode(line)
    b=[6-len(adj[v]) for v in range(nn)]
    if sum(b)!=6: continue
    seen={0}; st=[0]
    while st:
        x=st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    if len(seen)!=nn: continue
    if not always_balanced(nn,adj,b): continue
    graphs+=1
    units=[v for v in range(nn) for _ in range(b[v])]
    support=set(v for v in range(nn) if b[v]>0)
    nonunlockers=[w for w in range(nn) if not unlocks(nn,adj,w,units)]
    ncount[len(nonunlockers)]+=1
    for w in nonunlockers:
        btype[b[w]] += 1
        supp_cnt['in_support' if w in support else 'full_interior'] += 1
print(f"n={n} alwaysBalanced={graphs}")
print(f"  #nonunlockers per graph: {dict(sorted(ncount.items()))}")
print(f"  nonunlocker b-value dist: {dict(sorted(btype.items()))}")
print(f"  nonunlocker location: {dict(supp_cnt)}")
