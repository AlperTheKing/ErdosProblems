"""Deliberately construct a 2-gadget triangle-free graph: an overloaded C5-blowup gadget + a separate
odd-cycle gadget, joined by linker edges, to try to realize a Q-only bad-edge K-component (would refute
NO-Q-ONLY). We try several linker patterns and odd cycles, all triangle-free, and report the K-component
structure (does the second gadget's bad edges form a Q-only component?)."""
from fractions import Fraction as F
from _h import loads
from _cond1_proof import build_K
from _schur_spec import pf_exact
from _K_qonly import kgraph_components

def c5blow(t, base=0):
    """C5 blow-up with parts of size t, vertices base..base+5t-1."""
    E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):
                E.append((base+i*t+a, base+((i+1)%5)*t+b))
    return E, 5*t

def cycle(k, base=0):
    E=[(base+i, base+(i+1)%k) for i in range(k)]
    return E, k

def analyze(E,n,label):
    info=loads(n,E)
    if info is None:
        print(f"  {label}: no valid config (loads=None)"); return
    K,T,O,Q,N,_=build_K(info)
    if not O:
        print(f"  {label}: N={N} no overload (O empty)"); return
    P,M,ell,_=pf_exact(info)
    Oset=set(O)
    comp,nc=kgraph_components(K,n)
    qonly=[]
    for c in range(nc):
        nodes=[v for v in range(n) if comp[v]==c]; ns=set(nodes)
        if len(nodes)<2: continue
        hasO=any(v in Oset for v in nodes)
        meets=any(set(P[fi].keys()) & ns for fi in range(len(M)))
        if meets and not hasO:
            qonly.append((nodes,all(T[v]==F(N) for v in nodes)))
    print(f"  {label}: N={N} |O|={len(O)} Kcomps={nc} Q-only-badedge-comps={qonly}  T-range=[{float(min(T))},{float(max(T))}]")

if __name__=="__main__":
    print("=== 2-gadget constructions hunting a Q-only bad-edge K-component ===")
    # gadget A: C5 blow-up t=2 (overloaded), vertices 0..9
    EA,nA=c5blow(2,0)
    # gadget B: C7, vertices 10..16
    for kb in (5,7,9):
        EB,nB=cycle(kb,nA)
        n=nA+nB
        # try linkers: connect a vertex of A to a vertex of B (must keep triangle-free + bipartite-ish)
        for la in (0,2,4):
            for lb in (nA,nA+1,nA+2):
                E=EA+EB+[(la,lb)]
                analyze(E,n,f"C5b2 + C{kb} link({la}-{lb})")
        # also try a longer linker path of length 2
        # add intermediate vertex
    # also: two separate C5-blowups of different sizes
    EA,nA=c5blow(2,0)
    EB,nB=c5blow(1,nA)  # plain C5
    E=EA+EB+[(0,nA)]
    analyze(E,nA+nB,"C5b2 + C5 link(0-10)")
