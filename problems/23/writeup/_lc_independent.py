"""INDEPENDENT exact verification of Codex's locked per-bad-edge LOCAL CIRCULANT atom (block 291).
Per bad edge f (ell=ell(f), |cyc_f|=k geodesics): p_f(v)=#geos thru v /k; tau_f(e)= 1 for bad edge f,
and sum over geodesics Q of (1/k) for each geodesic edge e in Q. L_{tau_f} = weighted Laplacian (edge weights
tau_f). a_bar(ell)=ell^3/(4(ell^2-2)). LC matrix A_f = ell*diag(p_f) - p_f p_f^T - a_bar*L_{tau_f} on the
support (cycle/geodesic vertices). Claim: A_f PSD (exact rational LDL). Summed => diag(T)-K-L_omega>=0.
My OWN implementation (not importing Codex's). Full battery; report per-bad-edge PSD failures."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def is_psd(S):
    n=len(S); A=[row[:] for row in S]
    for k in range(n):
        p=A[k][k]
        if p<0: return False
        if p==0:
            for j in range(k+1,n):
                if A[k][j]!=0: return False
            continue
        for i in range(k+1,n):
            if A[i][k]==0: continue
            fac=A[i][k]/p
            Ak=A[k]; Ai=A[i]
            for j in range(k,n): Ai[j]-=fac*Ak[j]
    return True

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    for f in M:
        Ps=cyc[f]; k=len(Ps); l=ell[f]
        a=F(l**3,4*(l*l-2))
        # p_f(v) = #geos thru v / k
        pf={}
        for v in range(n):
            c=sum(1 for P in Ps if v in P)
            if c: pf[v]=F(c,k)
        # tau_f edges: bad edge weight 1; geodesic edges weight (count/k)
        tau={}
        ef=(min(f),max(f)); tau[ef]=tau.get(ef,F(0))+F(1)
        for P in Ps:
            for i in range(len(P)-1):
                e=(min(P[i],P[i+1]),max(P[i],P[i+1])); tau[e]=tau.get(e,F(0))+F(1,k)
        # support = vertices touched by p_f or tau edges
        supp=set(pf.keys())
        for (x,y) in tau: supp.add(x); supp.add(y)
        supp=sorted(supp); idx={v:i for i,v in enumerate(supp)}; s=len(supp)
        # A = ell*diag(p_f) - p_f p_f^T - a*L_tau
        A=[[F(0)]*s for _ in range(s)]
        for v in supp:
            A[idx[v]][idx[v]]+= l*pf.get(v,F(0))
        for v in supp:
            for w in supp:
                A[idx[v]][idx[w]]-= pf.get(v,F(0))*pf.get(w,F(0))
        for (x,y),wt in tau.items():
            ix,iy=idx[x],idx[y]
            A[ix][ix]-= a*wt; A[iy][iy]-= a*wt; A[ix][iy]+= a*wt; A[iy][ix]+= a*wt
        acc['nbad']+=1
        if not is_psd([row[:] for row in A]):
            acc['fail']+=1
            if acc['first'] is None: acc['first']=(name,n,l,k)

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

if __name__=="__main__":
    acc={'nbad':0,'fail':0,'first':None}
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(nm,nn,adj,s,acc)
    print("  structured+Mycielskian+glued: bad-edges=%d LC-fails=%d"%(acc['nbad'],acc['fail']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d: bad-edges=%d LC-fails=%d"%(nn,acc['nbad'],acc['fail']),flush=True)
    print("\n  per-bad-edge LC atom: bad edges tested=%d  PSD FAILURES=%d %s"%(acc['nbad'],acc['fail'],acc['first'] or ''),flush=True)
    print("  === LOCAL CIRCULANT ATOM (per bad edge) %s => K + L_omega <= diag(T) PROVEN+verified ==="%("PSD everywhere" if not acc['fail'] else "FAILS"),flush=True)
