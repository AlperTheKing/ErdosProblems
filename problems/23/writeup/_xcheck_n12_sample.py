#!/usr/bin/env python3
"""Independent cross-check: re-run a SAMPLE (every k-th) of geng -tc 12 through the
ORIGINAL census_GPI functions (different code path from AUDIT_Tuniform_n12.py), exact
Fractions, confirm 0 U-violations and report min-slack on the sample. Also runs the
LP-dual GPI (gpi_tau) on the worst graph: tau* must be <= maxT (uniform-share) <= K."""
import sys, subprocess, importlib.util, io, contextlib
from fractions import Fraction
spec=importlib.util.spec_from_file_location("cg","E:/Projects/ErdosProblems/problems/23/writeup/census_GPI.py")
cg=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(cg)
GENG=cg.GENG
STEP=11  # sample every 11th graph -> ~104k independent rechecks

def U(g6):
    n,E=cg.dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=cg.gmin(n,adj,cg.maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    K=n+(n*n-G)
    T=[Fraction(0) for _ in range(n)]
    for (u,v) in M:
        Ps=cg.geos(adj,side,u,v); nf=len(Ps); sh=Fraction(ell[(u,v)],nf)
        for P in Ps:
            for w in P: T[w]+=sh
    return n,G,K,max(T)

proc=subprocess.Popen([GENG,"-tc","12"],stdout=subprocess.PIPE,text=True,bufsize=1<<20)
checked=0;skipped=0;viol=0;min_slack=None;worst=None;idx=0
for line in proc.stdout:
    g=line.strip()
    if not g: continue
    idx+=1
    if idx % STEP: continue
    r=U(g)
    if r is None: skipped+=1; continue
    n,G,K,maxT=r; checked+=1
    slack=Fraction(K)-maxT
    if min_slack is None or slack<min_slack: min_slack=slack; worst=(g,n,G,K,maxT)
    if maxT>K: viol+=1; print("VIOL",g,n,G,K,maxT)
print(f"SAMPLE(step={STEP}): checked={checked} skipped={skipped} viols={viol}")
print(f"min_slack={min_slack} ({float(min_slack):.4f}) at {worst}")

# LP-dual GPI on the worst graph from the full run
gw="K?ABBBwerwBw"
n,E=cg.dec(gw); G,n2,tau,K=cg.gpi_tau(n,E)
print(f"LP-dual GPI on {gw}: Gamma={G} tau*={tau:.6f} K={K}  tau*<=K:{tau<=K+1e-9}")
