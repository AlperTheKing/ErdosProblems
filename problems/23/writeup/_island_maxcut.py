"""KEY TEST for the induction: is the restricted cut on a K-closed K-component C a MAXIMUM cut of G[C]?
If yes, then by IH Gamma(G[C]) <= |C|^2 with the restricted cut; and Gamma_C = Gamma of that cut.
A critical component has Gamma_C = N|C| > |C|^2 (since N>|C|), contradiction => no critical Q-only comp.

We test: for every K-closed K-component C disjoint from O (and for ALL components), compare
  cut_restricted(C) = #cut edges of G[C] under global side
  maxcut(G[C]) = true max cut of induced subgraph
Report whether restricted == max. Census N<=11 (loads-cut) + bridge + blow-ups.
Crucially: does it hold for components carrying bad edges? for would-be-critical (all T=N) comps?
"""
from fractions import Fraction as F
from itertools import product
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact
from _bdef_construct import Kcomponents, build_K_T, mycielski, union_disjoint, add_edges, Cn, blow_g

def induced_maxcut(C, adj):
    C=list(C); idx={v:i for i,v in enumerate(C)}; m=len(C)
    iedges=[(idx[u],idx[v]) for u in C for v in adj[u] if v in idx and v>u]
    best=0
    for bits in range(1<<m):
        s=[(bits>>i)&1 for i in range(m)]
        c=sum(1 for u,v in iedges if s[u]!=s[v])
        if c>best: best=c
    return best, iedges

def restricted_cut(C, adj, side):
    Cs=set(C)
    return sum(1 for u in C for v in adj[u] if v in Cs and v>u and side[u]!=side[v])

def test_graph(name, n, E):
    info=loads(n,E)
    if info is None: return
    adj=info['adj']; side=info['side']
    K,T,M,ell,nn=build_K_T(info); N=nn
    O=set(v for v in range(nn) if T[v]>N)
    comps=Kcomponents(K,nn)
    for C in comps:
        if len(C)>16: continue
        Cs=set(C)
        carries_bad=any(f[0] in Cs and f[1] in Cs for f in M)
        if not carries_bad: continue
        mc,_=induced_maxcut(C,adj)
        rc=restricted_cut(C,adj,side)
        crit=all(T[v]==N for v in C)
        meetsO=bool(Cs&O)
        if rc!=mc or crit:
            print(f"  [{name}] |C|={len(C)} restrictedcut={rc} inducedMAXcut={mc} "
                  f"RESTRICTED-IS-MAX={rc==mc} critical={crit} meetsO={meetsO}")
    return

if __name__=="__main__":
    print("=== Is restricted cut on K-closed bad-carrying component a MAX cut of G[C]? ===")
    print("(only printing components where restricted != max, OR critical)")
    # bridge
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
    n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),[(0,5)])
    test_graph("bridge",n,E)
    # blow-ups
    for t in [2,3]:
        nn,EE=blow_g(5,Cn(5),t); test_graph(f"C5[{t}]",nn,EE)
    # census
    print("--- census loads-cut N=7..10: violations of restricted-is-max on bad-carrying comps ---")
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        viol=0; crit=0; tot=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            adj=info['adj']; side=info['side']
            K,T,M,ell,N=build_K_T(info)
            O=set(v for v in range(N) if T[v]>N)
            for C in Kcomponents(K,N):
                Cs=set(C)
                if not any(f[0] in Cs and f[1] in Cs for f in M): continue
                tot+=1
                mc,_=induced_maxcut(C,adj); rc=restricted_cut(C,adj,side)
                if rc!=mc: viol+=1
                if all(T[v]==N for v in C): crit+=1
        print(f"  N={nn}: bad-carrying comps={tot} restricted!=max={viol} critical(T=N on C)={crit}",flush=True)
