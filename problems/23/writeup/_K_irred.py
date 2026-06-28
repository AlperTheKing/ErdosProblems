"""Test the IRREDUCIBILITY lever for condition (1):
A critical KQQ-component C yields a nonneg eigenvector x (supp = C, zero on O) with K x = N x globally
(shown: for o in O, K[o,q']=0 for q' in C because leak[q']=0 => K[q',o]=0=K[o,q']; cross-component
zero; within C it's the Perron relation). So if the FULL K is IRREDUCIBLE, its only nonneg eigenvector
is strictly positive, contradicting x=0 on O (O nonempty). => no critical component => condition (1).

So condition (1) is PROVEN whenever K is irreducible (K-graph {v~w: K[v,w]>0} connected on V).
We test: is the K-graph connected for all configs with O nonempty? Over census + blow-ups, EXACT.
If K-graph is connected, condition (1) is proven for that config by the irreducibility argument.
Report: any config (with O) where K-graph is DISCONNECTED, and if so whether a separate component
could be critical (i.e. could the disconnection break the proof)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K

def kgraph_components(K,n):
    seen=[-1]*n; cid=0
    for s in range(n):
        if seen[s]!=-1: continue
        st=[s]; seen[s]=cid
        while st:
            u=st.pop()
            for v in range(n):
                if v!=u and seen[v]==-1 and K[u][v]>0: seen[v]=cid; st.append(v)
        cid+=1
    return seen,cid

def test(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return None
    comp,nc=kgraph_components(K,n)
    # is the K-graph connected (over all of V)?
    connected = (nc==1)
    # if disconnected, do all components contain at least one O vertex OR are they non-critical?
    # a component (in K-graph on V) that lies entirely in Q and is 'critical' would be the danger.
    # check each V-component: if subset of Q and all its verts saturated+leak0 => critical (dangerous).
    Oset=set(O); Qset=set(Q)
    danger=0
    for c in range(nc):
        nodes=[v for v in range(n) if comp[v]==c]
        if all(v in Qset for v in nodes):
            # leak within component: for v in nodes, K[v,o]=0 for o in O automatically (different comp)
            # so leak=0 for all; critical iff all saturated
            if all(T[v]==F(N) for v in nodes): danger+=1
    return dict(N=N,nO=len(O),kg_components=nc,connected=connected,danger=danger,
                comp_sizes=sorted([sum(1 for v in range(n) if comp[v]==c) for c in range(nc)]))

def run(Nmax,Nmin=7):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; disc=0; danger=0; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            d=test(info)
            if d is None: continue
            nt+=1
            if not d['connected']:
                disc+=1
                if wg is None: wg=(g6,d['comp_sizes'])
            danger+=d['danger']
        print(f"  N={nn}: with-O={nt} | K-graph DISCONNECTED={disc}{(' ex='+str(wg)) if wg else ''} | "
              f"critical-V-components(DANGER)={danger}",flush=True)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

if __name__=="__main__":
    print("=== K-graph irreducibility lever for condition (1) ===")
    print("    connected K-graph => condition(1) proven (irreducible Perron). report disconnections + danger.")
    for g6,t in [("H?AAF_}",1),("J?AE@`KkH{?",1),("H?bBF_{",2),("I?BD@g]Qo",2),("J???E?pNu\\?",2)]:
        nn,EE=blow(g6,t); info=loads(nn,EE)
        if info:
            d=test(info)
            if d: print(f"  {g6}[{t}] N={d['N']}: K-comps={d['kg_components']} connected={d['connected']} "
                        f"sizes={d['comp_sizes']} danger={d['danger']}")
    run(11,7)
