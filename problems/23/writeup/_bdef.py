"""INDEPENDENT exact stress of Codex's BOUNDARY-DEFICIT lemma (block 19):
For every full K-component C (edges K[v,w]>0) with C disjoint from O={T>N}:
    deficit(C) := N*|C| - mass(C)  >=  dB(C) := #B-edges crossing C.
K built independently from pf_exact (NOT Codex's build_K). Exact Fraction. Report any violation with witness,
and CHARACTERIZE the C-with-O-empty components (are they all trivial T=0 singletons? any non-trivial Q-only comp?)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact
from _superphi import blow

def components(K,n):
    seen=[False]*n; comps=[]
    for s in range(n):
        if seen[s]: continue
        stack=[s]; seen[s]=True; C=[]
        while stack:
            v=stack.pop(); C.append(v)
            for w in range(n):
                if w!=v and not seen[w] and K[v][w]>0:
                    seen[w]=True; stack.append(w)
        comps.append(sorted(C))
    return comps

def analyze(info):
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
    comps=components(K,n)
    out=[]  # (C, deficit, dB, mass, allT0, issingleton, fail)
    for C in comps:
        Cs=set(C)
        if Cs & O: continue   # only C disjoint from O
        mass=sum(T[v] for v in C)
        deficit=F(N*len(C))-mass
        dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
        allT0=all(T[v]==0 for v in C)
        out.append((tuple(C),deficit,dB,mass,allT0,len(C)==1,deficit<dB))
    return out,N,n

def run_census(Nmax,Nmin=5,stride=1):
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        fails=0; nontrivQ=0; worst=None; wg=None; nQcomp=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            res,N,_=analyze(info)
            for (C,deficit,dB,mass,allT0,single,fail) in res:
                nQcomp+=1
                if fail: fails+=1
                if not (single and allT0): nontrivQ+=1   # a non-trivial Q-only component
                slack=deficit-dB
                if worst is None or slack<worst: worst=slack; wg=(g6,C,float(deficit),dB)
                if fail and wg is None: wg=(g6,C,float(deficit),dB)
        print(f"  census N={nn}(str{stride}): Q-only comps={nQcomp} FAILS={fails} | NON-trivial Q-only comps(|C|>1 or T>0)={nontrivQ} | min(deficit-dB)={float(worst) if worst is not None else 'na'} @ {wg}",flush=True)

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def show(name,info):
    res,N,n=analyze(info)
    fails=[r for r in res if r[6]]
    nontriv=[r for r in res if not (r[5] and r[4])]
    import sys
    print(f"  {name} (N={N}): Q-only comps={len(res)} FAILS={len(fails)} non-trivial-Q-only={len(nontriv)}"
          + (f"  *** FAIL {fails[0]}" if fails else ""), flush=True)
    for r in nontriv:
        print(f"      NONTRIVIAL Q-only C(|C|={len(r[0])}): deficit={float(r[1])} dB={r[2]} mass={float(r[3])} allT0={r[4]}")

if __name__=="__main__":
    print("=== BOUNDARY-DEFICIT independent exact stress ===")
    # named
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?","J?AEB?oE?W?"]:
        n,E=dec(g6); show(g6,loads(n,E))
    # N=22 witness + overloaded blow-ups
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t)
        if nn>24: continue
        info=loads(nn,EE)
        if info: show(f"{g6}[{t}]",info)
    # iterated Mycielskians: C5->Grotzsch(11)->Myc(23)->Myc(47); Myc(C7)=15->31
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    C7=(7,[(i,(i+1)%7) for i in range(7)])
    chain=[("C5",C5)]
    n1,E1=mycielski(*C5); chain.append(("Grotzsch N=11",(n1,E1)))
    n2,E2=mycielski(n1,E1); chain.append(("Myc(Grotzsch) N=23",(n2,E2)))
    m1,F1=mycielski(*C7); chain.append(("Myc(C7) N=15",(m1,F1)))
    for name,(nn,EE) in chain:
        info=loads(nn,EE)
        if info is None: print(f"  {name}: loads=None"); continue
        show(name,info)
    # census
    run_census(11,5,1)
