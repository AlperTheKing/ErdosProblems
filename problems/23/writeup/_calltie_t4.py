"""VERTEX-BUDGET route to C-alltie.
Contrapositive: O nonempty, v saturated (T(v)=N), v's K-comp C is Q-only (C cap O = empty),
and v has a dead B-neighbor z (T(z)=0).

Budget argument candidate:
  N = |V| >= |C| + |C'| + |Z|, where
    C' = a loaded K-component containing some o in O (exists since O nonempty); C' != C, |C'| >= 5.
    Z  = set of dead-net vertices not in C or C'. We KNOW z in Z so |Z| >= 1.
  Saturation: T(v) = N.

We want to find the exact intrinsic inequality relating maxT_C and the AVAILABLE outside-C vertices.
Measure precisely, over census, for every loaded K-comp C and the chosen vertex v with T(v)=maxT_C:
    excess(C) = maxT_C - |C|
    outside(C)= N - |C|   (vertices not in C)
and the relation excess(C) <= outside(C) is trivial (maxT_C<=N). The QUESTION: when O nonempty,
how big must 'outside' structure be?  We log, for the saturated-Q-only-dead config, whether it
EVER occurs and what the outside decomposition looks like.

Also test the sharper INTRINSIC quantity:
    g_C := number of vertices NOT in C that are needed to 'support' T(v)=N.
We instead directly test the candidate THEOREM:
   (BUDGET) If C is a loaded K-comp and v in C has T(v) >= |C| + 6, then ... [check what holds]
and more usefully measure: among ALL loaded K-comps over the census, the max of
    maxT_C - |C| - (N - |C| - 5*[#other loaded comps] - [#dead outside])
to see if there's slack."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _calltie_glue import components_from_info

def scan(Nmin,Nmax):
    # For each graph, identify loaded K-comps, O, dead net. For each Q-only loaded comp C with a
    # saturated vertex and a dead B-neighbor, check O empty. Also record max excess when O nonempty.
    worst_excess_Ononempty=F(-10**9); wit=None
    cnt_qonly_sat_dead_Ononempty=0
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            T=info['T']; N=info['n']; adj=info['adj']; side=info['side']; Bset=info['Bset']
            O=set(v for v in range(N) if T[v]>N)
            if not O: continue   # focus on O nonempty
            comps=components_from_info(info)
            loaded=[C for C in comps if sum(T[v] for v in C)>0]
            for C in loaded:
                if C & O: continue   # only Q-only
                Cs=set(C)
                for v in C:
                    if T[v]!=N: continue
                    dead=[w for w in adj[v] if side[w]!=side[v] and T[w]==0]
                    if not dead: continue
                    cnt_qonly_sat_dead_Ononempty+=1
                    if wit is None: wit=(g6,v,sorted(C),sorted(O),dead)
                # track excess even without dead nb
                mx=max(T[w] for w in C)
                ex=mx-len(C)
                if ex>worst_excess_Ononempty:
                    worst_excess_Ononempty=ex;
        print(f"  N={nn}: [O nonempty] Q-only-sat-dead count={cnt_qonly_sat_dead_Ononempty} worstExcess(Qonly,Ononempty)={float(worst_excess_Ononempty):+.2f}",flush=True)
    print(f"TOTAL [O nonempty, loads cut]: Q-only sat-with-dead = {cnt_qonly_sat_dead_Ononempty}  witness={wit}")
    print(f"   worst (maxT_C-|C|) over Q-only comps when O nonempty = {float(worst_excess_Ononempty):+.3f}")

if __name__=="__main__":
    print("=== VERTEX-BUDGET probe: Q-only sat-with-dead when O NONEMPTY (loads cut) ===")
    scan(5,11)
