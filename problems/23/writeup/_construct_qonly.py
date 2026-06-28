"""Try to CONSTRUCT a Q-only bad-edge K-component (would show NO-Q-ONLY is not a general theorem,
leaving only the SATURATED version 'no critical component' as the real condition-(1) lemma).
Strategy: build triangle-free G as the disjoint-ish union of two odd-cycle gadgets sharing a connection
that does NOT create shared bad-edge geodesics. Use blow-ups + small linkers. Just scan many random
triangle-free connected graphs at N=12..15 looking for any Q-only bad-edge K-component."""
import random, subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _cond1_proof import build_K
from _schur_spec import pf_exact
from _K_qonly import kgraph_components

def randtrianglefree(n, p, seed):
    random.seed(seed)
    adj=[set() for _ in range(n)]
    edges=[(i,j) for i in range(n) for j in range(i+1,n)]
    random.shuffle(edges)
    E=[]
    for (i,j) in edges:
        if random.random()>p: continue
        # triangle-free check
        if adj[i] & adj[j]: continue
        adj[i].add(j); adj[j].add(i); E.append((i,j))
    # connectivity
    seen={0}; st=[0]
    while st:
        u=st.pop()
        for v in adj[u]:
            if v not in seen: seen.add(v); st.append(v)
    if len(seen)!=n: return None
    return E

def has_qonly(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return None
    P,M,ell,_=pf_exact(info)
    Oset=set(O)
    comp,nc=kgraph_components(K,n)
    for c in range(nc):
        nodes=[v for v in range(n) if comp[v]==c]; nodeset=set(nodes)
        if len(nodes)<2: continue
        has_O=any(v in Oset for v in nodes)
        meets=any(set(P[fi].keys()) & nodeset for fi in range(len(M)))
        if meets and not has_O:
            allsat=all(T[v]==F(N) for v in nodes)
            return (nodes,[float(T[v]) for v in nodes],allsat)
    return None

if __name__=="__main__":
    print("=== search for Q-only bad-edge K-component (random triangle-free N=12..16) ===")
    found=0; saturated_found=0
    for n in range(12,17):
        for seed in range(4000):
            E=randtrianglefree(n,0.32,seed)
            if E is None: continue
            info=loads(n,E)
            if info is None: continue
            r=has_qonly(info)
            if r:
                found+=1
                if r[2]: saturated_found+=1
                if found<=8:
                    print(f"  N={n} seed={seed}: Q-only bad-edge K-comp nodes={r[0]} T={r[1]} saturated={r[2]}")
        print(f"  ...through N={n}: Q-only-found={found} (saturated/critical={saturated_found})",flush=True)
    print(f"\n  TOTAL Q-only bad-edge K-components found={found}; of those SATURATED(critical)={saturated_found}")
