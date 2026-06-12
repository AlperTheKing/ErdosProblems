"""Independent Python re-implementation of the full shore filter battery
(enum_shore.cpp): [B] deficiency, [C] all-colourings boundary vector, [T] comparable
nonneighbours, [K] generalized local Lemma-1.1 kill test.
usage: geng -q -c -D6 a E:E | python verify_shore_indep.py a
"""
import sys

A = int(sys.argv[1])
ALLOWED = {(6,0,0),(4,1,1),(3,3,0),(2,2,2)}

def g6_to_adj(s, n):
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    need = n * (n - 1) // 2
    if len(bits) < need:
        return None
    adj = [0]*n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]: adj[i] |= 1 << j; adj[j] |= 1 << i
            idx += 1
    return adj

def colourings(n, adj, skip=-1):
    verts = [v for v in range(n) if v != skip]
    out = []
    col = {}
    def bt(i):
        if i == len(verts): out.append(dict(col)); return
        v = verts[i]
        used = set()
        m = adj[v]
        while m:
            u = (m & -m).bit_length() - 1; m &= m - 1
            if u in col: used.add(col[u])
        for c in range(3):
            if c not in used:
                col[v] = c; bt(i+1); del col[v]
    bt(0)
    return out

cnt = dict(total=0, not3col=0, badvec=0, badtwin=0, localKill=0, SURVIVORS=0)
for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith('>'): continue
    n = ord(line[0]) - 63
    if n != A:
        continue
    adj = g6_to_adj(line, n)
    if adj is None:
        continue
    cnt['total'] += 1
    deg = [bin(adj[v]).count('1') for v in range(n)]
    b = [6 - d for d in deg]
    cols = colourings(n, adj)
    if not cols: cnt['not3col'] += 1; continue
    bad = False
    for col in cols:
        s = [0,0,0]
        for v in range(n): s[col[v]] += b[v]
        if tuple(sorted(s, reverse=True)) not in ALLOWED: bad = True; break
    if bad: cnt['badvec'] += 1; continue
    twin = False
    for u in range(n):
        if b[u] != 0: continue
        for v in range(n):
            if v == u or (adj[u] >> v) & 1: continue
            nu = adj[u] & ~(1 << v)
            if nu & ~adj[v] == 0: twin = True; break
        if twin: break
    if twin: cnt['badtwin'] += 1; continue
    dead = False
    for v in range(n):
        ok = False
        for col in colourings(n, adj, skip=v):
            c3 = [0,0,0]
            m = adj[v]
            while m:
                u = (m & -m).bit_length() - 1; m &= m - 1
                c3[col[u]] += 1
            if sum(max(0, 2 - x) for x in c3) <= b[v]: ok = True; break
        if not ok: dead = True; break
    if dead: cnt['localKill'] += 1; continue
    cnt['SURVIVORS'] += 1
    print('SURVIVOR:', line)
print('PY', A, cnt)
