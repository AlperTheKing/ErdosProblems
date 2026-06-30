"""Per-edge excess Phi_f = sum_v p_f(v) T(v) - N*L_f.   S = sum_f L_f Phi_f.
SUM-SBC <=> S <= (N^2/25 - m)*Gamma.   PATH-LRS(avg) <=> Phi_f <= L_f*(N^2/25-m) for each f.
Question: is there an instance where some Phi_f > L_f*(N^2/25-m) (per-edge FAILS) but aggregate S<=... still holds?
If yes -> SUM-SBC is strictly easier than per-edge PATH-LRS, and aggregation is the lever.
EXACT. Battery: census N<=11 (all gmin cuts), two-lane, blowups, fans, Mycielskians."""
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

def pf_of(M,cyc):
    pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    return pf

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; m=len(M); Gamma=sum(ell[f]**2 for f in M); slack=F(N*N,25)-m
    pf=pf_of(M,cyc)
    S=F(0); peredge_fail=0; worst_phi_ratio=None
    for f in M:
        Lf=ell[f]
        phi=sum(pf[f].get(v,F(0))*T[v] for v in pf[f]) - N*Lf
        S+=Lf*phi
        # per-edge PATH-LRS bound
        if phi> Lf*slack: peredge_fail+=1
        r=phi/(Lf*slack) if slack>0 else None
        if r is not None and (worst_phi_ratio is None or r>worst_phi_ratio): worst_phi_ratio=r
    RHS=slack*Gamma
    sumsbc = S<=RHS
    acc['tot']+=1
    if not sumsbc: acc['sumfail']+=1; acc['sumwit']=acc['sumwit'] or (name,n,m,str(S),str(RHS))
    if peredge_fail>0:
        acc['peredge_fail_inst']+=1
        # record if aggregate still holds despite per-edge fail
        if sumsbc:
            acc['easier']+=1
            if acc['easierwit'] is None:
                acc['easierwit']=(name,n,m,peredge_fail,float(worst_phi_ratio) if worst_phi_ratio else None,str(S),str(RHS))
    if acc['minsumslack'] is None or (RHS-S)<acc['minsumslack'][0]:
        acc['minsumslack']=(RHS-S,name,n,m)

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
    acc=dict(tot=0,sumfail=0,sumwit=None,peredge_fail_inst=0,easier=0,easierwit=None,minsumslack=None)
    for L in (8,12,16,20,24):
        n,E,side=build_two_lane(L); chk("twolane%d"%L,n,adj_of(n,E),side,acc)
    for cyc in (5,7,9):
        for t in range(1,5):
            n,E=blowup([t]*cyc)
            if n>24: continue
            adj,cuts=gmins(n,E)
            for s in cuts[:2]: chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for sizes in [[3,9,1,9,3],[2,10,1,10,2],[1,9,3,9,1],[9,1,9,1,9],[2,1,2,1,2],[3,1,3,1,3]]:
        n,E=blowup(sizes)
        if n<=24:
            adj,cuts=gmins(n,E)
            for s in cuts[:2]: chk("fan%s"%sizes,n,adj,s,acc)
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("census N=%d done tot=%d sumfail=%d peredge_fail_inst=%d easier=%d"%(nn,acc['tot'],acc['sumfail'],acc['peredge_fail_inst'],acc['easier']),flush=True)
    print("\nSUM-SBC total instances=%d  SUM-SBC failures=%d  %s"%(acc['tot'],acc['sumfail'],acc['sumwit'] or ''))
    print("per-edge PATH-LRS(avg) failing instances=%d ; of those aggregate STILL holds (easier!)=%d"%(acc['peredge_fail_inst'],acc['easier']))
    print("  easier witness:",acc['easierwit'])
    ms=acc['minsumslack']
    print("  min SUM-SBC slack (RHS-S) = %s = %.3f @ %s N=%d m=%d"%(str(ms[0]),float(ms[0]),ms[1],ms[2],ms[3]))
