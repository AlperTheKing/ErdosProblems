"""SOS-angle probe 2: find maximal SOS coefficient c with
   delta*L^2 + c*sum_i(h_i-m)^2 + E_0 <= (L/5)(N^2-Gamma)   (m=S/L),
and check whether dropping E_0 keeps it (decoupling test), and the
DEVIATION-NORMALIZED form  (relative to deficit)."""
import subprocess
from fractions import Fraction as F
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def rows_iter(fams):
    for (n,E) in fams:
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        try: _,cuts=gmins(n,E)
        except Exception: continue
        for side in cuts:
            st=struct_for_side(n,adj,side)
            if st is None: continue
            M,ell,T,mu,cyc=st
            N=F(n); Gamma=sum(T)
            for f in M:
                L=ell[f]
                if L%2==0: continue
                for P in cyc[f]:
                    if len(P)!=L: continue
                    h=[T[P[i]]/N for i in range(L)]
                    S=sum(h)
                    prods=[h[i]*h[(i+1)%L] for i in range(L)]
                    q=min(prods)
                    delta=(S/L)**2 - q
                    chiP=[0]*n
                    for end in (P[0],P[-1]):
                        ch=endpt_chi(n,adj,side,end,M,n)
                        for rr in range(n): chiP[rr]+=ch[rr]
                    E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
                    yield dict(n=n,N=N,L=L,Gamma=Gamma,h=h,S=S,delta=delta,E0=E0)

def build_fams():
    fams=[]
    fams.append(dec("H?AFBo]"))
    for nn in range(5,10):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            fams.append(dec(g6))
    for sizes in [(2,2,2,2,2),(3,3,3,3,3),(2,1,2,1,2),(3,2,3,2,3),(2,1,2,1,3),(4,1,4,1,4),(5,1,5,1,5),(1,3,1,3,1)]:
        fams.append(odd_blowup(5,list(sizes)))
    return fams

def main():
    fams=build_fams()
    # maximal c (over rows where SOS>0 and there is room) such that
    #   delta*L^2 + c*SOS + E_0 <= R := (L/5)(N^2-Gamma)
    #   => c <= (R - E_0 - delta*L^2)/SOS  =: cmax_row  (only when SOS>0)
    cmax=None; cmax_row=None
    nE0neg=0; tot=0
    # decoupling-without-E0: does delta*L^2 + SOS <= R hold when E0>=0? when E0<0?
    fail_noE0=0; worst_noE0=None
    for row in rows_iter(fams):
        tot+=1
        L=row['L']; N=row['N']; Gamma=row['Gamma']; E0=row['E0']; delta=row['delta']
        h=row['h']; S=row['S']; m=S/L
        R=F(L,5)*(N*N-Gamma)
        SOS=sum((hi-m)**2 for hi in h)
        if E0<0: nE0neg+=1
        room=R-E0-delta*L*L
        if SOS>0:
            crow=room/SOS
            if cmax is None or crow<cmax:
                cmax=crow; cmax_row=(row['n'],L,str(E0),str(delta*L*L),str(R),str(SOS),str(crow))
        # certificate WITHOUT E0 (pure SOS, no endpoint): delta*L^2 + SOS <= R ?
        lhs=delta*L*L+SOS
        if lhs>R:
            fail_noE0+=1
            ratio=lhs/R if R>0 else None
            if worst_noE0 is None or (ratio is not None and ratio>worst_noE0[0]):
                worst_noE0=(ratio,row['n'],L,str(E0),str(lhs),str(R))
    print("rows=%d  rows with E0<0: %d"%(tot,nE0neg))
    print("maximal SOS coeff c (delta*L^2 + c*SOS + E0 <= R on ALL rows): cmax=%s ~%.4f"%(cmax,float(cmax)))
    print("   binding row (n,L,E0,deltaL2,R,SOS,c):",cmax_row)
    print("WITHOUT E0 (pure SOS cert delta*L^2+SOS<=R): violations=%d"%fail_noE0)
    if worst_noE0: print("   worst no-E0 violation ratio=%.5f n=%s L=%s E0=%s lhs=%s R=%s"%(float(worst_noE0[0]),worst_noE0[1],worst_noE0[2],worst_noE0[3],worst_noE0[4],worst_noE0[5]))

if __name__=="__main__":
    main()
