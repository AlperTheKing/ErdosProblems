"""Collatz-Wielandt test-vector comparison for rho(O)<=N. For each battery cut build O (exact, M x M),
O[f,g]=<p_f,p_g>. For candidate positive vectors x indexed by bad edges, compute CW ratio max_f (O x)_f/(N x_f).
x candidates: x=1 (=>ROWSUM-O), x=ell (=>Cycle-SM), x=ell^2, x=1/ell, x=diag O[f,f], x=sqrt(ell).
Smallest max-ratio = tightest cert; most-uniform margin = most provable. Report per-x max ratio over battery + the
per-x MIN ratio (uniformity) and which graph is worst. Include fan + nonuniform fans."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def build_O(n,M,cyc):
    Pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        Pf.append({v:F(c,nf) for v,c in cnt.items()})
    m=len(M); O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(i,m):
            s=F(0)
            di=Pf[i]
            for v,pv in di.items():
                if v in Pf[j]: s+=pv*Pf[j][v]
            O[i][j]=s; O[j][i]=s
    return O,Pf

CANDS=['one','ell','ell2','invell','diag','sqrtell_approx']
def xvec(kind,M,ell,O):
    m=len(M)
    if kind=='one': return [F(1)]*m
    if kind=='ell': return [F(ell[M[i]]) for i in range(m)]
    if kind=='ell2': return [F(ell[M[i]])**2 for i in range(m)]
    if kind=='invell': return [F(1,ell[M[i]]) for i in range(m)]
    if kind=='diag': return [O[i][i] for i in range(m)]
    if kind=='sqrtell_approx':
        # rational approx of sqrt(ell): ell in {5,7,9,...}; use Fraction approx
        import math
        return [F(round(math.sqrt(ell[M[i]])*10000),10000) for i in range(m)]
    return [F(1)]*m

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    O,Pf=build_O(n,M,cyc); m=len(M)
    for kind in CANDS:
        x=xvec(kind,M,ell,O)
        if any(xi<=0 for xi in x): continue
        worst=F(-1)
        for i in range(m):
            Oxi=sum(O[i][j]*x[j] for j in range(m))
            r=Oxi/(F(n)*x[i])
            if r>worst: worst=r
        d=acc[kind]
        if worst>d['max'][0]: d['max']=(worst,name,n)

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]
def fan(sizes):
    nn,E=blowup(list(sizes)); base=nn; sep=[base+k for k in range(5)]
    for k in range(5):
        a=sep[k]; b=sep[(k+1)%5]; E.append((min(a,b),max(a,b)))
    nn+=5; E.append((min(sizes[0]*0+ (sum(sizes[:4])), sep[1]), max(sum(sizes[:4]),sep[1])))
    return nn,sorted(set(E))

if __name__=="__main__":
    acc={k:{'max':(F(-1),'',0)} for k in CANDS}
    # blowups + Mycielskians + glued islands
    for cyc in (5,7,9):
        for t in range(1,5):
            n,E=blowup([t]*cyc)
            if n>24: continue
            adj,cuts=gmins(n,E)
            for s in cuts[:2]: chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    grot=mycielski(5,Cn(5))
    for nm,(nn,E) in [("Grotzsch",grot),("M(C7)",mycielski(7,Cn(7))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    # census N<=9
    for nn in range(5,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done"%nn,flush=True)
    print("\n  Collatz-Wielandt max ratio max_f (Ox)_f/(N x_f) over battery, per test vector x:",flush=True)
    for k in CANDS:
        d=acc[k]['max']
        print("    x=%-14s max ratio = %s = %s  @ %s N=%d   %s"%(k,str(d[0]),str(float(d[0]))[:7],d[1],d[2],
              "<=1 OK (cert valid)" if d[0]<=1 else ">1 (cert INVALID for this x)"),flush=True)
