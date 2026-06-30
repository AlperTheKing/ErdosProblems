"""EXACT gate of Codex block-242 PRESSURE-SURPLUS-HALL (part (B) of the corrected 2-commodity transport).
Bands as in _level_transport: eta=N^2/25-beta, theta=(N+eta)/2, levels={0,theta}+positiveT.
  alpha_j=25(N+eta-(t_j+t_{j+1})), Delta_j, H_j={T>t_j}, sigma_j=dB-dM. K-components via kcomponents(n,cyc).
  Source_C(k)=sum_{j<k,alpha_j>0} Delta_j*alpha_j*|H_j cap C|; Volume_C(k)=sum_{j<k,alpha_j<0} Delta_j*(-alpha_j)*|H_j cap C|.
  Pressure(k)=sum_{j<k} 5N*Delta_j*sigma_j.
ASK: for every prefix k,  Pressure(k) <= sum_C max(0, Source_C(k)-Volume_C(k)).
Full battery. Report violations + min margin + first failure."""
import subprocess
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
    beta=len(M); eta=F(n*n,25)-beta; theta=(F(n)+eta)/2
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]; comps=sorted(set(cid))
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]+[theta]))
    bands=[]
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]; D=tn-tj
        if D<=0: continue
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        alpha=25*(F(n)+eta-(tj+tn))
        dB=dM=0
        for u in H:
            for v in adj[u]:
                if v in H: continue
                if side[u]!=side[v]: dB+=1
                else: dM+=1
        sigma=dB-dM
        cnt={c:0 for c in comps}
        for v in H: cnt[cid[v]]+=1
        bands.append((D,alpha,sigma,cnt))
    # prefix sweep
    Src={c:F(0) for c in comps}; Vol={c:F(0) for c in comps}; Press=F(0)
    acc['nconf']+=1
    for k in range(1,len(bands)+1):
        D,alpha,sigma,cnt=bands[k-1]
        if alpha>0:
            for c in comps: Src[c]=Src[c]+D*alpha*cnt[c]
        elif alpha<0:
            for c in comps: Vol[c]=Vol[c]+D*(-alpha)*cnt[c]
        Press=Press+5*F(n)*D*sigma
        surplus=sum((Src[c]-Vol[c]) for c in comps if Src[c]-Vol[c]>0)
        margin=surplus-Press
        acc['rows']+=1
        if margin<acc['minm'][0]: acc['minm']=(margin,name,n,beta,k,str(sigma))
        if margin<0:
            acc['viol']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,beta,k,str(Press),str(surplus),str(margin))

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
    acc={'nconf':0,'rows':0,'viol':0,'first':None,'minm':(F(10**18),'','','','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: viol=%d"%acc['viol'],flush=True)
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
    print("  blow-ups + Mycielskians + glued done (viol=%d)"%acc['viol'],flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol+%d)"%(nn,acc['viol']-v0),flush=True)
    print("\n  configs=%d rows=%d  PRESSURE-SURPLUS-HALL violations=%d"%(acc['nconf'],acc['rows'],acc['viol']),flush=True)
    print("  MIN margin = %s at (name,N,beta,k,sigma)=%s"%(float(acc['minm'][0]),acc['minm'][1:]),flush=True)
    if acc['first']: print("  first violation: %s"%(acc['first'],),flush=True)
    print("  === PRESSURE-SURPLUS-HALL %s ==="%("HOLDS" if not acc['viol'] else "FAILS"),flush=True)
