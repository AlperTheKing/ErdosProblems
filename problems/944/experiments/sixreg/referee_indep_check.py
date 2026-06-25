# INDEPENDENT referee check of H1 (built from the TEXT description, not the
# original script). Different data structures, different search (iterative
# product over independent-set structure + a full exhaustive check exploiting
# the bipartition), plus the anchor-local 729-case argument.
import itertools, sys

# --- Build H1 exactly as described in Section 1 of the refutation text ---
P = ['x1','x2','x3'] + ['p%d' % i for i in range(6)]
Q = ['y1','y2','y3'] + ['q%d' % i for i in range(6)]
E = []
# (a) full K_{3,3} on anchors
for i in (1,2,3):
    for j in (1,2,3):
        E.append(('x%d'%i, 'y%d'%j))
# (b) anchor fillers: x1~q0,q1; x2~q2,q3; x3~q4,q5; y1~p0,p1; y2~p2,p3; y3~p4,p5
pairs = {1:(0,1), 2:(2,3), 3:(4,5)}
for i in (1,2,3):
    a,b = pairs[i]
    E.append(('x%d'%i,'q%d'%a)); E.append(('x%d'%i,'q%d'%b))
    E.append(('y%d'%i,'p%d'%a)); E.append(('y%d'%i,'p%d'%b))
# (c) filler block K_{6,6} minus PM
for i in range(6):
    for j in range(6):
        if i != j:
            E.append(('p%d'%i,'q%d'%j))

# simplicity: no duplicate edges
canon = set(frozenset(e) for e in E)
assert len(canon) == len(E) == 51, (len(canon), len(E))

V = P + Q
adj = {v: set() for v in V}
for u,v in E:
    assert (u in P) != (v in P), "edge inside a part: not bipartite w.r.t. (P,Q)"
    adj[u].add(v); adj[v].add(u)

# structural hypotheses
deg = {v: len(adj[v]) for v in V}
anchors = ['x1','x2','x3','y1','y2','y3']
assert max(deg.values()) == 6
assert sorted(v for v in V if deg[v]==5) == sorted(anchors)
assert all(deg[v]==6 for v in V if v not in anchors)
# connectivity
seen, stack = {V[0]}, [V[0]]
while stack:
    u = stack.pop()
    for w in adj[u]:
        if w not in seen:
            seen.add(w); stack.append(w)
assert len(seen) == 18
print("H1 independent structural check: PASS (18 vtx, 51 edges, bipartite, connected, exactly the 6 anchors have deg 5, rest deg 6)")

gamma = {'x1':0,'x2':1,'x3':2,'y1':0,'y2':1,'y3':2}

# --- Check 1: anchor-local argument. Any proper colouring restricted to the
# anchors is a proper colouring of the K_{3,3} on them. Enumerate all 3^6.
ok_exists = False
n_proper = 0
for cs in itertools.product(range(3), repeat=6):
    c = dict(zip(anchors, cs))
    if all(c['x%d'%i] != c['y%d'%j] for i in (1,2,3) for j in (1,2,3)):
        n_proper += 1
        if all(c[a] != gamma[a] for a in anchors):
            ok_exists = True
print("anchor K33: %d proper colourings; ban-avoiding one exists: %s" % (n_proper, ok_exists))
assert n_proper == 42 and not ok_exists

# --- Check 2: FULL exhaustive over H1 (no backtracking shortcuts): enumerate
# all 3^9 colourings of P, derive allowed sets for each Q vertex, check.
Plist = list(P)
found = None
cnt_pcols = 0
for cs in itertools.product(range(3), repeat=9):
    cp = dict(zip(Plist, cs))
    if cp['x1']==0 or cp['x2']==1 or cp['x3']==2:
        continue
    cnt_pcols += 1
    ok = True
    for v in Q:
        allowed = {0,1,2} - {cp[w] for w in adj[v]}
        if v in gamma:
            allowed -= {gamma[v]}
        if not allowed:
            ok = False; break
    if ok:
        found = cp; break
print("full exhaustive (3^9 P-side x independent Q-side completion): witness found:", found)
assert found is None
print("INDEPENDENT VERDICT: H1 with rainbow bans is UNSAT -- lemma REFUTED")

# --- Check 3 (sanity/control): flipping one ban makes it colourable
gamma2 = dict(gamma); gamma2['x3'] = 1
found2 = None
for cs in itertools.product(range(3), repeat=9):
    cp = dict(zip(Plist, cs))
    if any(cp[a]==gamma2[a] for a in ('x1','x2','x3')):
        continue
    ass = {}
    ok = True
    for v in Q:
        allowed = {0,1,2} - {cp[w] for w in adj[v]}
        if v in gamma2:
            allowed -= {gamma2[v]}
        if not allowed:
            ok = False; break
        ass[v] = min(allowed)
    if ok:
        found2 = (cp, ass); break
assert found2 is not None
cp, ass = found2
full = dict(cp); full.update(ass)
assert all(full[u]!=full[v] for u,v in E)
assert all(full[a]!=gamma2[a] for a in anchors)
print("control (gamma with x3->1): COLOURABLE, witness verified edge-by-edge")
print("ALL INDEPENDENT CHECKS PASS")
