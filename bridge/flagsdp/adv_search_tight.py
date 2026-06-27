#!/usr/bin/env python3
"""Search for ANY tight (Gamma=N^2) connected-B max-cut triangle-free instance with m>=2 and NO safe peel.
Strategy: since the only tight families are C5[q] and odd cycles, probe:
 (A) C5[q] with extra/removed bad edges within parts' neighborhoods (still triangle-free),
 (B) two C5[q] blobs sharing a common part (necklace of blow-ups),
 (C) random triangle-free graphs near the C5[q] density that happen to be tight.
Report only harness-verified tight + m>=2 + no-peel obstructions; also near-tight (>=0.97) no-peel.
"""
import sys, random, itertools
sys.path.insert(0,'/e/Projects/ErdosProblems/bridge/flagsdp')
from peel_check import check_instance

def scan(name, n, adj, near=0.97):
    if n>26: return None
    r=check_instance(n,adj)
    if not (r.get("ok") and r.get("triangle_free") and r.get("B_connected")): return r
    g=r.get("gamma"); n2=r.get("n2")
    if g is None: return r
    ratio=g/n2
    obstruction = r.get("ge_n2") and r.get("m",0)>=2 and r.get("has_safe_peel") is False
    if obstruction:
        print(f"*** OBSTRUCTION {name}: N={n} m={r['m']} gamma={g} n2={n2} ratio={ratio:.4f} | {r['detail']}")
    elif r.get("m",0)>=2 and ratio>=near and r.get("has_safe_peel") is False:
        print(f"!!! NEAR-TIGHT NO-PEEL {name}: N={n} m={r['m']} gamma={g} n2={n2} ratio={ratio:.4f}")
    elif r.get("tight"):
        print(f"    tight-ok {name}: N={n} m={r['m']} ratio={ratio:.4f} sp={r['has_safe_peel']}")
    return r

# C5[q] builder with explicit parts
def C5q_parts(q):
    n=5*q; parts=[list(range(i*q,(i+1)*q)) for i in range(5)]
    adj=[set() for _ in range(n)]
    for i in range(5):
        for a in parts[i]:
            for b in parts[(i+1)%5]:
                adj[a].add(b); adj[b].add(a)
    return n,adj,parts

# (B) two C5[q] sharing a single common PART (so it's a "figure-eight" of blow-ups)
def two_C5q_shared_part(q):
    """First C5[q] on parts P0..P4. Second C5[q] reuses P0 (=its part Q0) and adds Q1..Q4 fresh.
    Triangle-free? P0 adj P1,P4 (first) and adj Q1,Q4 (second). Need no triangle: P1-?-Q1 etc no edge -> ok."""
    P=[list(range(i*q,(i+1)*q)) for i in range(5)]
    nxt=5*q
    Q=[P[0]]+[list(range(nxt+j*q,nxt+(j+1)*q)) for j in range(4)]
    n=nxt+4*q
    adj=[set() for _ in range(n)]
    def link(A,B):
        for a in A:
            for b in B: adj[a].add(b); adj[b].add(a)
    for i in range(5): link(P[i],P[(i+1)%5])
    for i in range(5): link(Q[i],Q[(i+1)%5])
    return n,adj

# (D) C5[q] with one part split: take C5[2] and add an extra vertex into a part -> unbalanced, retest
# Already covered by unbalanced blow-ups; here do exhaustive over all 5-part size multisets summing small.
def C5_unbalanced(mult):
    n=sum(mult); parts=[]; s=0
    for m in mult: parts.append(list(range(s,s+m))); s+=m
    adj=[set() for _ in range(n)]
    for i in range(5):
        for a in parts[i]:
            for b in parts[(i+1)%5]: adj[a].add(b); adj[b].add(a)
    return n,adj

# (C) random triangle-free graphs, keep only tight ones
def rand_tf(n, p, rng):
    adj=[set() for _ in range(n)]
    edges=[(u,v) for u in range(n) for v in range(u+1,n)]
    rng.shuffle(edges)
    for (u,v) in edges:
        if rng.random()<p and not (adj[u]&adj[v]):
            adj[u].add(v); adj[v].add(u)
    return adj

if __name__=="__main__":
    print("=== (B) figure-eight: two C5[q] sharing one part ===")
    for q in (1,2):
        n,adj=two_C5q_shared_part(q); scan(f"fig8_C5q_q{q}", n, adj)

    print("=== (D) exhaustive small unbalanced C5 part-sizes (sum<=26), look for tight/near-tight no-peel ===")
    cnt=0
    for mult in itertools.product(range(1,6),repeat=5):
        if sum(mult)>26: continue
        if max(mult)-min(mult)>2: continue   # near-balanced only (tight zone)
        cnt+=1
        n,adj=C5_unbalanced(list(mult)); scan(f"C5{mult}", n, adj, near=0.95)
    print(f"  checked {cnt} unbalanced C5 part-size multisets")

    print("=== (C) random triangle-free near C5-density, keep tight ===")
    rng=random.Random(12345)
    ntight=0; ntested=0
    for trial in range(4000):
        n=rng.choice([10,15,20])
        p=rng.uniform(0.30,0.55)
        adj=rand_tf(n,p,rng)
        ntested+=1
        r=scan(f"rand_{trial}", n, adj, near=0.98)
        if r and r.get("tight"): ntight+=1
    print(f"  random: tested {ntested}, tight found {ntight}")
    print("DONE")
