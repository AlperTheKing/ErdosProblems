"""Codex block 25: RESTRICT-MAXCUT. For a bad-carrying Q-only K-component C (C disjoint from O, O nonempty),
is the inherited side assignment restricted to C a MAXIMUM cut of G[C]? If yes => induction gives Gamma_C<=|C|^2
=> boundary-deficit => cond(1). Look for a COUNTEREXAMPLE (inherited internal cut < MaxCut(G[C])) on adversarial
island gluings (filtered components are vacuous on real census). Exact integer cut counts."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_construct import build_K_T, Kcomponents, Cn, union_disjoint, mycielski, is_triangle_free

def induced_edges(info, Cs):
    adj=info['adj']; E=[]
    Cl=sorted(Cs)
    for i,u in enumerate(Cl):
        for v in Cl[i+1:]:
            if v in adj[u]: E.append((u,v))
    return E

def maxcut_induced(C, edges):
    # brute force max cut of subgraph on vertex set C with given edges
    Cl=sorted(C); idx={v:i for i,v in enumerate(Cl)}; k=len(Cl)
    best=0
    # fix vertex 0 on side 0 to halve
    for mask in range(1<<(k-1)):
        side=[0]*k
        for b in range(k-1):
            if mask>>b & 1: side[b+1]=1
        cut=sum(1 for (u,v) in edges if side[idx[u]]!=side[idx[v]])
        if cut>best: best=cut
    return best

def inherited_cut(info, Cs, edges):
    side=info['side']
    return sum(1 for (u,v) in edges if side[u]!=side[v])

def filtered_components(info):
    K,T,M,ell,n=build_K_T(info); N=n
    O=set(v for v in range(n) if T[v]>N)
    if not O: return [],N,None
    out=[]
    for C in Kcomponents(K,n):
        Cs=set(C)
        if Cs & O: continue
        badC=[f for f in M if f[0] in Cs and f[1] in Cs]
        if not badC: continue
        out.append((C,Cs,T))
    return out,N,T

def test_graph(name, info):
    if info is None: print(f"  {name}: loads=None"); return []
    comps,N,T=filtered_components(info)
    findings=[]
    for (C,Cs,Tv) in comps:
        if len(C)>20:
            print(f"  {name}: filtered comp |C|={len(C)} too big for brute MaxCut, skip"); continue
        E=induced_edges(info,Cs)
        ic=inherited_cut(info,Cs,E); mc=maxcut_induced(C,E)
        crit=all(Tv[v]==N for v in C)
        gap=mc-ic
        findings.append((name,tuple(C),ic,mc,gap,crit))
        tag=" *** RESTRICT-MAXCUT COUNTEREXAMPLE" if gap>0 else ""
        print(f"  {name}: filtered comp |C|={len(C)} inherited-cut={ic} MaxCut(G[C])={mc} gap={gap} critical={crit}{tag}",flush=True)
    if not comps:
        # report whether O exists at all
        K,T2,M,ell,n=build_K_T(info); N2=n
        hasO=any(t>N2 for t in T2)
        print(f"  {name}: no filtered (bad-carrying Q-only, O!=empty) component (O present={hasO})",flush=True)
    return findings

def glue(islandN, islandE, gadgetN, gadgetE, bridges):
    n,E=union_disjoint((islandN,islandE),(gadgetN,gadgetE))
    # bridges: list of (i_in_island, j_in_gadget) -> (i, islandN+j)
    for (i,j) in bridges:
        E=E+[(i, islandN+j)]
    return n,E

if __name__=="__main__":
    print("=== RESTRICT-MAXCUT counterexample search (island gluings) ===")
    C5=(5,Cn(5)); C7=(7,Cn(7))
    g15n,g15E=mycielski(7,Cn(7))     # Myc(C7) N=15 gadget (has O)
    grn,grE=mycielski(5,Cn(5))       # Grotzsch N=11
    # battery of island + gadget + bridge combos
    cases=[]
    # C5 island to Myc(C7), various single/double bridges
    for br in [[(0,0)],[(0,7)],[(0,0),(2,3)],[(0,0),(1,7)],[(0,2),(2,9)]]:
        n,E=glue(5,Cn(5),g15n,g15E,br)
        if is_triangle_free(n,E): cases.append((f"C5+MycC7 br{br}",n,E))
    # C7 island to Myc(C7)
    for br in [[(0,0)],[(0,0),(3,7)]]:
        n,E=glue(7,Cn(7),g15n,g15E,br)
        if is_triangle_free(n,E): cases.append((f"C7+MycC7 br{br}",n,E))
    # C5 island to Grotzsch
    for br in [[(0,0)],[(0,5)],[(0,0),(2,6)]]:
        n,E=glue(5,Cn(5),grn,grE,br)
        if is_triangle_free(n,E): cases.append((f"C5+Grotzsch br{br}",n,E))
    # two C5 islands + gadget
    n2,E2=union_disjoint((5,Cn(5)),(5,Cn(5,0)))
    allfind=[]
    for name,n,E in cases:
        allfind += test_graph(name, loads(n,E))
    # census vacuity check N<=10
    print("--- census filtered-component count (should be 0) ---")
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        cnt=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            comps,N,T=filtered_components(info)
            cnt+=len(comps)
        print(f"  census N={nn}: filtered components={cnt}",flush=True)
    ce=[f for f in allfind if f[4]>0]
    print(f"\nRESULT: {len(allfind)} filtered components tested on constructions; RESTRICT-MAXCUT counterexamples={len(ce)}")
    for f in ce: print("   CE:",f)
