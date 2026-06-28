"""Adversarial gluing: try to realize a Q-only LOADED K-component COEXISTING with O nonempty.
Strategy: take an overloaded gadget G1 (has O) and a separate odd-cycle gadget G2 (loaded, Q-only),
join them so the joint max cut is gamma-min and keeps both as separate K-components.

We need the JOINT graph to be triangle-free and the gamma-min max cut to (a) have O nonempty
(from G1) and (b) keep G2's bad edges as a separate K-component disjoint from O.

Key: K-components are determined by SHARED geodesic supports. Two gadgets sharing no bad-edge
geodesic vertex stay separate. So glue via a single cut edge / bridge path that carries no bad geodesic.

We enumerate joins and check via loads()."""
from fractions import Fraction as F
import itertools, subprocess
from _h import dec, GENG, loads, maxcut_all, Bconn, bdist_restr, gmin
from _zmu import mu_edges

def components_from_info(info):
    n=info['n']; cyc=info['cyc']
    par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for f,Ps in cyc.items():
        for P in Ps:
            for i in range(1,len(P)):
                ra,rb=find(P[0]),find(P[i])
                if ra!=rb: par[ra]=rb
    comp={}
    for v in range(n): comp.setdefault(find(v),set()).add(v)
    return list(comp.values())

def report(name, n, E):
    info=loads(n,E)
    if info is None:
        print(f"{name}: loads None (cut not B-connected or no bad edge)"); return
    T=info['T']; N=info['n']
    O=set(v for v in range(N) if T[v]>N)
    comps=components_from_info(info)
    loaded=[C for C in comps if sum(T[v] for v in C)>0]
    qonly_loaded=[C for C in loaded if not (C & O)]
    print(f"{name}: N={N} Gamma={info['G']} |O|={len(O)} loaded-comps={len(loaded)} Q-only-loaded={len(qonly_loaded)}")
    for C in qonly_loaded:
        gc=sum(T[v] for v in C); sat=[v for v in C if T[v]==N]
        print(f"    *** Q-only LOADED comp sz={len(C)} GammaC={gc} sat={sat} C={sorted(C)}  <<< COEXISTS WITH O")
    return info, O, loaded, qonly_loaded

def C(k):
    """odd cycle C_k as edge list."""
    return [(i,(i+1)%k) for i in range(k)]

if __name__=="__main__":
    print("=== Try to realize a Q-only LOADED K-component coexisting with O ===")
    # Gadget that produces O: I??CF@wFo has |O|? actually it had |O|=0. Use I?BD@g]Qo (|O|=3)
    # Build a disjoint union joined by a long even bridge so the cut stays connected.
    # G1 = I?BD@g]Qo (N=10, has O). G2 = C5 (loaded Q-only when standalone? a lone C5: all T=1).
    n1,E1=dec("I?BD@g]Qo")
    # relabel C5 to start at n1
    base=n1
    E2=[(base+i, base+(i+1)%5) for i in range(5)]
    n2=base+5
    # bridge: connect via even path so both pieces lie on one connected bipartite cut.
    # Add a path of length 2 (even => same side parity) from a G1 vertex to a G2 vertex
    # using one fresh midpoint.
    for bridge_len in [2,4]:
        E=list(E1)+list(E2)
        prev=0  # a G1 vertex
        nn=n2
        for _ in range(bridge_len-1):
            E.append((prev,nn)); prev=nn; nn+=1
        E.append((prev, base))  # attach to a G2 vertex
        report(f"glue I?BD@g]Qo + C5 bridge{bridge_len}", nn, E)
    # Also try two odd cycles of different lengths joined (C5 + C7) via even bridge
    for (a,b) in [(5,7),(5,9),(7,7),(5,5)]:
        E=C(a)
        E2=[(a+i, a+(i+1)%b) for i in range(b)]
        E=E+E2
        nn=a+b
        # even bridge length 2
        E.append((0,nn)); E.append((nn,a)); nn+=1
        report(f"C{a}+C{b} even-bridge", nn, E)
