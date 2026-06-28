"""Precise danger analysis for condition (1) via K-graph components.

A critical KQQ-component is O-isolated, hence a union of K-graph V-components lying entirely in Q.
So 'no critical component' is implied by: NO K-graph V-component lies entirely in Q AND is saturated
(all T=N). We classify every K-graph V-component:
  - T0-singleton: size 1, T[q]=0 (no bad edge through q). [K[q,q]=0]  -- never saturated.
  - contains an O vertex: then it is NOT inside Q, cannot be a critical (O-isolated) component.
  - Q-only with size>=2: the DANGER class. If it exists and is fully saturated => critical.
We report, over census + blow-ups, whether any Q-only K-component of size>=2 exists at all, and if so
its saturation. EXACT. Also verify the structural facts:
  (a) every size-1 K-component has T=0 (K-isolated singleton carries no bad edge).
  (b) every K-component that meets a bad-edge support has size >= 5 (since |supp(f)|>=ell(f)>=5).
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K
from _schur_spec import pf_exact

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
    Oset=set(O)
    comp,nc=kgraph_components(K,n)
    qonly_ge2=0; qonly_sat=0; size1_nonzeroT=0; meets_badedge_small=0
    P,M,ell,_=pf_exact(info)
    # support union per component for fact (b)
    for c in range(nc):
        nodes=[v for v in range(n) if comp[v]==c]
        sz=len(nodes); nodeset=set(nodes)
        has_O=any(v in Oset for v in nodes)
        # does this component carry any bad-edge support?
        meets=any((set(P[fi].keys()) & nodeset) for fi in range(len(M)))
        if sz==1 and T[nodes[0]]!=0: size1_nonzeroT+=1
        if meets and sz<5: meets_badedge_small+=1
        if (not has_O) and sz>=2:
            qonly_ge2+=1
            if all(T[v]==F(N) for v in nodes): qonly_sat+=1
    return dict(N=N,nc=nc,qonly_ge2=qonly_ge2,qonly_sat=qonly_sat,
                size1_nonzeroT=size1_nonzeroT,meets_badedge_small=meets_badedge_small)

def run(Nmax,Nmin=7):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; qo2=0; qos=0; s1=0; mbs=0; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            d=test(info)
            if d is None: continue
            nt+=1
            qo2+=d['qonly_ge2']; qos+=d['qonly_sat']; s1+=d['size1_nonzeroT']; mbs+=d['meets_badedge_small']
            if d['qonly_ge2']>0 and wg is None: wg=g6
        print(f"  N={nn}: with-O={nt} | Q-only K-comp(size>=2)={qo2}{(' ex='+wg) if wg else ''} "
              f"(saturated/critical={qos}) | size1-with-T!=0={s1} (want 0) | badedge-comp-size<5={mbs} (want 0)",flush=True)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

if __name__=="__main__":
    print("=== Q-only K-component danger analysis (condition 1) ===")
    for g6,t in [("H?bBF_{",2),("I?BD@g]Qo",2),("J???E?pNu\\?",2),("J?`@C_W{Ck?",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t); info=loads(nn,EE)
        if info:
            d=test(info)
            if d: print(f"  {g6}[{t}] N={d['N']}: Kcomps={d['nc']} Q-only(>=2)={d['qonly_ge2']} "
                        f"critical={d['qonly_sat']} size1-T!=0={d['size1_nonzeroT']} badedge-small={d['meets_badedge_small']}")
    run(11,7)
