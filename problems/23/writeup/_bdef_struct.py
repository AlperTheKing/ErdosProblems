"""Structural probe: for each K-component C disjoint from O, examine
deficit(C) = sum_{v in C}(N-T(v)) >= dB(C). Look for a per-B-edge charge.
Candidate LOCAL charge: each crossing B-edge {x,y}, x in C, charges its unit to x's slack.
Test whether per-vertex slack(v)=N-T(v) >= (#crossing B-edges at v)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def probe(info):
    B=build(info)
    K=B['K']; T=B['T']; N=B['N']; n=B['n']; Bset=B['Bset']; O=B['O']
    comps=components(K,n)
    rows=[]
    for C in comps:
        Cs=set(C)
        if Cs&O: continue
        d=analyze_one(B,C)
        if d['sz']==1 and T[C[0]]==0: continue
        cross=[(a,b) for (a,b) in Bset if (a in Cs)^(b in Cs)]
        deg_cross={v:0 for v in C}
        for (a,b) in cross:
            x=a if a in Cs else b
            deg_cross[x]+=1
        slack={v:F(N)-T[v] for v in C}
        local_ok=all(slack[v]>=deg_cross[v] for v in C)
        rows.append(dict(C=C,sz=d['sz'],deficit=float(d['deficit']),dB=d['dB'],
                         local_ok=local_ok,
                         slacks={v:float(slack[v]) for v in C},
                         degc={v:deg_cross[v] for v in C}))
    return rows

if __name__=="__main__":
    names=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?","J?AEB?oE?W?"]
    for g6 in names:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        for r in probe(info):
            print(f"{g6} C(sz{r['sz']}): deficit={r['deficit']} dB={r['dB']} LOCAL_per_vertex_ok={r['local_ok']}")
            if not r['local_ok']:
                print(f"    slacks={r['slacks']}")
                print(f"    crossdeg={r['degc']}")
    print("--- census: does per-vertex slack>=crossdeg always hold? ---")
    for nn in range(5,10):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nloc_fail=0; ncomp=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in probe(info):
                ncomp+=1
                if not r['local_ok']: nloc_fail+=1
        print(f"  N={nn}: comps(nontriv)={ncomp} LOCAL_per_vertex_charge_FAILS={nloc_fail}")
