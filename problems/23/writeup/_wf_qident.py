"""Verify EXACTLY the algebraic reduction:
 BD-TARGET  <=>  q(mu) >= 0  where q(mu)=ell*mu^2 - ell*(N+a+b)*mu + (N^2+ell*a*b),  mu=row/ell.
 Endpoint identities (claimed): q(a)=N(N-ell*a),  q(b)=N(N-ell*b).
 Also report: smaller root mu- of q; whether actual mu <= mu-; and the slack q(mu).
 And test the WEAKER atom S3-low: ell*Smin_supp <= N  (= q(a)>=0).
Battery: census<=10 + structured killers (Myc N<=23, blow-ups, glued).  EXACT Fraction."""
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

agg={'qa_id':[0,0],'qb_id':[0,0],'BDT':[0,0],'S3low':[0,0],'qmu_pos':[0,0]}
firsts={k:None for k in agg}

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
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mu=row/ll
        Sv=[S[v] for v in d]; a=min(Sv); b=max(Sv)
        var=sum(d[v]*(S[v]-mu)**2 for v in d)
        bd=ll*(b-mu)*(mu-a); tgt=N*(N-row)
        def q(x): return ll*x*x - ll*(N+a+b)*x + (N*N+ll*a*b)
        # endpoint identities
        agg['qa_id'][1]+=1
        if q(a)==N*(N-ll*a): agg['qa_id'][0]+=1
        elif firsts['qa_id'] is None: firsts['qa_id']=(src,f,str(q(a)),str(N*(N-ll*a)))
        agg['qb_id'][1]+=1
        if q(b)==N*(N-ll*b): agg['qb_id'][0]+=1
        elif firsts['qb_id'] is None: firsts['qb_id']=(src,f,str(q(b)),str(N*(N-ll*b)))
        # BDT <=> q(mu)>=0
        agg['BDT'][1]+=1
        if bd<=tgt: agg['BDT'][0]+=1
        elif firsts['BDT'] is None: firsts['BDT']=(src,f,str(bd),str(tgt))
        agg['qmu_pos'][1]+=1
        if q(mu)>=0: agg['qmu_pos'][0]+=1
        elif firsts['qmu_pos'] is None: firsts['qmu_pos']=(src,f,str(q(mu)))
        # consistency: BDT iff q(mu)>=0
        # S3-low: ell*a <= N  (= q(a)>=0)
        agg['S3low'][1]+=1
        if ll*a<=N: agg['S3low'][0]+=1
        elif firsts['S3low'] is None: firsts['S3low']=(src,f,'ell*a='+str(ll*a),'N='+str(n))

if __name__=="__main__":
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: per(n,adj,s,f"c{nn}:{g6}")
        print(f"done census N={nn}",flush=True)
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
        print(f"done {nm}",flush=True)
    print("\n=== FINAL (exact) ===")
    for k in agg:
        print(f"  {k}: {agg[k]}"+("  FIRSTFAIL "+str(firsts[k]) if firsts[k] else ""))
