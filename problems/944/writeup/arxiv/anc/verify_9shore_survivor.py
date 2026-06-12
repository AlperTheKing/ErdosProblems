"""Independent verification of the unique 9-shore survivor HEzftz{ and of the
enum_9shore filter logic (recount the 729-graph classification in pure Python)."""
import itertools, sys
from itertools import product

def g6_to_adj(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]: adj[i].add(j); adj[j].add(i)
            idx += 1
    return n, adj

ALLOWED = {(6,0,0),(4,1,1),(3,3,0),(2,2,2)}

def classify(n, adj):
    deg = [len(adj[v]) for v in range(n)]
    b = [6 - d for d in deg]
    if any(x < 0 or x > 5 for x in b): return 'badB', None
    cols = []
    def bt(i, col):
        if i == n: cols.append(tuple(col)); return
        used = {col[u] for u in adj[i] if u < i}
        for c in range(3):
            if c not in used:
                col.append(c); bt(i+1, col); col.pop()
    bt(0, [])
    if not cols: return 'not3col', None
    for col in cols:
        s = [0,0,0]
        for v in range(n): s[col[v]] += b[v]
        if tuple(sorted(s, reverse=True)) not in ALLOWED: return 'badvec', None
    for u in range(n):
        if b[u] != 0: continue
        for v in range(n):
            if v == u or v in adj[u]: continue
            if (adj[u] - {v}) <= adj[v]: return 'badtwin', None
    return 'SURVIVOR', (b, cols)

# Full recount over geng output piped in
counts = {}
surv = []
for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith('>'): continue
    n, adj = g6_to_adj(line)
    assert n == 9 and sum(len(a) for a in adj)//2 == 24
    tag, info = classify(n, adj)
    counts[tag] = counts.get(tag, 0) + 1
    if tag == 'SURVIVOR': surv.append((line, adj, info))
print('python recount:', counts)
for line, adj, (b, cols) in surv:
    print('SURVIVOR', line, 'b=', ''.join(map(str,b)), 'ncol=', len(cols))
    print('  edges:', sorted((i,j) for i in range(9) for j in adj[i] if i<j))
    print('  degseq:', [len(adj[v]) for v in range(9)])
    col = cols[0]
    print('  colouring (rep):', col)
    s = [0,0,0]
    for v in range(9): s[col[v]] += b[v]
    print('  boundary vector:', s)
    # connectivity check
    seen = {0}; st=[0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    print('  connected:', len(seen)==9)
    # triangle / structure hints
    from itertools import combinations
    tri = sum(1 for a,bb,c in combinations(range(9),3) if bb in adj[a] and c in adj[a] and c in adj[bb])
    print('  triangles:', tri)
    # complement structure
    comp = [(i,j) for i in range(9) for j in range(i+1,9) if j not in adj[i]]
    print('  complement edges (12):', comp)
