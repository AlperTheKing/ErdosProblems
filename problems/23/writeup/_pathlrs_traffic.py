"""Verify Codex's blue-edge-traffic reformulation of PATH-LRS(c1) and profile the terms for cap-hunting.
Handshake: sum_{e in B incident v} mu(e) = 2 T(v) - iota(v), iota(v)=sum_{g bad, v endpoint} ell[g].
For path P (Pset=set(P)):  I=sum_{e in B both-in-P} mu(e); D=sum_{e in B one-in-P} mu(e); J=sum_{v in P} iota(v).
Identity: sum_{v in P} T(v) = (2I+D+J)/2.   PATH-LRS <=> 2I+D+J <= 2 L A, A=N+N^2/25-m.
Verify identity (must be EXACT 0 mismatch) + PATH-LRS, dump (I,D,J,2LA) at min margin to expose binding term."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _verify_two_lane import build_two_lane

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); A=F(n)+F(n*n,25)-m
    iota=[F(0)]*n
    for g in M:
        iota[g[0]]+=ell[g]; iota[g[1]]+=ell[g]
    Bedges=[e for e in mu]  # mu keyed on cut (B) edges
    for f in M:
        Lf=ell[f]
        for P in cyc[f]:
            Pset=set(P)
            I=F(0); D=F(0)
            for e in Bedges:
                u,v=e; a=u in Pset; b=v in Pset
                if a and b: I+=mu[e]
                elif a or b: D+=mu[e]
            J=sum(iota[v] for v in Pset)
            lhs=sum(T[v] for v in P)
            rhs_id=(2*I+D+J)/2
            acc['paths']+=1
            if lhs!=rhs_id:
                acc['idmis']+=1
                if acc['fid'] is None: acc['fid']=(name,n,str(f),str(lhs),str(rhs_id))
            # PATH-LRS as 2I+D+J <= 2LA
            margin=2*Lf*A-(2*I+D+J)
            if margin<0:
                acc['viol']+=1
                if acc['fviol'] is None: acc['fviol']=(name,n,str(f))
            if margin<acc['minm'][0]:
                acc['minm']=(margin,name,n,m,Lf,str(I),str(D),str(J),str(2*Lf*A),str(lhs))

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

if __name__=="__main__":
    acc=dict(paths=0,idmis=0,viol=0,fid=None,fviol=None,minm=(F(10**9),'',0,0,0,'','','','',''))
    for L in (8,12,16):
        n,E,side,bad=build_two_lane(L); chk("twolane%d"%L,n,adj_of(n,E),side,acc)
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4],[3,9,1,9,3]):
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: chk("C5%s"%parts,n,adj,s,acc)
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (paths=%d idmis=%d viol=%d)"%(nn,acc['paths'],acc['idmis'],acc['viol']),flush=True)
    print("\n  IDENTITY sum_P T = (2I+D+J)/2: mismatches=%d %s"%(acc['idmis'],acc['fid'] or ''),flush=True)
    print("  PATH-LRS 2I+D+J <= 2LA: violations=%d %s"%(acc['viol'],acc['fviol'] or ''),flush=True)
    mm=acc['minm']
    print("  MIN margin=%s @ %s N=%d m=%d L=%d : I=%s D=%s J=%s 2LA=%s sumT=%s"%(
        str(mm[0]),mm[1],mm[2],mm[3],mm[4],mm[5],mm[6],mm[7],mm[8],mm[9]),flush=True)
    print("  === traffic reformulation %s ==="%("VERIFIED (identity exact, PATH-LRS holds)" if acc['idmis']==0 and acc['viol']==0 else "PROBLEM"),flush=True)
