"""Find PROPER Q-only K-components: O nonempty AND a K-component C disjoint from O with C != V.
These are the only nontrivial test cases for cond(1)/boundary-deficit. For each, report
deficit, dB, and whether the LOCAL per-vertex charge (slack(v)>=crossdeg(v)) holds.
Also stress iterated Mycielskians + N=22 blowup."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one
from _superphi import blow

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def proper_components(info):
    """Return list of (C, dict) for PROPER components disjoint from O, given O nonempty."""
    B=build(info)
    K=B['K']; T=B['T']; N=B['N']; n=B['n']; Bset=B['Bset']; O=B['O']
    if not O: return B, []
    comps=components(K,n)
    out=[]
    for C in comps:
        Cs=set(C)
        if Cs&O: continue
        if len(C)==n: continue  # not proper
        d=analyze_one(B,C)
        cross=[(a,b) for (a,b) in Bset if (a in Cs)^(b in Cs)]
        deg_cross={v:0 for v in C}
        for (a,b) in cross:
            x=a if a in Cs else b
            deg_cross[x]+=1
        slack={v:F(N)-T[v] for v in C}
        local_ok=all(slack[v]>=deg_cross[v] for v in C)
        d['local_ok']=local_ok
        d['allT0']=all(T[v]==0 for v in C)
        out.append((C,d))
    return B, out

def census(Nmax,Nmin=5,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nproper=0; nnontriv=0; bd_fail=0; loc_fail=0; ex=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B,comps=proper_components(info)
            for C,d in comps:
                nproper+=1
                if not (d['sz']==1 and d['allT0']):
                    nnontriv+=1
                    if ex is None: ex=(g6,C,d['sz'],float(d['deficit']),d['dB'],d['allT0'])
                if not d['bd_ok']: bd_fail+=1
                if not d['local_ok']: loc_fail+=1
        print(f"  N={nn}(str{stride}): PROPER-Q-comps={nproper} (nontrivial={nnontriv}) bd_FAIL={bd_fail} LOCAL_FAIL={loc_fail} ex={ex}",flush=True)

def show(name,info):
    B,comps=proper_components(info)
    print(f"  {name} (N={B['N']}): O-size={len(B['O'])} #proper-Q-comps={len(comps)}")
    for C,d in comps:
        tag="TRIVIAL(T0-singleton)" if (d['sz']==1 and d['allT0']) else "NONTRIVIAL"
        print(f"     C(sz{d['sz']}) {tag}: deficit={float(d['deficit'])} dB={d['dB']} bd_ok={d['bd_ok']} LOCAL_ok={d['local_ok']} nFC={d['nFC']}")

if __name__=="__main__":
    print("=== PROPER Q-only K-components (the real cond(1) test cases) ===")
    # iterated Mycielskians
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5)
    n2,E2=mycielski(n1,E1)
    n3,E3=mycielski(n2,E2)
    m1,F1=mycielski(*C7)
    m2,F2=mycielski(m1,F1)
    chain=[("Grotzsch N=11",(n1,E1)),("Myc(Grotzsch) N=23",(n2,E2)),
           ("Myc^3(C5) N=47",(n3,E3)),("Myc(C7) N=15",(m1,F1)),("Myc(Myc(C7)) N=31",(m2,F2))]
    for name,(nn,EE) in chain:
        info=loads(nn,EE)
        if info is None: print(f"  {name}: loads=None"); continue
        show(name,info)
    # N=22 blowup + overloaded blowups
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t)
        if nn>24: continue
        info=loads(nn,EE)
        if info: show(f"{g6}[{t}]",info)
    print("--- census: where do PROPER nontrivial Q-only components occur? ---")
    census(11,5,1)
