"""EXACT gate of Codex block-301 net_H(v)<=3 split, scoped to multi-pos-K-comp configs, high bands H_j (2t_j>=N),
v in H_j. B_out/M_out/B_in/M_in, lip_slack=dB_total-dM_total. net_H(v)=B_out-M_out=lip_slack-(B_in-M_in).
  (A) B_in(v) >= M_in(v).
  (B) B_in-M_in=0 => lip_slack <= 3.
  (C) lip_slack>3 => B_in-M_in >= lip_slack-3.   [(C) == verified net cap]
Full battery; report viol + tight (C) dumps."""
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
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    if len(set(cid[v] for v in range(n) if T[v]>0))<2: return
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    for j in range(len(levs)-1):
        tj=levs[j]
        if 2*tj<F(n): continue
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        for v in H:
            B_out=sum(1 for w in adj[v] if w not in H and side[v]!=side[w])
            M_out=sum(1 for w in adj[v] if w not in H and side[v]==side[w])
            B_in=sum(1 for w in adj[v] if w in H and w!=v and side[v]!=side[w])
            M_in=sum(1 for w in adj[v] if w in H and w!=v and side[v]==side[w])
            lip=(B_out+B_in)-(M_out+M_in)
            acc['npts']+=1
            if B_in<M_in:
                acc['vA']+=1
                if acc['fA'] is None: acc['fA']=(name,n,j,v,B_in,M_in)
            if B_in-M_in==0 and lip>3:
                acc['vB']+=1
                if acc['fB'] is None: acc['fB']=(name,n,j,v,lip)
            if lip>3:
                acc['nC']+=1
                if B_in-M_in < lip-3:
                    acc['vC']+=1
                    if acc['fC'] is None: acc['fC']=(name,n,j,v,lip,B_in,M_in)
                else:
                    acc['Ctight'].append((name,n,j,v,lip,B_in,M_in,B_out,M_out,str(T[v])))

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
    acc={'npts':0,'vA':0,'vB':0,'vC':0,'nC':0,'fA':None,'fB':None,'fC':None,'Ctight':[]}
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
        print("  census N=%d done (vA=%d vB=%d vC=%d)"%(nn,acc['vA'],acc['vB'],acc['vC']),flush=True)
    print("\n  scoped (j,v) points=%d"%acc['npts'],flush=True)
    print("  (A) B_in>=M_in: violations=%d %s"%(acc['vA'],acc['fA'] or ''),flush=True)
    print("  (B) B_in-M_in=0 => lip<=3: violations=%d %s"%(acc['vB'],acc['fB'] or ''),flush=True)
    print("  (C) lip>3 => B_in-M_in>=lip-3: cases(lip>3)=%d violations=%d %s"%(acc['nC'],acc['vC'],acc['fC'] or ''),flush=True)
    print("  (C) tight cases (name,N,j,v,lip,B_in,M_in,B_out,M_out,T[v]):",flush=True)
    for d in acc['Ctight'][:8]: print("    %s"%(d,),flush=True)
    print("  === net_H split %s ==="%("(A)&(B)&(C) ALL HOLD => local proof route for net_H<=3" if (acc['vA']==0 and acc['vB']==0 and acc['vC']==0) else "FAILS"),flush=True)
