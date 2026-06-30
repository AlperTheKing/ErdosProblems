"""COMPREHENSIVE diagnostic answering Codex 301/302/305/306 at once. Multi-pos-K-comp gamma-min cuts, high
bands H={T>t_j} 2t_j>=N. Per band: delta_M(H) (internal bad edges). Per vertex v in H: B_in,M_in,B_out,M_out,
dB,dM,lip=dB-dM, zmuB(zero-mu B-edges),pmuB, incident bad-edge lengths, K-comp size. Tests:
 split(A) B_in>=M_in; (B) isolated=>lip<=3; (C) lip>3=>B_in-M_in>=lip-3; delta_M(H)=0; I1 dM=1 (isolated);
 I2 dB<=4 (isolated); I3 zmuB<=1 (isolated). Dumps ALL distinct scoped isolated high-vertex patterns."""
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
    badset={}
    for f in M: badset[(min(f),max(f))]=ell[f]
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    if len(set(cid[v] for v in range(n) if T[v]>0))<2: return
    csize={}
    for v in range(n): csize[cid[v]]=csize.get(cid[v],0)+1
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    for j in range(len(levs)-1):
        tj=levs[j]
        if 2*tj<F(n): continue
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        dM_H=sum(1 for f in M if f[0] in H and f[1] in H)   # internal bad edges
        if dM_H>0: acc['vDM']+=1
        for v in H:
            B_in=M_in=B_out=M_out=zmuB=pmuB=0; badlens=[]
            for w in adj[v]:
                e=(min(v,w),max(v,w))
                bad = e in badset
                inside = w in H
                if side[v]!=side[w]:  # B edge
                    if inside: B_in+=1
                    else: B_out+=1
                    mv=mu.get(e,F(0))
                    if mv==0: zmuB+=1
                    else: pmuB+=1
                else:  # bad edge
                    if inside: M_in+=1
                    else: M_out+=1
                if bad: badlens.append(badset[e])
            dB=B_in+B_out; dM=M_in+M_out; lip=dB-dM; net=B_out-M_out
            acc['npts']+=1
            isolated = (B_in==0 and M_in==0)
            if B_in<M_in: acc['vA']+=1
            if isolated and lip>3: acc['vB']+=1
            if lip>3 and (B_in-M_in)<lip-3: acc['vC']+=1
            if isolated:
                acc['niso']+=1
                if dM!=1: acc['vI1']+=1
                if dB>4: acc['vI2']+=1
                if zmuB>1: acc['vI3']+=1
                acc['iso'].append((name,j,v,str(T[v]),dB,dM,zmuB,pmuB,B_out,M_out,sorted(badlens),csize[cid[v]],net))

def blowup(parts):
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
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    acc=dict(npts=0,niso=0,vA=0,vB=0,vC=0,vDM=0,vI1=0,vI2=0,vI3=0,iso=[])
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0)),("C5|C5",bridge((5,Cn(5)),(5,Cn(5)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done"%nn,flush=True)
    print("\n  scoped points=%d, isolated=%d, bands with delta_M(H)>0=%d"%(acc['npts'],acc['niso'],acc['vDM']),flush=True)
    print("  split: (A)B_in>=M_in viol=%d (B)isolated=>lip<=3 viol=%d (C)lip>3=>B_in-M_in>=lip-3 viol=%d"%(acc['vA'],acc['vB'],acc['vC']),flush=True)
    print("  306: delta_M(H)=0 for all scoped high bands: %s (viol=%d)"%("YES" if acc['vDM']==0 else "NO",acc['vDM']),flush=True)
    print("  305 isolated: I1 dM=1 viol=%d ; I2 dB<=4 viol=%d ; I3 zmuB<=1 viol=%d"%(acc['vI1'],acc['vI2'],acc['vI3']),flush=True)
    print("  ALL distinct isolated high-vertex patterns (name,j,v,T,dB,dM,zmuB,pmuB,B_out,M_out,badlens,Ksize,net):",flush=True)
    seen=set()
    for d in acc['iso']:
        key=(d[0],d[4],d[5],d[6],tuple(d[10]))
        if key in seen: continue
        seen.add(key); print("    %s"%(d,),flush=True)
    print("  === comprehensive diagnostic done (%d distinct iso patterns) ==="%len(seen),flush=True)
