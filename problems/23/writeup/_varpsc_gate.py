"""EXACT variational PSC-50 gate (Codex block 228) -- avoids algebraic eigenvectors via ARBITRARY RATIONAL x.
For rational x over bad edges: phi(v)=sum_f x_f p_f(v), L=sum_v phi^2 = x^T O x, and the claim (for ALL x):
  Q(x) := L^2 - (N+N^2/25-|M|)*L + (N/50)*D <= 0,   D = sum_B |phi_u^2-phi_v^2| - sum_M |phi_u^2-phi_v^2|.
(Equivalent to L+|M|+Xi_x/50<=N+N^2/25 after dividing by L>0; Xi_x=TV_B(h)-TV_M(h), h=N phi^2/L.)
Choosing x=Perron recovers PSC-50 => SBC => Erdos. EXACT Fraction. Adversarial x: basis e_f, all-ones, random
small-int, and a NEAR-PERRON rational (rounded float Perron, where L is maximal = the binding direction).
Battery: census gamma-min N<=11 + two-lane + k-lane breakers + C5[t] + Mycielskians. Report min margin=-Q + any
Q>0 (violation) with the x."""
import subprocess, random
import numpy as np
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane, Ogram
from _wf_lrsbreak_0 import build_k_lane, cutsize
from _wf_lrsbreak_0c import greedy_chords

random.seed(20260629)

def Qval(n,adj,side,M,ell,O,pf,x,Nq):
    # SCALE-INVARIANT normalized form (Codex block 229): lambda_x = ||Px||^2/||x||^2 (Rayleigh),
    # h(v)=N*phi(v)^2/L with L=||phi||^2 (scale-invariant), Xi_x=TV_B(h)-TV_M(h).
    # margin = N + N^2/25 - |M| - lambda_x - Xi_x/50 ; violation if margin<0.
    phi=[F(0)]*n
    for gi,f in enumerate(M):
        if x[gi]==0: continue
        for v,pv in pf[f].items(): phi[v]+=x[gi]*pv
    L=sum(p*p for p in phi)
    if L==0: return None
    norm2=sum(c*c for c in x)
    lam_x=L/norm2
    h=[F(n)*phi[v]*phi[v]/L for v in range(n)]
    Xi=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                d=abs(h[u]-h[v])
                if side[u]!=side[v]: Xi+=d
                else: Xi-=d
    m=len(M)
    margin=F(n)+Nq-m-lam_x-Xi/F(50)
    return -margin, lam_x   # return Q=-margin so existing (Q>0 => violation) logic still works

def check(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    res=Ogram(n,adj,side)
    if res is None: return
    M,ell,O=res; m=len(M)
    if m==0: return
    st=struct_for_side(n,adj,side); _M,_e,T,_mu,cyc=st
    pf={}
    for f in M:
        k=len(cyc[f]); d={}
        for P in cyc[f]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[f]=d
    Nq=F(n*n,25)
    xs=[]
    xs.append([F(1)]*m)                                  # all-ones
    for i in range(m): xs.append([F(1) if j==i else F(0) for j in range(m)])  # basis
    for _ in range(8): xs.append([F(random.randint(0,4)) for _ in range(m)])  # random small-int
    # near-Perron rational (round float Perron to /60)
    Of=np.array([[float(x) for x in r] for r in O]); w,V=np.linalg.eigh(Of)
    xp=V[:,-1];
    if xp.sum()<0: xp=-xp
    xs.append([F(int(round(float(c)*60)),60) for c in xp])
    xs.append([F(int(round(float(c)*600)),600) for c in xp])
    for x in xs:
        if all(c==0 for c in x): continue
        r=Qval(n,adj,side,M,ell,O,pf,x,Nq)
        if r is None: continue
        Q,L=r
        margin=-Q
        acc['n']+=1
        if margin<acc['min'][0]: acc['min']=(margin,name,n,m,str(L))
        if Q>0:
            acc['viol']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,m,[str(c) for c in x],str(Q))

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
    acc={'n':0,'viol':0,'first':None,'min':(F(10**18),'','','','')}
    print("=== EXACT variational PSC-50 gate (rational x): Q(x) <= 0 for all x ===",flush=True)
    for L in (8,12,16,20):
        n,E,side,_=build_two_lane(L); check("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); check("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane + k-lane done (min margin=%s, viol=%d)"%(float(acc['min'][0]),acc['viol']),flush=True)
    for cyc in (5,7,9):
        for t in range(1,5):
            n,E=blowup([t]*cyc); adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): check("C%d[%d]"%(cyc,t),n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:1]: check(name,nn,adj,s,acc)
    print("  blow-ups + Mycielskians done (min margin=%s, viol=%d)"%(float(acc['min'][0]),acc['viol']),flush=True)
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (viol+%d)"%(nn,acc['viol']-v0),flush=True)
    print("\n  total (graph,cut,x) evals=%d  variational-PSC-50 VIOLATIONS (Q>0)=%d"%(acc['n'],acc['viol']),flush=True)
    print("  MIN margin (-Q) = %s at %s"%(float(acc['min'][0]),acc['min'][1:]),flush=True)
    if acc['first']: print("  first violation: %s"%(acc['first'],),flush=True)
    print("  === variational PSC-50 %s ==="%("VIOLATED by a rational x (return to Codex)" if acc['viol'] else "HOLDS exactly for all tested rational x (basis/all-ones/random/near-Perron) on full battery"),flush=True)
