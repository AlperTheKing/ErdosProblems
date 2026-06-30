"""EXACT gate of Codex block-308 COMBINED LOCAL-HIGH-STRUCTURE lemma. Scoped: multi-pos-K-comp gamma-min
maxcut, high band H={T>t_j} with 2t_j>=N.
  (L1) delta_M(H)=0  [no internal bad edge in H].
  (L2) every isolated v in H (B_in=M_in=0) has dM_total(v)=1 AND dB_total(v)<=4.
  (L3) every v in H has dB_total(v)-dM_total(v) <= 4.   [NEW: ALL v in H, not just isolated]
Report L1/L2/L3 violations separately. Dump L3=4 equality cases and L2 dB=4 cases. If L3 fails, report
whether B_in(v) >= lip_slack(v)-3 at the failure (absorption)."""
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
    badset=set((min(a,b),max(a,b)) for a,b in M)
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    if len(set(cid[v] for v in range(n) if T[v]>0))<2: return
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    for j in range(len(levs)-1):
        tj=levs[j]
        if 2*tj<F(n): continue
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        dM_H=sum(1 for f in M if f[0] in H and f[1] in H)
        if dM_H>0:
            acc['vL1']+=1
            if acc['fL1'] is None: acc['fL1']=(name,n,j,dM_H)
        for v in H:
            B_in=M_in=B_out=M_out=0
            for w in adj[v]:
                if w==v: continue
                inside=w in H
                if side[v]!=side[w]:
                    if inside: B_in+=1
                    else: B_out+=1
                else:
                    if inside: M_in+=1
                    else: M_out+=1
            dB=B_in+B_out; dM=M_in+M_out; lip=dB-dM
            acc['npts']+=1
            isolated=(B_in==0 and M_in==0)
            # L3: all v in H
            if lip>4:
                acc['vL3']+=1
                absorb = B_in >= lip-3
                if acc['fL3'] is None: acc['fL3']=(name,n,j,v,lip,B_in,M_in,absorb)
            elif lip==4:
                acc['L3eq'].append((name,n,j,v,dB,dM,B_in,M_in,B_out,M_out,str(T[v]),isolated))
            # L2: isolated v
            if isolated:
                acc['niso']+=1
                if dM!=1:
                    acc['vL2dm']+=1
                    if acc['fL2dm'] is None: acc['fL2dm']=(name,n,j,v,dM)
                if dB>4:
                    acc['vL2db']+=1
                    if acc['fL2db'] is None: acc['fL2db']=(name,n,j,v,dB)
                if dB==4:
                    acc['L2eq'].append((name,n,j,v,dM,str(T[v])))

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

if __name__=="__main__":
    acc=dict(npts=0,niso=0,vL1=0,vL2dm=0,vL2db=0,vL3=0,fL1=None,fL2dm=None,fL2db=None,fL3=None,L3eq=[],L2eq=[])
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
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (vL1=%d vL2dm=%d vL2db=%d vL3=%d)"%(nn,acc['vL1'],acc['vL2dm'],acc['vL2db'],acc['vL3']),flush=True)
    print("\n  scoped points=%d, isolated=%d"%(acc['npts'],acc['niso']),flush=True)
    print("  (L1) delta_M(H)=0: viol=%d %s"%(acc['vL1'],acc['fL1'] or ''),flush=True)
    print("  (L2) isolated=>dM=1: viol=%d %s ; isolated=>dB<=4: viol=%d %s"%(acc['vL2dm'],acc['fL2dm'] or '',acc['vL2db'],acc['fL2db'] or ''),flush=True)
    print("  (L3) all v in H: dB-dM<=4: viol=%d %s"%(acc['vL3'],acc['fL3'] or ''),flush=True)
    print("  L3=4 equality cases (distinct, name,j,v,dB,dM,B_in,M_in,B_out,M_out,T,isolated):",flush=True)
    seen=set()
    for d in acc['L3eq']:
        key=(d[0],d[3],d[4],d[5],d[11]);
        if key in seen: continue
        seen.add(key); print("    %s"%(d,),flush=True)
    print("  L2 dB=4 isolated cases (distinct, name,j,v,dM,T):",flush=True)
    seen2=set()
    for d in acc['L2eq']:
        key=(d[0],d[4]);
        if key in seen2: continue
        seen2.add(key); print("    %s"%(d,),flush=True)
    ok = acc['vL1']==0 and acc['vL2dm']==0 and acc['vL2db']==0 and acc['vL3']==0
    print("  === COMBINED L1&L2&L3 %s ==="%("ALL HOLD => clean local proof of net_H<=3" if ok else "FAILS"),flush=True)
