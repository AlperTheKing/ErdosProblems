"""KEY GATE: is  max_v T(v) <= A = N + N^2/25 - m  for every gamma-min connected-B max cut?
If YES: since diag(T)-K >= 0 (proven local-circulant => diag(T)-K >= L_omega >= 0), Rayleigh gives
   rho(K) <= max_v T(v) <= A  =>  SUM-SBC  =>  #23.   A FULLY RIGOROUS chain modulo this pointwise gate.
Wait: diag(T)-K>=0 gives x^T K x <= sum T x^2 <= maxT * ||x||^2 => rho(K)<=maxT. Clean.
So the WHOLE conjecture would reduce to the SCALAR pointwise bound  T(v) <= N + N^2/25 - m.
Test EXACT on full battery: census N<=11 all gmin cuts, two-lane, blowups, fans, Mycielskians.
Report violations + min margin (A - maxT) + equality cases."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def gmins(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; m=len(M); A=F(N)+F(N*N,25)-m
    maxT=max(T)
    acc['tot']+=1
    margin=A-maxT
    if maxT>A:
        acc['viol']+=1
        if acc['fv'] is None: acc['fv']=(name,n,m,str(maxT),str(A),str(margin))
    if acc['minm'] is None or margin<acc['minm'][0]:
        acc['minm']=(margin,name,n,m,str(maxT),str(A))

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
def build_two_lane(L):
    a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
    n=3*(L+1); E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        E.add((min(i,a(i)),max(i,a(i)))); E.add((min(i,b(i)),max(i,b(i))))
    for i in range(L):
        for u in (a(i),b(i)):
            for v in (a(i+1),b(i+1)): E.add((min(u,v),max(u,v)))
    for e in [(0,L-2),(0,L),(2,L-2),(2,L)]: E.add((min(e),max(e)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)
    return n,sorted(E),side

if __name__=="__main__":
    acc=dict(tot=0,viol=0,fv=None,minm=None)
    for L in (8,12,16,20,24):
        n,E,side=build_two_lane(L); chk("twolane%d"%L,n,adj_of(n,E),side,acc)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in cuts[:2]: chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for sizes in [[3,9,1,9,3],[2,10,1,10,2],[1,9,3,9,1],[9,1,9,1,9],[2,1,2,1,2],[3,1,3,1,3],[4,3,4,3,4],[1,48,6,8,48][:5]]:
        n,E=blowup(sizes)
        if n<=26:
            adj,cuts=gmins(n,E)
            for s in cuts[:2]: chk("fan%s"%sizes,n,adj,s,acc)
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("census N=%d done tot=%d viol=%d"%(nn,acc['tot'],acc['viol']),flush=True)
    print("\nMAX-T GATE:  max_v T(v) <= N + N^2/25 - m ?  tot=%d viol=%d  %s"%(acc['tot'],acc['viol'],acc['fv'] or ''))
    mm=acc['minm']
    print("  min margin (A-maxT) = %s = %.4f @ %s N=%d m=%d  maxT=%s A=%s"%(str(mm[0]),float(mm[0]),mm[1],mm[2],mm[3],mm[4],mm[5]))
