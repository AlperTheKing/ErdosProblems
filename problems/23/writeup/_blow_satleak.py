"""Blow-up stress (N=15..30) for the two candidate lemmas behind condition (1):
  (SAT-LEAK)   every saturated underloaded vertex (T[q]=N, q in Q) has leak[q]>0.
  (NO-CRIT)    no critical KQQ-component.
  (O-ISO-SING) every O-isolated KQQ-component is a singleton.
Pure EXACT Fraction. Uses a curated list of bases that produce overloaded vertices."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K, reach_components

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
    # SAT-LEAK
    sat_leak0=[Q[i] for i in range(m) if r[i]==0 and leak[i]==0]
    min_leak_sat=None
    for i in range(m):
        if r[i]==0:
            if min_leak_sat is None or leak[i]<min_leak_sat: min_leak_sat=leak[i]
    # NO-CRIT and O-ISO-SING
    critical=0; max_iso=0; nsat=sum(1 for i in range(m) if r[i]==0)
    rowsum_ok=all(sum(KQQ[i][j] for j in range(m))<=F(N) for i in range(m))
    for c in range(ncomp):
        nodes=[i for i in range(m) if comp[i]==c]
        if all(leak[i]==0 for i in nodes): max_iso=max(max_iso,len(nodes))
        if all(r[i]==0 and leak[i]==0 for i in nodes): critical+=1
    return dict(N=N,m=m,nO=len(O),nsat=nsat,sat_leak0=sat_leak0,
                min_leak_sat=min_leak_sat,critical=critical,max_iso=max_iso,rowsum_ok=rowsum_ok)

if __name__=="__main__":
    print("=== BLOW-UP STRESS N>=15: SAT-LEAK, NO-CRIT, O-ISO-SINGLETON (exact) ===")
    bases=["G?bF`w","H?bBF_{","I?ABCc]}?","I?BD@g]Qo","I?BD@jWF_","I?BD?{{}?",
           "J???E?pNu\\?","J?`@C_W{Ck?","J?AE@`KkH{?","I?BF@zWF_"]
    nfail=0; worst_iso=0; nsat_total=0
    for g6 in bases:
        for t in (2,3,4):
            nn,EE=blow(g6,t)
            if nn<14 or nn>30: continue
            info=loads(nn,EE)
            if info is None: continue
            d=check(info)
            if d is None: continue
            nsat_total+=d['nsat']
            bad = d['sat_leak0'] or d['critical']>0 or d['max_iso']>1 or not d['rowsum_ok']
            if bad: nfail+=1
            worst_iso=max(worst_iso,d['max_iso'])
            ml = float(d['min_leak_sat']) if d['min_leak_sat'] is not None else None
            print(f"  {g6}[{t}] N={d['N']}: nO={d['nO']} nsat={d['nsat']} SAT-LEAK0={d['sat_leak0']} "
                  f"minleak_sat={ml} critical={d['critical']} maxOiso={d['max_iso']} rowsum<=N:{d['rowsum_ok']} "
                  f"{'<<FAIL' if bad else ''}",flush=True)
    print(f"\n  FAILS={nfail}; max O-iso-size={worst_iso} (want 1); total saturated verts seen={nsat_total}")
