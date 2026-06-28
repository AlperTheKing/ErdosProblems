"""Adversarial search for a PROPER LOADED Q-only K-component with O NONEMPTY (the cond(1) obstruction),
and for any boundary-deficit VIOLATION (deficit < dB). If found with deficit small + dB>=1, that is the
genuine critical/near-critical obstruction. Constructions:
  - C5-blowup (extremal, T==N) joined to a C7 or odd cycle by identifying/bridging vertices
  - Mycielskians of odd cycles and small graphs
  - random connected triangle-free graphs with mixed degree (some long geodesics -> overload)
Exact Fraction. Report any O-nonempty OTHER comp and the min deficit-dB among them."""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def analyze_graph(name,nn,EE,report=True):
    """returns list of OTHER comps with O nonempty: (C, deficit, dB, bd_ok, O)"""
    info=loads(nn,EE)
    if info is None:
        return None
    B=build(info); K=B['K']; T=B['T']; N=B['N']; O=B['O']; n=B['n']
    comps=components(K,n)
    others=[]
    for C in comps:
        Cs=set(C)
        if Cs&O: continue
        if len(C)==n: continue
        if len(C)==1 and T[C[0]]==0: continue
        d=analyze_one(B,C)
        others.append((tuple(C),float(d['deficit']),d['dB'],d['bd_ok'],sorted(O),len(O)>0))
    return dict(N=N,O=sorted(O),nO=len(O),others=others)

def rand_trifree(n,p,seed):
    random.seed(seed)
    # build triangle-free by rejection
    adj=[set() for _ in range(n)]; E=[]
    order=[(i,j) for i in range(n) for j in range(i+1,n)]
    random.shuffle(order)
    for i,j in order:
        if random.random()>p: continue
        # adding i-j: triangle iff common neighbor
        if adj[i]&adj[j]: continue
        adj[i].add(j); adj[j].add(i); E.append((i,j))
    return n,E

if __name__=="__main__":
    found_Ononempty=[]
    minslack=None
    # iterated Mycielskians
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    cur=C5; chain=[("C5",C5)]
    for k in range(2):
        nn,EE=mycielski(*cur); cur=(nn,EE); chain.append((f"Myc^{k+1}(C5) N={nn}",cur))
    C7=(7,[(i,(i+1)%7) for i in range(7)])
    cur=C7
    for k in range(1):
        nn,EE=mycielski(*cur); cur=(nn,EE); chain.append((f"Myc^{k+1}(C7) N={nn}",cur))
    for name,(nn,EE) in chain:
        if nn>24: continue
        r=analyze_graph(name,nn,EE)
        if r is None: print(f"  {name}: loads=None"); continue
        oc=[o for o in r['others'] if o[5]]
        print(f"  {name} (N={r['N']}, O={r['O']}): OTHER={len(r['others'])} O-nonempty-OTHER={len(oc)}")
        for o in oc:
            print(f"     *** O-NONEMPTY OTHER: C={o[0]} deficit={o[1]} dB={o[2]} bd_ok={o[3]}")
            found_Ononempty.append((name,o))
    # random triangle-free, varied density and size
    print("--- random triangle-free scan (looking for O-nonempty proper-loaded Q-only comp) ---")
    cnt=0; nfound=0
    for seed in range(3000):
        n=random.Random(seed).randint(8,16)
        p=random.Random(seed*7+1).uniform(0.25,0.6)
        nn,EE=rand_trifree(n,p,seed)
        r=analyze_graph(f"rand{seed}",nn,EE,report=False)
        if r is None: continue
        cnt+=1
        oc=[o for o in r['others'] if o[5]]
        for o in oc:
            nfound+=1
            slack=o[1]-o[2]
            if minslack is None or slack<minslack: minslack=slack
            if nfound<=20:
                print(f"   rand{seed} N={r['N']} O={r['O']}: O-NONEMPTY OTHER C={o[0]} deficit={o[1]} dB={o[2]} bd_ok={o[3]}")
    print(f"random: graphs-with-cut={cnt} O-nonempty-OTHER-comps-found={nfound} min(deficit-dB)among-them={minslack}")
    print(f"TOTAL O-nonempty OTHER from structured: {len(found_Ononempty)}")
