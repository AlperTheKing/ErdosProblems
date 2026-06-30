"""Gate Codex 341 refined five-shadow BASE atom. For each gamma-min connected-B max cut, bad edge f with ell=5,
shortest blue geodesic P=(x0,x1,x2,x3,x4):
  V0=N_M(x4) (bad/mono neighbors of x4), V4=N_M(x0); V_i (i=1,2,3) = {v: dB(x0,v)=i and dB(v,x4)=4-i}; m04=e(V0,V4).
Verify (1) V0..V4 pairwise disjoint and x_i in V_i; (2) BaseEx=5(|V0|+|V4|+m04/|V1|+m04/|V2|+m04/|V3|-N) <= 0.
EXACT. Full battery incl Mycielskians N=23 + glued islands."""
import subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

def blue_bfs(n,adj,side,src):
    d=[-1]*n; d[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[w]!=side[u] and d[w]<0: d[w]=d[u]+1; q.append(w)
    return d

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    for f in M:
        if ell[f]!=5: continue
        for P in cyc[f]:
            if len(P)!=5: continue
            x0,x1,x2,x3,x4=P
            V0=set(w for w in adj[x4] if side[w]==side[x4])   # bad neighbors of x4
            V4=set(w for w in adj[x0] if side[w]==side[x0])   # bad neighbors of x0
            d0=blue_bfs(n,adj,side,x0); dX=blue_bfs(n,adj,side,x4)
            Vi={i:set(v for v in range(n) if d0[v]==i and dX[v]==4-i) for i in (1,2,3)}
            Vs={0:V0,1:Vi[1],2:Vi[2],3:Vi[3],4:V4}
            acc['rows']+=1
            # (1) disjoint + containment
            allv=[]
            ok_disj=True
            for i in range(5):
                for v in Vs[i]: allv.append((i,v))
            seen={}
            for i,v in allv:
                if v in seen and seen[v]!=i: ok_disj=False
                seen[v]=i
            cont = all(P[i] in Vs[i] for i in range(5))
            if not ok_disj: acc['vdisj']+=1
            if not cont:
                acc['vcont']+=1
                if acc['fcont'] is None: acc['fcont']=(name,n,str(f),[sorted(Vs[i]) for i in range(5)])
            # (2) BaseEx
            m04=sum(1 for u in V0 for w in adj[u] if w in V4 and side[u]==side[w])  # mono edges V0-V4
            # e(V0,V4): count edges with one endpoint in V0, other in V4
            m04=0
            for u in V0:
                for w in adj[u]:
                    if w in V4: m04+=1
            # each undirected edge counted... V0,V4 disjoint so count once per direction => divide
            m04=F(m04)
            if not Vi[1] or not Vi[2] or not Vi[3]:
                continue
            BaseEx=5*(F(len(V0))+F(len(V4))+m04/len(Vi[1])+m04/len(Vi[2])+m04/len(Vi[3])-F(n))
            if BaseEx>0:
                acc['vbase']+=1
                if acc['fbase'] is None: acc['fbase']=(name,n,str(f),len(V0),len(V4),str(m04),str(BaseEx))

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge_g(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc=dict(rows=0,vdisj=0,vcont=0,vbase=0,fcont=None,fbase=None)
    for parts in ([1,1,1,1,1],[2,2,2,2,2],[2,1,2,1,2],[3,2,3,2,3],[3,9,1,9,3]):
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: chk("C5%s"%parts,n,adj,s,acc)
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),("Myc(Grotzsch)",mycielski(mycielski(5,Cn(5))[0],mycielski(5,Cn(5))[1])),
                      ("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0)),
                      ("C5|C5",bridge_g((5,Cn(5)),(5,Cn(5)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    for nn in range(5,11):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (rows=%d vbase=%d)"%(nn,acc['rows'],acc['vbase']),flush=True)
    print("\n  BASE atom: rows(ell=5)=%d"%acc['rows'])
    print("  (1) disjointness viol=%d ; path-containment viol=%d %s"%(acc['vdisj'],acc['vcont'],acc['fcont'] or ''))
    print("  (2) BaseEx<=0 violations=%d %s"%(acc['vbase'],acc['fbase'] or ''))
    print("  === BASE atom %s ==="%("HOLDS (disjoint+contained, BaseEx<=0)" if acc['vdisj']==0 and acc['vcont']==0 and acc['vbase']==0 else "FAILS"))
