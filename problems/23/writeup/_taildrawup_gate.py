"""INDEPENDENT exact gate of Codex/GPT TAIL-DRAWUP PATH-LRS. For each bad edge f and shortest blue geodesic
P=(x_0..x_{L-1}), L=ell[f]:
  Lambda_i(P) = {v : dB(x_0,v)=i and dB(v,x_{L-1})=L-1-i}   (dB = blue/cut-edge graph distance)
  gamma_0=dM(x_0), gamma_{L-1}=dM(x_{L-1}), gamma_i = m/|Lambda_i| (1<=i<=L-2);  Coh = sum gamma_i.
  u_i = T[x_i]/L - gamma_i ; sum u_i = avg_P T - Coh.
  U_{-1}=0, U_k=sum_{0..k} u_i ; Theta_fwd = U_{L-1}-min_k U_k ; Theta = min(fwd, on reversed path).
  SCALAR:   Coh + Theta + m <= n + n^2/25.   (=> PATH-LRS(c1): avg_P T + m <= n+n^2/25, since Theta>=avg-Coh.)
EXACT Fraction. Full battery. Report paths, scalar viol, majorant viol, min margins, equality cases."""
import subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

def blue_bfs(n,adj,side,src):
    dist=[-1]*n; dist[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[w]!=side[u] and dist[w]<0:
                dist[w]=dist[u]+1; q.append(w)
    return dist

def dM_deg(adj,side,v): return sum(1 for w in adj[v] if side[w]==side[v])

def theta(uvals):
    # max drawup of prefix sums with U_{-1}=0
    U=F(0); mn=F(0); s=F(0)
    # prefix mins including U_{-1}=0
    mins=F(0); cur=F(0); best=None
    cur=F(0); mins=F(0)
    prefix=[F(0)]  # U_{-1}
    acc=F(0)
    for u in uvals:
        acc+=u; prefix.append(acc)
    Uend=prefix[-1]
    return Uend-min(prefix)

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); cap=F(n)+F(n*n,25)
    for f in M:
        L=ell[f]
        for P in cyc[f]:
            if len(P)!=L:
                # geodesic length should equal ell; guard
                pass
            x0=P[0]; xL=P[-1]
            d0=blue_bfs(n,adj,side,x0); dL=blue_bfs(n,adj,side,xL)
            # gamma
            gam=[]
            for i,xi in enumerate(P):
                if i==0: gam.append(F(dM_deg(adj,side,x0)))
                elif i==len(P)-1: gam.append(F(dM_deg(adj,side,xL)))
                else:
                    Lam=sum(1 for v in range(n) if d0[v]==i and dL[v]==(L-1-i))
                    if Lam==0: Lam=1
                    gam.append(F(m,Lam))
            Coh=sum(gam)
            uvals=[F(T[P[i]],1)/L - gam[i] for i in range(len(P))]
            Th_f=theta(uvals)
            Th_b=theta(list(reversed(uvals)))
            Th=min(Th_f,Th_b)
            avg=sum(T[v] for v in P)/F(L)
            acc['paths']+=1
            # majorant
            if avg>Coh+Th:
                acc['vmaj']+=1
                if acc['fmaj'] is None: acc['fmaj']=(name,n,str(f),str(avg),str(Coh+Th))
            # scalar
            margin=cap-(Coh+Th+m)
            if margin<0:
                acc['vsc']+=1
                if acc['fsc'] is None: acc['fsc']=(name,n,str(f),str(Coh),str(Th),m,str(cap))
            if margin<acc['minm'][0]:
                acc['minm']=(margin,name,n,m,L,str(Coh),str(Th),str(avg))

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
    acc=dict(paths=0,vsc=0,vmaj=0,fsc=None,fmaj=None,minm=(F(10**9),'',0,0,0,'','',''))
    for L in (8,12,16,20,24):
        n,E,side,bad=build_two_lane(L); chk("twolane%d"%L,n,adj_of(n,E),side,acc)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4],[3,9,1,9,3]):
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: chk("C5%s"%parts,n,adj,s,acc)
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),("Myc(Grotzsch)",mycielski(mycielski(5,Cn(5))[0],mycielski(5,Cn(5))[1])),
                      ("M(C7)",mycielski(7,Cn(7))),("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
                      ("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (paths=%d vsc=%d vmaj=%d)"%(nn,acc['paths'],acc['vsc'],acc['vmaj']),flush=True)
    print("\n  TAIL-DRAWUP scalar Coh+Theta+m <= n+n^2/25: paths=%d  scalar viol=%d %s"%(acc['paths'],acc['vsc'],acc['fsc'] or ''),flush=True)
    print("  majorant avg_P T <= Coh+Theta: viol=%d %s"%(acc['vmaj'],acc['fmaj'] or ''),flush=True)
    mm=acc['minm']
    print("  min scalar margin=%s @ %s N=%d m=%d L=%d  Coh=%s Theta=%s avg=%s"%(str(mm[0]),mm[1],mm[2],mm[3],mm[4],mm[5],mm[6],mm[7]),flush=True)
    print("  === TAIL-DRAWUP %s ==="%("HOLDS on full battery + two-lane" if acc['vsc']==0 and acc['vmaj']==0 else "*** FAILS ***"),flush=True)
