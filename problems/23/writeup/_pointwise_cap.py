"""EXACT gate of Codex block-298 pointwise refinements (multi-comp high bands, 2t_j>=N, >=2 pos K-comps).
ASK1: net_H(v) = #cut-nbrs outside H_j - #bad-nbrs outside H_j <= 3 for every v in H_j (=> F1 sigma_j<=3|H_j|).
ASK2: t_j <= theta - 3N/25 (theta=(N+eta)/2; with maxT<=theta gives F2). Full battery; dump tight cases."""
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
    m=len(M); eta=F(n*n,25)-m; theta=(F(n)+eta)/2
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    if len(set(cid[v] for v in range(n) if T[v]>0))<2: return
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]
        if 2*tj<F(n): continue
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        # ASK2
        acc['nhigh']+=1
        mar2=theta-F(3*n,25)-tj
        if mar2<acc['m2'][0]: acc['m2']=(mar2,name,n)
        if tj>theta-F(3*n,25):
            acc['v2']+=1
            if acc['f2'] is None: acc['f2']=(name,n,str(mar2))
        # ASK1 pointwise
        for v in H:
            dB=sum(1 for w in adj[v] if w not in H and side[v]!=side[w])
            dM=sum(1 for w in adj[v] if w not in H and side[v]==side[w])
            net=dB-dM
            acc['npts']+=1
            if net>acc['maxnet'][0]: acc['maxnet']=(net,name,n,j,v,str(T[v]),dB,dM)
            if net>3:
                acc['v1']+=1
                if acc['f1'] is None: acc['f1']=(name,n,j,v,net,dB,dM)

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
    acc={'nhigh':0,'npts':0,'v1':0,'v2':0,'f1':None,'f2':None,
         'maxnet':(-99,'','','','','','',''),'m2':(F(10**18),'','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
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
        print("  census N=%d (v1=%d v2=%d)"%(nn,acc['v1'],acc['v2']),flush=True)
    print("\n  multi-comp high bands=%d, pointwise checks=%d"%(acc['nhigh'],acc['npts']),flush=True)
    print("  ASK1 net_H(v)<=3: violations=%d  MAX net = (net,name,N,j,v,T[v],dB,dM)=%s"%(acc['v1'],acc['maxnet']),flush=True)
    print("  ASK2 t_j<=theta-3N/25: violations=%d  min margin=%s %s"%(acc['v2'],str(acc['m2'][0]),acc['m2'][1:]),flush=True)
    print("  === POINTWISE F1/F2 %s ==="%("HOLD => local proof of sign lemma" if (acc['v1']==0 and acc['v2']==0) else "FAIL"),flush=True)
