"""Codex block 37: SAT-BOUNDARY-DEFICIT. For every K-component C disjoint from O:
   deficit(C) = N|C| - sum_{v in C} T(v)  >=  sat_boundary(C) = #B-boundary edges (x,y), x in C, y outside, T(x)=N.
Weaker than deficit>=dB; still excludes critical components (critical => deficit=0, sat_boundary>=1). Exact Fraction.
Test loads-gate + glued constructions (non-vacuous) + census loads-cut."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _schur_spec import pf_exact
from _superphi import blow
from _bdef import components
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def check(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    O=set(v for v in range(n) if T[v]>N)
    Bset=info['Bset']
    res=[]
    for C in components(K,n):
        Cs=set(C)
        if Cs & O: continue
        deficit=F(N*len(C))-sum(T[v] for v in C)
        satb=0
        for (a,b) in Bset:
            if (a in Cs) ^ (b in Cs):
                xin = a if a in Cs else b
                if T[xin]==N: satb+=1
        res.append((tuple(C),deficit,satb,deficit<satb))
    return res,N

def show(name,info):
    if info is None: return 0
    res,N=check(info)
    viol=[r for r in res if r[3]]
    if viol: print(f"  {name} (N={info['n']}): *** SAT-BDEF VIOLATION {viol[:3]}",flush=True)
    return len(viol)

def battery():
    cases=[]; g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5)); g23=mycielski(*gr)
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr,g23]:
            for br in [[(0,0)],[(0,1)],[(0,gN-1)],[(0,0),(2,3)],[(0,2),(2,5)],[(1,0),(3,4)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n<=24 and is_triangle_free(n,E): cases.append((f"isl{iN}+gad{gN} br{br} N={n}",n,E))
    return cases

if __name__=="__main__":
    print("=== SAT-BOUNDARY-DEFICIT exact stress ===")
    tot=0
    print("--- glued constructions (non-vacuous) ---")
    for name,n,E in battery(): tot+=show(name,loads(n,E))
    print("--- named / Mycielskians / blow-ups ---")
    C5=(5,Cn(5)); n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(7,Cn(7))
    for nm,(nn,EE) in [("Grotzsch",(n1,E1)),("MycGrotzsch N=23",(n2,E2)),("MycC7 N=15",(m1,F1))]:
        tot+=show(nm,loads(nn,EE))
    for g6,t in [("J?AADBWeay?",2),("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t); tot+=show(f"{g6}[{t}]",loads(nn,EE))
    print("--- census loads-cut N=7..11 ---")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        cv=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            res,N=check(info)
            cv+=sum(1 for r in res if r[3])
        print(f"  census N={nn}: SAT-BDEF violations={cv}",flush=True); tot+=cv
    print(f"\nTOTAL SAT-BOUNDARY-DEFICIT violations: {tot}")
