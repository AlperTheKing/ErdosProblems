"""CLASSIFY every K-component C disjoint from O over the census. Claim to verify EXACTLY:
every such C is exactly one of
  (FULL)  C = V  (requires O empty),  deficit = N|V|-Gamma = N^2-Gamma >= 0, dB = 0 (no boundary).
  (ISO0)  a T=0 isolated vertex (singleton with T(v)=0),  deficit = N, dB = deg_B(v) <= N-1 < N.
i.e. there is NO PROPER component with any load (T>0) disjoint from O.
Also: for ISO0 singletons, confirm dB = deg_B(v) and deg_B(v) < N (so deficit=N > dB). And confirm
when O is empty the only Q-only comp is the whole graph (K connected on load-bearing vertices).
Report counts of each class and any component that is NEITHER (the would-be 'critical' obstruction)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def classify(info):
    B=build(info)
    K=B['K']; T=B['T']; N=B['N']; n=B['n']; O=B['O']; Bset=B['Bset']
    comps=components(K,n)
    classes={'FULL':0,'ISO0':0,'OTHER':0}
    others=[]
    for C in comps:
        Cs=set(C)
        if Cs&O: continue
        d=analyze_one(B,C)
        if len(C)==n:
            classes['FULL']+=1
            # sanity: O empty
            assert not O, f"FULL comp but O nonempty {info}"
            continue
        if len(C)==1 and T[C[0]]==0:
            classes['ISO0']+=1
            v=C[0]
            degB=sum(1 for (a,b) in Bset if a==v or b==v)
            # dB for singleton = degB
            assert d['dB']==degB
            assert degB<N
            continue
        classes['OTHER']+=1
        degs={v:sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs)) for v in C}
        others.append((tuple(C),float(d['deficit']),d['dB'],d['nFC'],[float(T[v]) for v in C]))
    return classes,others

if __name__=="__main__":
    print("=== classify K-components disjoint from O (FULL / ISO0 / OTHER) ===")
    tot={'FULL':0,'ISO0':0,'OTHER':0}; all_others=[]
    for nn in range(5,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        cc={'FULL':0,'ISO0':0,'OTHER':0}
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            classes,others=classify(info)
            for k in cc: cc[k]+=classes[k]
            for o in others: all_others.append((g6,)+o)
        for k in tot: tot[k]+=cc[k]
        print(f"  N={nn}: FULL={cc['FULL']} ISO0={cc['ISO0']} OTHER={cc['OTHER']}",flush=True)
    print(f"TOTAL: FULL={tot['FULL']} ISO0={tot['ISO0']} OTHER(proper-loaded Q-only)={tot['OTHER']}")
    if all_others:
        print("OTHER examples (PROPER LOADED Q-only comps - the would-be obstruction):")
        for o in all_others[:20]: print("  ",o)
