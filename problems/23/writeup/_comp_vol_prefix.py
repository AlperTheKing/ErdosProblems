"""EXACT standalone gate of claim (A): PER-COMPONENT VOLUME PREFIX.
For every K-component c and threshold tau:  Phi_c(tau) = int_0^tau 25(N+eta-2s)|H_s cap c| ds >= 0,
eta=N^2/25-beta. At breakpoints t_k: Phi_c(t_k)=sum_{j<k} alpha_j*Delta_j*|H_j cap c|,
alpha_j=25(N+eta-(t_j+t_{j+1})). Split levels at theta=(N+eta)/2 to catch the in-band min. Full battery
(N<=24). Report min Phi_c over all (config, component, breakpoint) + first negative."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    beta=len(M); eta=F(n*n,25)-beta; theta=(F(n)+eta)/2
    comp_map,find=kcomponents(n,cyc)
    cid=[find(u) for u in range(n)]
    comps=set(cid)
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]+[theta]))
    # per band: Delta, alpha, and |H_j cap c| for each component
    bands=[]
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]; D=tn-tj
        if D<=0: continue
        alpha=25*(F(n)+eta-(tj+tn))
        cntc={c:0 for c in comps}
        for v in range(n):
            if T[v]>tj: cntc[cid[v]]+=1
        bands.append((D,alpha,cntc))
    acc['nconf']+=1
    for c in comps:
        run=F(0)
        for (D,alpha,cntc) in bands:
            run+=alpha*D*cntc[c]
            if run<acc['minp'][0]: acc['minp']=(run,name,n,beta,c)
            if run<0:
                acc['viol']+=1
                if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,beta,c,str(run))

def blow(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc={'nconf':0,'viol':0,'first':None,'minp':(F(10**18),'','','','')}
    for c in (5,7,9):
        for t in range(1,5):
            n,E=blow([t]*c)
            if n>24: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blow(parts)
        if n>24: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    print("  structured done: viol=%d"%acc['viol'],flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol+%d)"%(nn,acc['viol']-v0),flush=True)
    print("\n  configs=%d  (A) per-component volume-prefix violations=%d"%(acc['nconf'],acc['viol']),flush=True)
    print("  MIN Phi_c over all (config,component,breakpoint) = %s at %s"%(float(acc['minp'][0]),acc['minp'][1:]),flush=True)
    if acc['first']: print("  first negative: %s"%(acc['first'],),flush=True)
    print("  === (A) per-component volume PREFIX %s ==="%("HOLDS" if not acc['viol'] else "FAILS"),flush=True)
