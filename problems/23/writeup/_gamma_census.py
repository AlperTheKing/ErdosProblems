"""Exhaustive census gate for Gamma <= N^2 over ALL connected triangle-free graphs N=5..11,
gmin connected-B max cut. Exact integers. Reports any violation + worst ratio."""
import subprocess, sys
from fractions import Fraction as F
from _h import dec, GENG, gmin, maxcut_all

def gamma(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    return G

Nmax=int(sys.argv[1]) if len(sys.argv)>1 else 11
worst=F(0); worstg=None; totalv=0; total=0
for N in range(5,Nmax+1):
    out=subprocess.run([GENG,"-c","-t",str(N)],capture_output=True,text=True).stdout.split()
    cnt=0; vio=0
    for g6 in out:
        n,E=dec(g6)
        G=gamma(n,E)
        if G is None: continue
        cnt+=1; total+=1
        rat=F(G,n*n)
        if rat>worst: worst=rat; worstg=(g6,n,G)
        if G>n*n:
            vio+=1; totalv+=1
            if vio<=3: print(f"  VIOLATION N={N} g6={g6} Gamma={G} > {n*n}", flush=True)
    print(f"N={N}: {cnt} gmin instances, {vio} violations (worst-so-far ratio {float(worst):.5f} @ {worstg})", flush=True)
print(f"TOTAL {total} instances, {totalv} violations. Worst Gamma/N^2 = {float(worst):.6f} at {worstg}", flush=True)
print("Gamma<=N^2 HOLDS on full connected-tri-free census" if totalv==0 else "*** VIOLATIONS FOUND ***", flush=True)
