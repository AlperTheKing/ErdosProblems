"""Test the DISCRIMINANT condition (sufficient for BD-TARGET for ALL mu):
   DISC:  ell*(N+a+b)^2 <= 4*(N^2 + ell*a*b)   [<=> q(mu)>=0 for every mu, i.e. min_mu q >=0]
If DISC holds on the battery it's a clean mu-free sufficient lemma. Also test variants:
   D2: ell*(b-a)^2 <= 4*(N-ell*b)*(? ) ... derive: q min = N^2+ell ab - ell(N+a+b)^2/4.
       4*qmin/... ; equivalently (N - ell*b)(N-ell*a) >= ell*(b-a)^2/4? check that identity.
   Indeed q(a)q(b)... no. Let's just test DISC and D3: (N-ell a)+(N-ell b) >= ...
EXACT. Battery: census<=10 + killers (Myc N<=23, blow-ups, glued)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for x in range(off[i],off[i+1]):
            for y in range(off[j],off[j+1]): EE.append((min(x,y),max(x,y)))
    return nn,EE
def bridge(b1,b2,u,v):
    n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]

agg={'DISC':[0,0],'D2_prodform':[0,0]}; firsts={k:None for k in agg}
def per(n,adj,s,src):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu_,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    N=F(n)
    for f in M:
        if len(cyc[f])<2: continue
        d=pf[f]; ll=sum(d.values()); Sv=[S[v] for v in d]; a=min(Sv); b=max(Sv)
        # DISC: ell*(N+a+b)^2 <= 4(N^2+ell ab)
        agg['DISC'][1]+=1
        if ll*(N+a+b)**2 <= 4*(N*N+ll*a*b): agg['DISC'][0]+=1
        elif firsts['DISC'] is None: firsts['DISC']=(src,f,'ell='+str(ll),'a='+str(a),'b='+str(b),'N='+str(n),
                                                     'lhs='+str(ll*(N+a+b)**2),'rhs='+str(4*(N*N+ll*a*b)))
        # D2 product form: (N-ell a)(N-ell b) >= ell^2 (b-a)^2/4 ? (equivalent to DISC? check)
        agg['D2_prodform'][1]+=1
        if (N-ll*a)*(N-ll*b) >= ll*ll*(b-a)**2/4: agg['D2_prodform'][0]+=1
        elif firsts['D2_prodform'] is None: firsts['D2_prodform']=(src,f,'(N-ella)(N-ellb)='+str((N-ll*a)*(N-ll*b)),'rhs='+str(ll*ll*(b-a)**2/4))

if __name__=="__main__":
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: per(n,adj,s,f"c{nn}:{g6}")
        print(f"done census N={nn}: DISC={agg['DISC']}",flush=True)
    extra=[('C5[2]',)+blowup([2,2,2,2,2]),('C5[3]',)+blowup([3,3,3,3,3]),
           ('C5[4]',)+blowup([4,4,4,4,4]),('C5unbal',)+blowup([1,5,2,2,5]),
           ('C5[1,6,2,2,6]',)+blowup([1,6,2,2,6]),
           ('M(C9)',)+mycielski(9,Cn(9)),('M(C11)',)+mycielski(11,Cn(11)),
           ('Grot11',)+mycielski(5,Cn(5)),
           ('C7brgGrot',)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ('M(Grot)23',)+mycielski(*mycielski(5,Cn(5)))]
    for nm,n,E in extra:
        adj,cuts=gmins(n,E)
        for s in cuts: per(n,adj,s,nm)
        print(f"done {nm}: DISC={agg['DISC']} first={firsts['DISC']}",flush=True)
    print("\n=== FINAL ===")
    for k in agg: print(f"  {k}: {agg[k]}"+("  FIRSTFAIL "+str(firsts[k]) if firsts[k] else ""))
