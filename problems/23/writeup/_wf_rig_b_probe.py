"""Probe: measure slack structure for route (b) SOS on a few configs."""
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

def report(name,parts):
    n,E=blowup(parts)
    adj,cuts=gmins(n,E); side=cuts[0]
    st=struct_for_side(n,adj,side)
    if st is None:
        print(name,"NO struct"); return
    M,ell,T,mu,cyc=st
    N=n; m=len(M); Gamma=sum(ell[f]**2 for f in M)
    sumTTN=sum(t*(t-N) for t in T)
    badset=set((min(a,b),max(a,b)) for a,b in M)
    tvcut=F(0); tvbad=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                d=abs(T[u]-T[v])
                if side[u]!=side[v]: tvcut+=d
                else: tvbad+=d
    S=Gamma*(F(N*N,25)-m)-sumTTN-F(N,5)*(tvcut-tvbad)
    print("%s: N=%d beta=%d Gamma=%s"%(name,N,m,Gamma))
    print("  T=",[str(t) for t in T])
    print("  sumT=%s (=Gamma? %s)"%(sum(T), sum(T)==Gamma))
    print("  sumT(T-N)=%s tvcut=%s tvbad=%s"%(sumTTN,tvcut,tvbad))
    print("  SLACK S=%s = %f"%(S,float(S)))

if __name__=="__main__":
    report("C5[1]",[1,1,1,1,1])
    report("C5[2]",[2,2,2,2,2])
    report("C5[3]",[3,3,3,3,3])
    report("nu[2,2,2,2,3]",[2,2,2,2,3])
    report("nu[1,5,2,2,5]",[1,5,2,2,5])
    report("C7[1]",[1,1,1,1,1,1,1])
