"""FLOAT SCOUT (route decision only; exact cert later) of the candidate: rho(O_c) <= N+eta per K-component,
which would IMPLY (CV) via Rayleigh (sum_{v in c}T^2 = l^T O_c l <= rho(O_c)*Gamma_c <= (N+eta)Gamma_c).
O = P^T P, P[v,f]=p_f(v)/|cyc_f|. Report max over battery of rho(O_c)/(N+eta). <=1 => route viable -> exact PSD cert."""
import subprocess, numpy as np
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
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
    m=len(M); eta=float(F(n*n,25)-m); A=n+eta
    Mlist=list(M)
    # P[v, f] = p_f(v)/|cyc_f|
    P=np.zeros((n,m))
    for fi,f in enumerate(Mlist):
        Ps=cyc[f]; cf=len(Ps)
        for v in range(n):
            cnt=sum(1 for Pp in Ps if v in Pp)
            if cnt: P[v,fi]=cnt/cf
    O=P.T@P
    # component of each bad edge = component of any geodesic vertex
    comp_map,find=kcomponents(n,cyc)
    fcomp=[find(cyc[f][0][0]) for f in Mlist]
    comps={}
    for fi,c in enumerate(fcomp): comps.setdefault(c,[]).append(fi)
    for c,idx in comps.items():
        Oc=O[np.ix_(idx,idx)]
        if Oc.shape[0]==0: continue
        rho=max(np.linalg.eigvalsh(Oc)) if Oc.shape[0]>1 else Oc[0,0]
        ratio=rho/A if A>0 else 9e9
        acc['n']+=1
        if ratio>acc['maxr'][0]: acc['maxr']=(ratio,name,n,m,Oc.shape[0],rho,A)

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
    acc={'n':0,'maxr':(-1.0,'','','','','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: maxratio=%.4f"%acc['maxr'][0],flush=True)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued: maxratio=%.4f"%acc['maxr'][0],flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d: maxratio=%.4f"%(nn,acc['maxr'][0]),flush=True)
    print("\n  components=%d  MAX rho(O_c)/(N+eta) = %.5f"%(acc['n'],acc['maxr'][0]),flush=True)
    print("  at %s (Oc size=%s, rho=%.4f, N+eta=%.4f)"%(acc['maxr'][1:5],acc['maxr'][4],acc['maxr'][5],acc['maxr'][6]),flush=True)
    print("  => %s"%("VIABLE: rho(O_c)<=N+eta everywhere (float); do EXACT PSD cert" if acc['maxr'][0]<=1.0 else "TOO STRONG: rho(O_c)>N+eta somewhere; need l_c-specific (CV)"),flush=True)
