"""Stress Codex FULL-LOW-INTERNAL-LOAD (sum_{v in H}T(v) <= N*|H| on full-low bands 2b<=N) on ALL MAXIMUM cuts
(not just Gamma-min), census N=7..11, brute force. A single NON-Gamma-min max-cut violation => minimality still
required; otherwise likely min-free. Reports violations split by (gamma-min vs ordinary max cut). EXACT Fraction."""
import subprocess
from itertools import product
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side

def maxcuts(n,E):
    best=-1; cuts=[]
    for bits in product((0,1),repeat=n-1):
        side=(0,)+bits
        c=0
        for (u,v) in E:
            if side[u]!=side[v]: c+=1
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return best,cuts

def fli_check(n,adj,side):
    st=struct_for_side(n,adj,list(side))
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    Gamma=sum(ell[f]**2 for f in M)
    levs=[F(0)]+sorted(set(v for v in T if v>0))
    worst=None
    for j in range(len(levs)-1):
        a=levs[j]; b=levs[j+1]
        if 2*b>n: continue
        H=[v for v in range(n) if T[v]>a]
        if not H: continue
        h=len(H); TH=sum(T[v] for v in H)
        m=F(n)*h-TH
        if worst is None or m<worst[0]: worst=(m,a,b,h)
    return (Gamma,worst)

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    vmin=0; vnonmin=0; first=None; ngraph=0; rows=0
    gmar=F(10**18)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0m=vmin; v0n=vnonmin
        for g6 in outg:
            n,E=dec(g6); adj=adj_of(n,E)
            mc,cuts=maxcuts(n,E)
            data=[]
            for side in cuts:
                if not Bconn(n,adj,side): continue
                r=fli_check(n,adj,side)
                if r is None or r[1] is None: continue
                data.append((r[0],r[1],side))   # (Gamma, worst=(margin,a,b,h), side)
            if not data: continue
            ngraph+=1
            gminG=min(d[0] for d in data)
            for (G,worst,side) in data:
                rows+=1
                mar=worst[0]
                if mar<gmar: gmar=mar
                if mar<0:
                    if G==gminG: vmin+=1
                    else: vnonmin+=1
                    if first is None: first=(g6,n,float(mar),G,gminG,(G==gminG))
        print("  census N=%d done: graphs=%d rows=%d vmin+%d vnonmin+%d (min margin %s)"%(nn,ngraph,rows,vmin-v0m,vnonmin-v0n,gmar),flush=True)
        if first: break
    print("\n  FULL-LOW-INTERNAL-LOAD over ALL maximum cuts: gamma-min violations=%d, ordinary-max violations=%d"%(vmin,vnonmin),flush=True)
    print("  global min margin = %s ~ %.4f"%(gmar,float(gmar)),flush=True)
    if first: print("  first violation: %s"%(first,),flush=True)
    print("  => %s"%("MIN-FREE likely: holds on ALL maximum cuts (no non-min violation)" if (vmin+vnonmin)==0
        else ("MINIMALITY REQUIRED: a non-min max cut violates" if vnonmin else "gamma-min cut itself violates?!")),flush=True)
