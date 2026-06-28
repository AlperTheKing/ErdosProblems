"""Fast blow-up hunt for condition (1) load-bearing facts (skip expensive full inverse;
inverse>=0 follows from the classical M-matrix theorem once nonsingularity holds).
Per blow-up, EXACT-check:
  (R) rowsum(K_QQ)<=N for all q in Q
  (NC) no critical KQQ-component (=> nonsingular N*I-K_QQ; by per-component Perron rho<N)
  (SING) every O-isolated KQQ-component is a SINGLETON  (the clean structural lemma)
  per-component block det>0 (cheap-ish; det faster than inverse)
Targets N up to ~30. Reports any O-isolated component of size>=2 (would be the danger), and any
critical component, with the base graph + blow factor.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K, det_frac, reach_components

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

def check(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return None
    m=len(Q)
    KQQ=[[K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    leak=[sum(K[Q[i]][o] for o in O) for i in range(m)]
    r=[F(N)-T[Q[i]] for i in range(m)]
    comp,ncomp=reach_components(KQQ)
    rowsum_ok=all(sum(KQQ[i][j] for j in range(m))<=F(N) for i in range(m))
    critical=0; max_iso=0; blockdet_pos=True; min_blockdet_margin=None
    for c in range(ncomp):
        nodes=[i for i in range(m) if comp[i]==c]
        iso=all(leak[i]==0 for i in nodes)
        if iso: max_iso=max(max_iso,len(nodes))
        if all(r[i]==0 and leak[i]==0 for i in nodes): critical+=1
        block=[[ (F(N) if i==j else F(0)) - KQQ[nodes[i]][nodes[j]] for j in range(len(nodes))] for i in range(len(nodes))]
        bd=det_frac(block)
        if bd<=0: blockdet_pos=False
    ok = rowsum_ok and critical==0 and blockdet_pos and max_iso<=1
    return dict(N=N,m=m,nO=len(O),ncomp=ncomp,rowsum_ok=rowsum_ok,critical=critical,
                max_iso=max_iso,blockdet_pos=blockdet_pos,ok=ok)

def census_bases(nn, limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    return out if limit is None else out[:limit]

if __name__=="__main__":
    print("=== Condition (1) FAST blow-up hunt: O-iso singletons + no critical + rowsum<=N ===")
    # gather a diverse set of base graphs (those known to produce O after blow-up)
    bases=set(["G?bF`w","H?AAF_}","I?BD@g]Qo","I?ABCc]}?","J???E?pNu\\?","J?`@C_W{Ck?",
               "J?AE@`KkH{?","J??CE@a}?z?"])
    # add many N=9,10 bases
    for nn in (9,10):
        for g6 in census_bases(nn):
            bases.add(g6)
    bases=sorted(bases)
    seen=0; fails=0; worst_iso=0; worst_iso_g=None; crit_found=[]
    for g6 in bases:
        for t in (2,3):
            nn,EE=blow(g6,t)
            if nn>30: continue
            info=loads(nn,EE)
            if info is None: continue
            d=check(info)
            if d is None: continue
            seen+=1
            if d['max_iso']>worst_iso: worst_iso=d['max_iso']; worst_iso_g=(g6,t,nn)
            if d['critical']>0: crit_found.append((g6,t,nn))
            if not d['ok']:
                fails+=1
                print(f"  FAIL {g6}[{t}] N={d['N']}: rowsum<=N:{d['rowsum_ok']} critical={d['critical']} "
                      f"maxOiso={d['max_iso']} blockdet>0:{d['blockdet_pos']}",flush=True)
    print(f"\n  scanned {seen} overloaded blow-ups (N up to 30): FAILS={fails}")
    print(f"  max O-isolated-component size found = {worst_iso} @ {worst_iso_g}  (want 1)")
    print(f"  critical components found: {crit_found}  (want [])")
