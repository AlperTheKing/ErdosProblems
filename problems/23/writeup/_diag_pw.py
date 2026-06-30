"""EXACT gate of Codex block-300. Multi-component (>=2 pos K-comp) gamma-min cuts. theta=(N+eta)/2.
ASK A: L2=levels_pos[-2] <= theta - 3N/25. report viol + min margin.
ASK B: for every high-band vertex v in H_j with net_H(v)>=3 (tight), dump full boundary profile:
  dB_total(v),dM_total(v),lip_slack=dB-dM, B_out,M_out,B_in,M_in, T[v], incident bad edges."""
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
    m=len(M); eta=F(n*n,25)-m; theta=(F(n)+eta)/2
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    if len(set(cid[v] for v in range(n) if T[v]>0))<2: return
    badset=set((min(a,b),max(a,b)) for a,b in M)
    levels_pos=sorted(set(T[v] for v in range(n) if T[v]>0))
    L2=levels_pos[-2] if len(levels_pos)>=2 else F(0)
    margA=theta-F(3*n,25)-L2
    if margA<acc['mA'][0]: acc['mA']=(margA,name,n)
    if L2>theta-F(3*n,25):
        acc['vA']+=1
        if acc['fA'] is None: acc['fA']=(name,n,str(margA))
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    for j in range(len(levs)-1):
        tj=levs[j]
        if 2*tj<F(n): continue
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        for v in H:
            B_out=sum(1 for w in adj[v] if w not in H and side[v]!=side[w])
            M_out=sum(1 for w in adj[v] if w not in H and side[v]==side[w])
            net=B_out-M_out
            if net>=3:
                B_in=sum(1 for w in adj[v] if w in H and w!=v and side[v]!=side[w])
                M_in=sum(1 for w in adj[v] if w in H and w!=v and side[v]==side[w])
                dB=B_out+B_in; dM=M_out+M_in
                incbad=[(min(v,w),max(v,w)) for w in adj[v] if (min(v,w),max(v,w)) in badset]
                acc['dumps'].append((name,n,j,v,net,dB,dM,dB-dM,B_out,M_out,B_in,M_in,str(T[v]),len(incbad)))

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
    acc={'vA':0,'fA':None,'mA':(F(10**18),'',''),'dumps':[]}
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
        print("  census N=%d done (vA=%d, dumps=%d)"%(nn,acc['vA'],len(acc['dumps'])),flush=True)
    print("\n  ASK A: L2 <= theta-3N/25 violations=%d  min margin=%s %s"%(acc['vA'],str(acc['mA'][0]),acc['mA'][1:]),flush=True)
    print("  ASK B: net_H(v)>=3 tight-vertex dumps (name,N,j,v,net,dB,dM,lip_slack,B_out,M_out,B_in,M_in,T[v],#incbad):",flush=True)
    seen=set()
    for d in acc['dumps']:
        key=(d[0],d[3],d[4])
        if key in seen: continue
        seen.add(key)
        print("    %s"%(d,),flush=True)
    print("  === ASK A %s ; ASK B dumped %d tight vertices ==="%("HOLDS" if not acc['vA'] else "FAILS",len(seen)),flush=True)
