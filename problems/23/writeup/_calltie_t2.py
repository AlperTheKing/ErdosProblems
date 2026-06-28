"""Investigate the apparent CLAIM-A failures = sat-with-deadnb in Q-only comps.
Are these genuine C-alltie violations, or does O empty / cut-choice explain it?
Dump full structure for I??CABoNo under loads() cut."""
from fractions import Fraction as F
from _h import dec, loads
from _bdef_theory import build, components

def crossdeg(v, Cs, Bset):
    c=0
    for (a,b) in Bset:
        if a==v and b not in Cs: c+=1
        elif b==v and a not in Cs: c+=1
    return c

for g6 in ["I??CABoNo"]:
    n,E=dec(g6); info=loads(n,E)
    B=build(info); K=B['K']; T=B['T']; N=B['N']; O=B['O']; Bset=B['Bset']; side=info['side']
    print(f"{g6}: N={N} O={sorted(O)} side={side}")
    comps=components(K,n)
    for C in comps:
        Cs=set(C)
        if Cs&O: tag="(meets O)"
        else: tag="(Q-only)"
        load=sum(T[v] for v in C)
        print(f"  comp {sorted(C)} {tag} Gamma_C={float(load)} deficit={float(N*len(C)-load)}")
        for v in C:
            cd=crossdeg(v,Cs,Bset)
            deadnb=[w for w in range(n) if (min(v,w),max(v,w)) in Bset and T[w]==0]
            mark=""
            if T[v]==N: mark+=" SAT"
            if T[v]==0: mark+=" DEAD"
            if T[v]==N and deadnb: mark+=f" SAT-DEADNB(z={deadnb})"
            print(f"    v={v} T={float(T[v])} crossdeg={cd} N-T-cd={float(N-T[v]-cd)} side={side[v]}{mark}")
