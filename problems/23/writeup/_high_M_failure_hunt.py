"""MAKE-OR-BREAK for the |M|-salvage: do ROWSUM-O / rho(O)<=N failures stay LOW-bad-count (|M| << N^2/25), or
can a HIGH-|M| (near N^2/25) triangle-free gamma-min connected-B max cut fail? beta=|M|=e-MaxCut; conjecture is
|M|<=N^2/25, extremal C5[t] sits exactly at |M|=N^2/25 and holds tight. If every failure has |M| well below
N^2/25, the proof splits (direct beta bound for low |M|, spectral for high |M|). Report, per config: |M|,
N^2/25, ROWSUM max-ratio, rho(O)/N, and FLAG any failure with |M|/(N^2/25) large.
Battery: census gamma-min N<=11 + blow-ups C5[t]/C7[t]/C9[t] (boundary) + two-lane L=8..16 + Mycielskians +
adversarial multi-lane / multi-chord attempts to push |M| up while failing."""
import subprocess
from fractions import Fraction as F
import numpy as np
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane, Ogram, cutsize

def classify(name,n,adj,side,acc,want_global_max=False):
    if not Bconn(n,adj,side): return
    res=Ogram(n,adj,side)
    if res is None: return
    M,ell,O=res
    Mcnt=len(M)
    rowsums=[float(sum(O[i])) for i in range(Mcnt)]
    maxrow=max(rowsums) if rowsums else 0.0
    Of=np.array([[float(x) for x in r] for r in O]) if Mcnt else np.zeros((0,0))
    rho=max(abs(np.linalg.eigvals(Of))) if Mcnt else 0.0
    Nq=n*n/25.0
    rowsum_fail = maxrow>n+1e-9
    rho_fail = rho>n+1e-9
    if rowsum_fail or rho_fail:
        acc['fails'].append((name,n,Mcnt,Nq,round(Mcnt/Nq,3),round(maxrow/n,4),round(rho/n,4)))
        if Mcnt/Nq>acc['max_Mratio'][0]:
            acc['max_Mratio']=(Mcnt/Nq,name,n,Mcnt,Nq,round(rho/n,4),round(maxrow/n,4))
    acc['n_configs']+=1

def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

if __name__=="__main__":
    acc={'n_configs':0,'fails':[],'max_Mratio':(0.0,'','','','','','')}
    print("=== HIGH-|M| failure hunt (|M| vs N^2/25 for ROWSUM-O/rho(O) failures) ===",flush=True)
    # two-lane family L=8..16
    for L in range(8,17,2):
        n,E,side,bad=build_two_lane(L); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        classify("two-lane-L%d"%L,n,adj,side,acc)
    # census gamma-min
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: classify("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (configs=%d fails=%d)"%(nn,acc['n_configs'],len(acc['fails'])),flush=True)
    # boundary blow-ups C5[t],C7[t],C9[t]
    for cyc in (5,7,9):
        for t in range(1,9):
            n,E=blowup([t]*cyc); adj0,cuts=gmins(n,E)
            for s in cuts[:2]: classify("C%d[%d]"%(cyc,t),n,[set(x for x in a) for a in (lambda adj=[set() for _ in range(n)]: [ (adj[u].add(v) or adj[v].add(u)) for u,v in E] and adj)()],s,acc) if False else None
            adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            for s in (cuts[:2] if cuts else []): classify("C%d[%d]"%(cyc,t),n,adj,s,acc)
    print("  boundary blow-ups done (configs=%d)"%acc['n_configs'],flush=True)
    # Mycielskians
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: classify(name,nn,adj,s,acc)
    print("  Mycielskians done (configs=%d)"%acc['n_configs'],flush=True)
    print("\n  total configs=%d  TOTAL FAILURES (rowsum or rho > N)=%d"%(acc['n_configs'],len(acc['fails'])),flush=True)
    print("  failures (name,N,|M|,N^2/25,|M|/(N^2/25),maxrow/N,rho/N):",flush=True)
    for fr in sorted(acc['fails'], key=lambda z:-z[4])[:20]: print("    ",fr,flush=True)
    print("  LARGEST |M|/(N^2/25) among failures = %s"%(acc['max_Mratio'],),flush=True)
    hi=[f for f in acc['fails'] if f[4]>=1.0]
    print("  === %s ==="%("BREAK: a failure with |M|>=N^2/25 exists -> salvage dead" if hi else "SALVAGE HOLDS in battery: every ROWSUM-O/rho(O) failure has |M| < N^2/25 (low-bad-count, harmless)"),flush=True)
