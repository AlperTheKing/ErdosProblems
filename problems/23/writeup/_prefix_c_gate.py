"""EXACT gate of Codex block-238 PREFIX-LOAD-PSC-c for c in {5,25}.
Net_j(c) = w_j*( D*|H_j| - 25*(2 t_j + w_j - N)*|H_j| - (25N/c)*sigma_j ),  D=N^2-25|M|, sigma_j=dB-dM>=0.
PREFIX-LOAD-PSC-c: for every prefix k, sum_{j<k} Net_j(c) >= 0.  c=25 validated; c=5 (sigma coeff 5N) is
5x harsher -- Codex min ratio ~5.03 at census, wants full-battery exact test (Myc N=23 + glued kill the
fragile routes). Report per-c min prefix margin + first violation."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

CS=(5,25)

def boundary(n,adj,side,Hset):
    dB=dM=0
    for u in Hset:
        for v in adj[u]:
            if v in Hset: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); D=F(n*n)-25*m
    levels=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    data=[]
    for j in range(len(levels)-1):
        tj=levels[j]; wj=levels[j+1]-levels[j]
        Hset=set(v for v in range(n) if T[v]>tj)
        if not Hset: continue
        Hsz=len(Hset); dB,dM=boundary(n,adj,side,Hset); sig=dB-dM
        base=D*Hsz-25*(2*tj+wj-F(n))*Hsz   # part independent of c (times w_j)
        data.append((wj,base,sig))
    acc['n']+=1
    for c in CS:
        coef=F(25*n,c)
        cum=F(0); mn=None
        for (wj,base,sig) in data:
            cum+= wj*(base-coef*sig)
            if mn is None or cum<mn: mn=cum
        if mn is None: continue
        if mn<acc['min%d'%c][0]: acc['min%d'%c]=(mn,name,n,m)
        if mn<0:
            acc['v%d'%c]+=1
            if acc['f%d'%c] is None: acc['f%d'%c]=(name,''.join(map(str,side)),n,m,float(mn))

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

if __name__=="__main__":
    acc={'n':0}
    for c in CS: acc['v%d'%c]=0; acc['f%d'%c]=None; acc['min%d'%c]=(F(10**18),'','','')
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: v5=%d v25=%d minM5=%s"%(acc['v5'],acc['v25'],float(acc['min5'][0])),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        a0=acc['v5']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (v5+%d)"%(nn,acc['v5']-a0),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                        ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done",flush=True)
    print("\n  total configs=%d"%acc['n'],flush=True)
    for c in CS:
        print("  c=%d: PREFIX-LOAD-PSC-%d violations=%d  min prefix margin=%s at %s"%(c,c,acc['v%d'%c],float(acc['min%d'%c][0]),acc['min%d'%c][1:]),flush=True)
        if acc['f%d'%c]: print("       first c=%d violation: %s"%(c,acc['f%d'%c]),flush=True)
    print("  === PREFIX-LOAD-PSC-5 %s ; -25 %s ==="%(
        "FAILS" if acc['v5'] else "HOLDS","FAILS" if acc['v25'] else "HOLDS"),flush=True)
