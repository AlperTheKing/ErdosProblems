"""EXACT gate of GPT's circulant route assembly. K=PP^T, P[v,f]=p_f(v)=#geos/|cyc_f|, T(v)=sum ell_f p_f(v).
R_cyc = sum_f a_f L_f,  a_f = ell_f^3/(4(ell_f^2-2)) [rational <= sharp], L_f = (1/|cyc_f|) sum_{P in cyc_f}
L_{cycle(P)}, cycle(P)=P + closing bad edge (simple ell_f-cycle Laplacian). Test PSD (exact rational LDL):
  (1) B - R_cyc = diag(T) - K - R_cyc >= 0   [min-free circulant identity; expect hold on ALL max cuts]
  (2) R_cyc + diag(N - T) >= 0               [closure-relevant 'Hardy-Schrodinger'; min-DEPENDENT]
If both hold => N*I-K = (1)+(2) >= 0 = SPEC => Gamma<=N^2 => delta=0.  Battery N<=30 (gmins)."""
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
    if n>30: return
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    # P[v,f]
    Mlist=list(M)
    P=[[F(0)]*len(Mlist) for _ in range(n)]
    for fi,f in enumerate(Mlist):
        Ps=cyc[f]; cf=len(Ps)
        for v in range(n):
            c=sum(1 for Pp in Ps if v in Pp)
            if c: P[v][fi]=F(c,cf)
    # K = P P^T
    K=[[F(0)]*n for _ in range(n)]
    for u in range(n):
        Pu=P[u]
        for w in range(u,n):
            Pw=P[w]
            s=sum(Pu[fi]*Pw[fi] for fi in range(len(Mlist)))
            K[u][w]=s; K[w][u]=s
    Tv=[sum(ell[Mlist[fi]]*P[v][fi] for fi in range(len(Mlist))) for v in range(n)]
    # R_cyc
    R=[[F(0)]*n for _ in range(n)]
    for fi,f in enumerate(Mlist):
        l=ell[f]
        if l*l-2==0: continue
        a=F(l**3,4*(l*l-2))
        cf=len(cyc[f]); w=a/cf
        for Pp in cyc[f]:
            L=len(Pp)
            # simple cycle: consecutive in Pp, plus closing edge (Pp[-1],Pp[0])
            cyedges=[(Pp[i],Pp[(i+1)%L]) for i in range(L)]
            for (x,y) in cyedges:
                R[x][x]+=w; R[y][y]+=w; R[x][y]-=w; R[y][x]-=w
    # (1) diag(T) - K - R
    S1=[[ (Tv[i]-K[i][i]-R[i][i]) if i==j else (-K[i][j]-R[i][j]) for j in range(n)] for i in range(n)]
    # (2) R + diag(N - T)
    S2=[[ (R[i][i]+F(n)-Tv[i]) if i==j else R[i][j] for j in range(n)] for i in range(n)]
    acc['n']+=1
    if not is_psd(S1):
        acc['v1']+=1
        if acc['f1'] is None: acc['f1']=(name,n,len(M))
    if not is_psd(S2):
        acc['v2']+=1
        if acc['f2'] is None: acc['f2']=(name,''.join(map(str,side)),n,len(M))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc={'n':0,'v1':0,'v2':0,'f1':None,'f2':None}
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>30: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[2,1,2,1,3]]:
        n,E=blowup(parts)
        if n>30: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(nm,nn,adj,s,acc)
    print("  structured done: configs=%d (1)B-R_cyc viol=%d (2)R+diag(N-T) viol=%d"%(acc['n'],acc['v1'],acc['v2']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done: configs=%d v1=%d v2=%d"%(nn,acc['n'],acc['v1'],acc['v2']),flush=True)
    print("\n  configs=%d"%acc['n'],flush=True)
    print("  (1) B - R_cyc >= 0 (min-free circulant): violations=%d %s"%(acc['v1'],acc['f1'] or ''),flush=True)
    print("  (2) R_cyc + diag(N-T) >= 0 (closure/min-dep): violations=%d %s"%(acc['v2'],acc['f2'] or ''),flush=True)
    print("  === %s ==="%("BOTH HOLD => circulant route CLOSES SPEC on battery!" if not acc['v1'] and not acc['v2']
        else "(1)%s (2)%s"%("ok" if not acc['v1'] else "FAILS","ok" if not acc['v2'] else "FAILS")),flush=True)
