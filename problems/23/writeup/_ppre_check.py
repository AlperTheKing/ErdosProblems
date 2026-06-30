"""Confirm P_pre>=0 (pre-half c=5 pressure margin) and the identity Net5_j = 5*P_j, on census gmins N<=11."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
def boundary(n,adj,side,H):
    dB=dM=0
    for u in H:
        for v in adj[u]:
            if v in H: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM
viol=0; mn=F(10**18); nb=0; mismatch=0
for nn in range(7,12):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg:
        n,E=dec(g6); adj,cuts=gmins(n,E)
        for side in cuts:
            if not Bconn(n,adj,side): continue
            st=struct_for_side(n,adj,side)
            if st is None: continue
            M,ell,T,mu,cyc=st
            if not M: continue
            m=len(M); eta=F(n*n,25)-m; D=F(n*n)-25*m
            levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
            Ppre=F(0); Net5pre=F(0)
            for j in range(len(levs)-1):
                tj=levs[j]; tn=levs[j+1]; wj=tn-tj
                H=set(v for v in range(n) if T[v]>tj)
                if not H: continue
                h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
                if 2*tj<F(n):
                    Aj=wj*(F(n)+eta-tj-tn)*h
                    Pj=5*Aj-F(n)*wj*sig
                    Net5=wj*(D*h-25*(2*tj+wj-F(n))*h-5*F(n)*sig)
                    Ppre+=Pj; Net5pre+=Net5
            if Net5pre!=5*Ppre: mismatch+=1
            nb+=1
            if Ppre<mn: mn=Ppre
            if Ppre<0: viol+=1
    print("  through N=%d: configs=%d P_pre viol=%d mismatch=%d"%(nn,nb,viol,mismatch),flush=True)
print("P_pre>=0 census gmins N<=11: configs=%d violations=%d min P_pre=%s ; identity Net5=5*P_j mismatches=%d"%(nb,viol,float(mn),mismatch))
