#!/usr/bin/env python3
"""EXACT audit of GPT-Pro round-10 (PREFIX-HALL) concrete claims on the n=8 witness G?`F`w.
Verifies, line by line, every checkable arithmetic claim before adopting PREFIX-HALL as the target:
  (1) G?`F`w parses to edges {04,06,15,16,26,27,36,37,47,57}
  (2) maxcut=8 (beta=2) realised by the bipartition {0,1,2,3}|{4,5,6,7}; bad edges = {47,57}
  (3) ell(47)=ell(57)=5; Gamma=50; N^2-Gamma=14
  (4) the four shortest 5-cycles GPT lists
  (5) the suffix 6-2-7 is SHARED by geodesics 4-0-6-2-7 and 5-1-6-2-7 (segment-disjointness fails)
Reuses the from-scratch machinery in verify_iii_independent.py (no flagsdp import)."""
from verify_iii_independent import dec, maxcut_all, geos

G6 = "G?`F`w"
n, E = dec(G6)
adj = [set() for _ in range(n)]
for u, v in E:
    adj[u].add(v); adj[v].add(u)

print(f"=== AUDIT of GPT round-10 n=8 witness {G6!r} ===")
# (1) edges
claimed_edges = {(0,4),(0,6),(1,5),(1,6),(2,6),(2,7),(3,6),(3,7),(4,7),(5,7)}
got = set((min(u,v),max(u,v)) for u,v in E)
print(f"(1) n={n} (expect 8: {n==8}); edges match GPT: {got==claimed_edges}")
if got != claimed_edges:
    print(f"    GOT   {sorted(got)}")
    print(f"    CLAIM {sorted(claimed_edges)}")

# (2) maxcut + the specific bipartition
edges = [(min(u,v),max(u,v)) for u,v in E]
best = -1
for m in range(1<<(n-1)):
    side = [(m>>u)&1 for u in range(n)]
    c = sum(1 for u,v in edges if side[u]!=side[v])
    best = max(best, c)
beta = len(edges) - best
# the claimed bipartition {0,1,2,3}|{4,5,6,7}
sideA = [0,0,0,0,1,1,1,1]
cutA = sum(1 for u,v in edges if sideA[u]!=sideA[v])
badA = [(u,v) for u,v in edges if sideA[u]==sideA[v]]
print(f"(2) e={len(edges)}  maxcut={best} (GPT says 8: {best==8})  beta={beta} (GPT says 2: {beta==2})")
print(f"    bipartition {{0,1,2,3}}|{{4,5,6,7}} cut={cutA} is-max={cutA==best}; bad edges={sorted(badA)} (GPT {{47,57}}: {sorted(badA)==[(4,7),(5,7)]})")

# (3) ell via B-distance (restricted to cut edges), Gamma
def bdist(s, t, side):
    from collections import deque
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d:
                d[v]=d[u]+1; q.append(v)
    return d.get(t,-1)
ell = {f: bdist(f[0], f[1], sideA)+1 for f in badA}
Gamma = sum(l*l for l in ell.values())
print(f"(3) ell={ell} (GPT 5,5: {set(ell.values())=={5}}); Gamma={Gamma} (GPT 50: {Gamma==50}); N^2-Gamma={n*n-Gamma} (GPT 14: {n*n-Gamma==14})")

# (4) shortest 5-cycles per bad edge = geodesic + the bad edge
print("(4) shortest geodesic-cycles per bad edge (geodesic in B, then close with the bad edge):")
all_cycles = []
for f in badA:
    for P in geos(adj, sideA, f[0], f[1]):
        cyc = P + [f[0]]
        all_cycles.append((f, cyc))
        print(f"    bad {f}: cycle {'-'.join(map(str,cyc))}  (len {len(P)} = ell {ell[f]}: {len(P)==ell[f]})")
gpt_cycles = {(4,0,6,2,7),(4,0,6,3,7),(5,1,6,2,7),(5,1,6,3,7)}
got_cycles = set(tuple(c[:-1]) for _,c in all_cycles)
print(f"    four cycles match GPT: {got_cycles==gpt_cycles}")

# (5) shared suffix 6-2-7 between geodesics 4-0-6-2-7 and 5-1-6-2-7 (segment-disjointness FAILS)
def geo_between(s,t):
    return [P for P in geos(adj, sideA, s, t)]
g47 = geos(adj, sideA, 4, 7)   # geodesics 4->7
g57 = geos(adj, sideA, 5, 7)   # geodesics 5->7
has_4_0_6_2_7 = [4,0,6,2,7] in g47
has_5_1_6_2_7 = [5,1,6,2,7] in g57
shared_suffix = [6,2,7]
suf_ok = has_4_0_6_2_7 and has_5_1_6_2_7
print(f"(5) geodesic 4-0-6-2-7 exists: {has_4_0_6_2_7}; 5-1-6-2-7 exists: {has_5_1_6_2_7}; "
      f"shared suffix {shared_suffix} => segment-disjointness FAILS (GPT's multiplicity obstruction): {suf_ok}")

# Peel C = 4-0-6-2-7, h=5, N-h=3; other incident bad edge 57 ell 5; A(C)=5, 2(N-h)=6 => A-ST vacuous
C = [4,0,6,2,7]; h=len(C); Cset=set(C)
incident_other = [f for f in badA if (f[0] in Cset or f[1] in Cset) and f!=(4,7)]
A = sum(ell[f] for f in incident_other)
print(f"(6) peel C={C} h={h} N-h={n-h}; other incident bad={incident_other} A(C)={A} 2(N-h)={2*(n-h)} "
      f"=> A-2(N-h)={A-2*(n-h)} (GPT -1, A-ST vacuous: {A-2*(n-h)==-1})")
print("=== DONE ===")
