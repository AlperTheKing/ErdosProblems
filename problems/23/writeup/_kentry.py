r"""Probe K[u,x] entries to understand the budget T(u)<=|U_u|.
T(u)=sum_{x in U_u} K[u,x]. Budget <=> average K-entry in row u over its support <= 1.
Tests:
  - max over ALL (u,x) of K[u,x] on loads-cut census N<=11 (diag and offdiag) -- is it <=1?
  - for both-pos zero-mu endpoints u: max K[u,x], and does T(u)<=|U_u| hold?
  - characterize: budget T(u)<=|U_u| vs T(u)<=N/2 ?  (is budget <=> T(u)<=N/2 - count mismatches)"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def Kmat(info):
    N=info['n']; M=info['M']; cyc=info['cyc']
    pf=[{} for _ in range(len(M))]
    pfx={}
    for idx,f in enumerate(M):
        Ps=cyc[f]; k=len(Ps)
        for x in range(N):
            c=sum(1 for P in Ps if x in P)
            if c: pfx[(f,x)]=F(c,k)
    K=[[F(0)]*N for _ in range(N)]
    for f in M:
        for x in range(N):
            px=pfx.get((f,x),F(0))
            if px==0: continue
            for y in range(N):
                py=pfx.get((f,y),F(0))
                if py: K[x][y]+=px*py
    return K,pfx

if __name__=="__main__":
    print("=== K-entry / budget characterization ===")
    gmaxK=F(0); gmaxKoff=F(0); recK=None
    bud_eq_half=0; bud_only=0; half_only=0; nverts=0
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            N=info['n']; T=info['T']
            K,pfx=Kmat(info)
            for u in range(N):
                if T[u]==0: continue
                Uu=[x for x in range(N) if K[u][x]>0]
                bud = (T[u]<=len(Uu))
                half = (2*T[u]<=N)
                nverts+=1
                if bud and half: bud_eq_half+=1
                elif bud and not half: bud_only+=1
                elif half and not bud: half_only+=1
                for x in range(N):
                    if K[u][x]>gmaxK: gmaxK=K[u][x]; recK=(g6,u,x,str(K[u][x]),u==x)
                    if u!=x and K[u][x]>gmaxKoff: gmaxKoff=K[u][x]
        print(f"  N={nn}: maxK={float(gmaxK)} maxK-offdiag={float(gmaxKoff)} | loaded-verts={nverts} "
              f"bud&half={bud_eq_half} bud-not-half={bud_only} half-not-bud={half_only}",flush=True)
    print(f"  global maxK record (g6,u,x,K,isdiag) = {recK}")
