"""Hard attack: realize O nonempty (one component overloaded) WHILE a SEPARATE loaded
K-component carries a saturated vertex (T=N) with a dead B-neighbor.

Idea: To keep O alive after adding the second gadget, the O must survive the larger N.
T(v)>N requires N < intrinsic load. The most overload-robust gadget is a DENSE one with
high Gamma_C/|C|. Use blowups C5[t] which have T==N_local uniformly -- on the nose. To get
strict overload we need an irregular dense gadget.

We take the standalone overloaded gadget G1 and try to add the SMALLEST possible second
loaded component so N grows the least. Smallest odd-cycle loaded comp = C5 (adds 5, all T=1<N).
But a lone C5 attached cannot have a SATURATED vertex (T=1). To get T=N in the 2nd comp we'd
need its intrinsic load to reach the global N -- which is large. So saturation in a SMALL
separate comp is structurally hard: T(v) in comp C is bounded by Gamma_C <= (internal mass),
and to reach N the comp must itself be large/dense -> raises N -> kills O.

This is the crux. Quantify it:
  In a Q-only comp C, max_v T(v) <= Gamma_C - (rest) ... actually T(v) <= Gamma_C. For T(v)=N
  we need Gamma_C >= N. But Gamma_C <= N|C| (deficit>=0) is automatic; the binding direction:
  to have a SATURATED v we need Gamma_C >= N. And the O lives in C' with Gamma_{C'} stuff.
  Total Gamma = sum Gamma_C <= N^2 (the very thing). And N = |C|+|C'|+(rest).

Test the SHARP inequality:  in a Q-only loaded comp C, does T(v)=N force |C| to be large
relative to the O-comp, exceeding the budget?

Concretely scan: for every pair (G1 overloaded, G2 with a high-load vertex) glued, does O survive
AND a separate saturated vertex appear? Brute force many glue topologies.
"""
from fractions import Fraction as F
import subprocess, itertools
from _h import dec, GENG, loads
from _calltie_glue import components_from_info

def check(name,n,E,verbose=False):
    info=loads(n,E)
    if info is None: return None
    T=info['T']; N=info['n']; adj=info['adj']; side=info['side']
    O=set(v for v in range(N) if T[v]>N)
    if not O: return ('noO',None)
    comps=components_from_info(info)
    Ocomp=None
    for Cc in comps:
        if Cc & O: Ocomp=Cc; break
    # look for a saturated vertex in a DIFFERENT comp, with a dead B-neighbor
    hits=[]
    for Cc in comps:
        if Cc & O: continue
        for v in Cc:
            if T[v]==N:
                deadnb=[w for w in adj[v] if side[w]!=side[v] and T[w]==0]
                if deadnb:
                    hits.append((v,sorted(Cc),deadnb))
    if hits:
        print(f"*** C-ALLTIE VIOLATION {name}: O={sorted(O)} separate-sat-dead={hits}")
        return ('VIOL',hits)
    return ('ok',None)

if __name__=="__main__":
    print("=== Hard attack on C-alltie: separate saturated+dead vertex while O nonempty ===")
    # Overloaded gadgets to seed O:
    seeds=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?","I??CABoNo","I??CF@wFo"]
    # second gadgets to attach (carry potential saturated vertices)
    second=["G?bF`w","I?BD@g]Qo","I??CABoNo","I??CF@wFo"]
    nviol=0; nok=0; nnoO=0
    for s1 in seeds:
        n1,E1=dec(s1)
        for s2 in second:
            n2g,E2g=dec(s2)
            base=n1
            E2=[(base+a,base+b) for (a,b) in E2g]
            # try several even bridges between a vertex of G1 and a vertex of G2
            for (u1,u2) in itertools.product(range(min(n1,4)), range(min(n2g,4))):
                for blen in [2,4]:
                    E=list(E1)+list(E2)
                    prev=u1; nn=base+n2g
                    for _ in range(blen-1):
                        E.append((prev,nn)); prev=nn; nn+=1
                    E.append((prev, base+u2))
                    r=check(f"{s1}+{s2} br{blen} ({u1},{u2})", nn, E)
                    if r is None: continue
                    tag=r[0]
                    if tag=='VIOL': nviol+=1
                    elif tag=='noO': nnoO+=1
                    else: nok+=1
    print(f"Total: VIOLATIONS={nviol} ok(O-survived,no-sep-sat-dead)={nok} O-died={nnoO}")
