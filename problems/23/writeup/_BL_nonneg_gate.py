"""Test whether the crux ATOM B_L >= 0 holds STANDALONE (without the E0 RHS), i.e.
   (BL0)   L*(N^2 - Gamma) - 25*sum_i (T[x_i]-N) - delL2  >=  0,   delL2 = S^2 - L^2 q.
If TRUE everywhere it would prove (A) directly via B_L >= 0 >= ... but the prompt says the
DECOUPLED bound fails, so we EXPECT (BL0) to be FALSE somewhere. Locate the violations and
characterize them: do they all have E0 (admissible neutral endpoint curvature) > 0 covering the
deficit?  i.e. is the ONLY place B_L<0 exactly where E0>0 large?  That pins the coupling.

We dump: B_L, E0adm (neutral+conn endpoint pair curvature, >=0 by gamma-min), and check
   B_L >= E0adm   (lemma A)  AND  separately the sign pattern of B_L.
ALL exact Fraction.
"""
import sys, subprocess
from fractions import Fraction as F
from _wf_deficit_farkas import gamma_of, deltas, flip
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def odd_blowup(m, sizes):
    nn = sum(sizes); start=[0]*m
    for i in range(1,m): start[i]=start[i-1]+sizes[i-1]
    E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(sizes[i]):
            for b in range(sizes[j]): E.append((start[i]+a,start[j]+b))
    return nn,E

def adm_dg(n, adj, side, v, Gamma):
    s2=flip(side,[v])
    if not Bconn(n,adj,s2): return F(0)
    dB,dM=deltas(n,adj,side,{v})
    if dB!=dM: return F(0)
    g1=gamma_of(n,adj,s2)
    if g1 is None: return F(0)
    return g1-Gamma

def rows_for_cut(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return []
    M,ell,T,mu,cyc=st
    N=F(n); Gamma=sum(T); out=[]
    for f in M:
        L=ell[f]
        if L%2==0: continue
        for P in cyc[f]:
            if len(P)!=L: continue
            x=P; Ti=[T[x[i]] for i in range(L)]
            h=[Ti[i]/N for i in range(L)]; S=sum(h)
            q=min(h[i]*h[(i+1)%L] for i in range(L))
            delL2=S*S-(L*L)*q; D=sum(Ti[i]-N for i in range(L))
            B_L=L*(N*N-Gamma)-25*D-delL2
            E0=adm_dg(n,adj,side,x[0],Gamma)+adm_dg(n,adj,side,x[-1],Gamma)
            out.append(dict(N=N,L=L,Gamma=Gamma,B_L=B_L,E0=E0,delL2=delL2,D=D))
    return out

def families():
    fams=[]
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); fams.append(("cen%d-%s"%(nn,g6),n,E))
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(3,2,3,2,3),(2,1,2,1,3)]:
        if sum(sizes)<=12: n,E=odd_blowup(5,list(sizes)); fams.append(("C5%s"%(sizes,),n,E))
    return fams

def main():
    fams=families(); rows=[]
    for (name,n,E) in fams:
        adj,cuts=gmins(n,E)
        for side in cuts:
            for r in rows_for_cut(n,adj,side):
                r['name']=name; rows.append(r)
    print("odd-L rows:", len(rows))
    blneg=[r for r in rows if r['B_L']<0]
    print("B_L < 0 rows (decoupled atom FALSE):", len(blneg))
    # among B_L<0, is E0>0 and B_L>=E0 (so covered)?
    cov=[r for r in blneg if r['B_L']>=r['E0']]
    print("  of those, B_L>=E0 (lemma A holds):", len(cov), " / E0>0:", len([r for r in blneg if r['E0']>0]))
    bad=[r for r in rows if r['B_L']<r['E0']]
    print("Lemma A (B_L>=E0) violations:", len(bad))
    # characterize B_L<0 rows
    blneg.sort(key=lambda r:float(r['B_L']))
    print("\nMOST NEGATIVE B_L (atom violations, where E0 credit is REQUIRED):")
    for r in blneg[:10]:
        print("  %s L=%d N=%s B_L=%s E0=%s delL2=%s D=%s" %
              (r['name'][:18], r['L'], r['N'], r['B_L'], r['E0'], r['delL2'], r['D']))
    # fraction of rows where B_L>=0 already (no credit needed)
    print("\nB_L>=0 rows:", len([r for r in rows if r['B_L']>=0]), "/", len(rows))

if __name__=="__main__":
    main()
