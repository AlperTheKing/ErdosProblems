"""Is the binding case for rho(K)<=N (max K-row-sum) always a UNIQUE-path bad edge?
rowsum(f)=sum_v p_f(v)S(v). For unique f, rowsum=UPO=sum_{v in P}S(v). For multi-geo f, rowsum=avg UPO_j.
Over gamma-min cuts, compute max rowsum/N over UNIQUE f vs MULTI f; report which achieves overall max and
the gap. If unique-path always binds (multi strictly slack), the unique-path proof (Part A+B) closes
rho(K)<=N and the multi-geo half is a soft corollary. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def check_cut(n,adj,s,name,acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        k=len(cyc[g])
        for P in cyc[g]:
            for v in P: S[v]+=F(1,k)
    N=n
    for f in M:
        k=len(cyc[f])
        rowsum=sum( (F(1,k)*sum(1 for P in cyc[f] if v in P))*S[v] for v in range(n) )
        r=rowsum/N
        if k==1:
            if r>acc['umax'][0]: acc['umax']=(r,N,name,f)
        else:
            if r>acc['mmax'][0]: acc['mmax']=(r,N,name,f)
        if r>acc['omax'][0]: acc['omax']=(r,N,name,f,'unique' if k==1 else 'multi')

def run():
    acc={'umax':(F(-1),0,'',None),'mmax':(F(-1),0,'',None),'omax':(F(-1),0,'',None,'')}
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check_cut(n,adj,s,g6,acc)
        print(f"  ...through N={nn}: unique-max/N={float(acc['umax'][0]):.4f}  multi-max/N={float(acc['mmax'][0]):.4f}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
                        ("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),("Grotzsch",grot),("Myc(Grotzsch)",mycg)]:
        adj,cuts=gmins(nn,E)
        for s in cuts: check_cut(nn,adj,s,name,acc)
    print(f"\n  UNIQUE-path max rowsum/N = {float(acc['umax'][0]):.4f} at {acc['umax'][2]} f={acc['umax'][3]} (N={acc['umax'][1]})",flush=True)
    print(f"  MULTI-geo  max rowsum/N = {float(acc['mmax'][0]):.4f} at {acc['mmax'][2]} f={acc['mmax'][3]} (N={acc['mmax'][1]})",flush=True)
    print(f"  OVERALL    max rowsum/N = {float(acc['omax'][0]):.4f} achieved by {acc['omax'][4]} f at {acc['omax'][2]}",flush=True)
    print(f"  === {'BINDING CASE = UNIQUE-path (multi strictly slack): unique-path proof closes rho(K)<=N' if acc['omax'][4]=='unique' else 'multi-geo can bind: variance argument needed'} ===",flush=True)

if __name__=="__main__": run()
