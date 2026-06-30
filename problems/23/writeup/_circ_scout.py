"""FLOAT SCOUT (route decision, NOT exact acceptance) of GPT circulant assembly. numpy eigvalsh min-eigenvalue of
  (1) B - R_cyc = diag(T)-K-R_cyc   [min-free circulant; expect >=0 incl non-min]
  (2) R_cyc + diag(N-T)              [closure 'Hardy-Schrodinger'; min-dependent]
R_cyc = sum_f a_f L_f, a_f=ell^3/(4(ell^2-2)), L_f=(1/|cyc|)sum_P L_{cycle(P)}. Report worst (most negative) min-eig.
If both >= -tol everywhere on gmins battery => route structure holds; (2) is the min-dependent closure to prove exactly."""
import subprocess, numpy as np
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    Mlist=list(M)
    P=np.zeros((n,len(Mlist)))
    for fi,f in enumerate(Mlist):
        Ps=cyc[f]; cf=len(Ps)
        for v in range(n):
            c=sum(1 for Pp in Ps if v in Pp)
            if c: P[v,fi]=c/cf
    K=P@P.T
    Tv=np.array([float(T[v]) for v in range(n)])
    R=np.zeros((n,n))
    for f in Mlist:
        l=ell[f]
        if l*l-2==0: continue
        a=l**3/(4*(l*l-2)); cf=len(cyc[f]); w=a/cf
        for Pp in cyc[f]:
            L=len(Pp)
            for i in range(L):
                x=Pp[i]; y=Pp[(i+1)%L]
                R[x,x]+=w; R[y,y]+=w; R[x,y]-=w; R[y,x]-=w
    S1=np.diag(Tv)-K-R
    S2=R+np.diag(n-Tv)
    e1=np.linalg.eigvalsh((S1+S1.T)/2).min()
    e2=np.linalg.eigvalsh((S2+S2.T)/2).min()
    acc['n']+=1
    if e1<acc['m1'][0]: acc['m1']=(e1,name,n,len(M))
    if e2<acc['m2'][0]: acc['m2']=(e2,name,n,len(M))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    print("  *** FLOAT SCOUT (route decision, not exact acceptance) ***",flush=True)
    acc={'n':0,'m1':(9.9,'','',''),'m2':(9.9,'','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(nm,nn,adj,s,acc)
    print("  structured done",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done"%nn,flush=True)
    print("\n  configs=%d"%acc['n'],flush=True)
    print("  (1) B - R_cyc        worst min-eig = %.6f at %s"%(acc['m1'][0],acc['m1'][1:]),flush=True)
    print("  (2) R_cyc+diag(N-T)  worst min-eig = %.6f at %s"%(acc['m2'][0],acc['m2'][1:]),flush=True)
    tol=-1e-7
    print("  => (1) %s ; (2) %s (float)"%("PSD" if acc['m1'][0]>tol else "INDEFINITE",
        "PSD => circulant route closes SPEC (gmins)!" if acc['m2'][0]>tol else "INDEFINITE -- multi-geodesic R_cyc insufficient"),flush=True)
