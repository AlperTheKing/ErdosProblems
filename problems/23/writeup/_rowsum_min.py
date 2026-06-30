"""VERIFY GPT-Pro claim: ROWSUM-O (max_f sum_g O_fg <= N, p_f=fraction, O_fg=<p_f,p_g>) requires GAMMA-MINIMALITY.
Enumerate ALL maximum cuts (brute force, N<=9) of triangle-free census graphs; for each B-connected maximum cut
compute Gamma and the ROWSUM-O max row sum. Look for a MAXIMUM (necessarily non-Gamma-min) cut with rowsum>N
while the Gamma-min cut has rowsum<=N. If found => GPT is right: minimality is essential, minimality-blind
proofs are dead. EXACT Fraction."""
import subprocess
from itertools import product
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side

def maxcut_all(n,E,adj):
    # brute force all 2-colorings (fix v0=0); return (maxcut_value, list of sides achieving it)
    best=-1; cuts=[]
    for bits in product((0,1),repeat=n-1):
        side=[0]+list(bits)
        c=sum(1 for (u,v) in E if side[u]!=side[v])
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return best,cuts

def rowsum_max(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    Mlist=list(M)
    pf=[]
    for f in Mlist:
        Ps=cyc[f]; cf=len(Ps)
        col=[F(sum(1 for P in Ps if v in P),cf) for v in range(n)]
        pf.append(col)
    Gamma=sum(ell[f]**2 for f in M)
    # row sum_f = sum_g sum_v pf[f][v]*pf[g][v] = sum_v pf[f][v]*S(v), S(v)=sum_g pf[g][v]
    S=[sum(pf[g][v] for g in range(len(Mlist))) for v in range(n)]
    rmax=F(-1)
    for fi in range(len(Mlist)):
        rs=sum(pf[fi][v]*S[v] for v in range(n))
        if rs>rmax: rmax=rs
    return Gamma,rmax

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    found=[]
    nchk=0
    for nn in range(5,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj=adj_of(n,E)
            mc,cuts=maxcut_all(n,E,adj)
            # for each maximum cut that is B-connected with bad edges, get (Gamma, rowsum)
            data=[]
            for side in cuts:
                if not Bconn(n,adj,side): continue
                r=rowsum_max(n,adj,side)
                if r is None: continue
                data.append((r[0],r[1],side))   # (Gamma, rowsum, side)
            if not data: continue
            nchk+=1
            gmin=min(d[0] for d in data)
            # rowsum on gamma-min cuts
            gmin_rs_ok=all(d[1]<=n for d in data if d[0]==gmin)
            # any maximum cut violating rowsum<=N?
            viol=[d for d in data if d[1]>n]
            if viol:
                v=viol[0]
                found.append((g6,n,mc,float(v[0]),gmin,float(v[1]),gmin_rs_ok))
                if len(found)<=5:
                    print("  VIOL g6=%s N=%d maxcut=%d : a MAX cut has Gamma=%s rowsum=%s>%d ; Gamma_min=%s ; gmin-cuts-ok=%s"%(
                        g6,n,mc,v[0],v[1],n,gmin,gmin_rs_ok),flush=True)
        print("  census N=%d done (graphs-with-data=%d, rowsum-violating-maxcuts found so far=%d)"%(nn,nchk,len(found)),flush=True)
    print("\n  TOTAL graphs with a MAXIMUM cut violating ROWSUM-O (rowsum>N) = %d"%len(found),flush=True)
    allgminok=all(f[6] for f in found) if found else True
    print("  On EVERY such graph, the Gamma-min cut(s) still satisfy ROWSUM-O: %s"%allgminok,flush=True)
    print("  => %s"%("CONFIRMS GPT: ROWSUM-O needs Gamma-minimality (non-min max cuts violate); minimality-blind proofs DEAD"
        if found and allgminok else
        ("NO max-cut violation found (ROWSUM-O holds for ALL maximum cuts?!)" if not found else
         "MIXED: some gamma-min cut also violates -- investigate")),flush=True)
