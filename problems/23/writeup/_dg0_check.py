"""Decisive check: are the NEAR-EXTREMAL small-B_L rows (the hard regime) ones where
   DG(x0)+DG(x_{L-1}) > 0 (endpoint lemma does real work), or DG=0 (lemma circular there)?
   If every row with small B_L has DG>0, the DG=0 rows are bounded away from B_L=0 (easy),
   and the endpoint lemma is a genuine reduction on the hard rows.
   Report: among DG=0 rows, the minimum B_L (excluding exact pure-cycle B_L=0);
           and the B_L distribution split by DG>0 vs DG=0, on near-extremal blow-ups.
"""
import subprocess
from fractions import Fraction as F
from _wf_deficit_farkas import gamma_of, deltas, flip, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint

def endpoint_dg(n, adj, side, v, Gamma):
    s2 = flip(side, [v])
    if not Bconn(n, adj, s2): return F(0)
    dB, dM = deltas(n, adj, side, {v})
    if dB != dM: return F(0)
    g1 = gamma_of(n, adj, s2)
    return F(0) if g1 is None else g1 - Gamma

def rows_for(name,n,E):
    adj,cuts=gmins(n,E); out=[]
    for side in cuts:
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st; N=F(n); Gamma=sum(T)
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                x=P
                h=[T[x[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
                C_L=S*S-(L*L)*q
                B_L=L*(N*N-Gamma)-25*sum(T[x[i]]-N for i in range(L))-C_L
                DG0=endpoint_dg(n,adj,side,x[0],Gamma); DGL=endpoint_dg(n,adj,side,x[-1],Gamma)
                out.append((B_L, DG0+DGL, name, L, tuple(x)))
    return out

def main():
    fams=[]
    # census + near-extremal blow-ups (perturbations of C5[t])
    for nn in range(5,10):
        for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fams.append(("cen%d"%nn,n,E))
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,3),(2,2,2,1,2)]:
        if sum(sizes)<=12:
            n,E=odd_blowup(5,list(sizes)); fams.append(("C5%s"%(sizes,),n,E))
    allrows=[]
    for (name,n,E) in fams: allrows+=rows_for(name,n,E)
    dg0=[r for r in allrows if r[1]==0]
    dgp=[r for r in allrows if r[1]>0]
    dg0_nz=[r for r in dg0 if r[0]>0]
    print("total rows:",len(allrows)," DG=0:",len(dg0)," DG>0:",len(dgp))
    print("DG=0 rows with B_L=0 (pure extremal):", sum(1 for r in dg0 if r[0]==0))
    if dg0_nz:
        m=min(dg0_nz,key=lambda r:r[0])
        print("MIN B_L over DG=0 nonzero rows:",str(m[0]),float(m[0])," at",m[2],"L=",m[3],m[4])
    # smallest B_L overall, and whether DG>0 there
    allnz=[r for r in allrows if r[0]>0]
    allnz.sort(key=lambda r:r[0])
    print("\nsmallest-B_L nonzero rows (B_L | DGsum | where):")
    for r in allnz[:15]:
        tag = "DG>0" if r[1]>0 else "DG=0 <-- circular here"
        print("  B_L=%s (%.4f) DGsum=%s  %s  %s L=%d" % (str(r[0]),float(r[0]),str(r[1]),tag,r[2],r[3]))

if __name__=="__main__":
    main()
