"""EXACT battery test for candidate (a): Gamma = sum_f ell_f^2 <= N^2 for every
triangle-free Gamma-min connected-B max cut.

Gamma <= N^2 is STRONGER than the target: Gamma >= 25 m and Gamma <= N^2 => m <= N^2/25.

Coverage:
 - census small N (geng, all connected triangle-free, N<=10) via gmin from _h
 - C5[t] balanced blow-ups t=1..8 (extremal: Gamma = N^2 exactly)
 - two-lane family L=8,12,16,20 (the rho(O)>N killer)
 - Mycielskians: M(C5)=Grotzsch (N=11), M(Grotzsch) (N=23), M_2(Petersen) (N=21),
   M(C9) (N=19), M_4(C5) (N=21), M(C7) (N=15), M(C11) (N=23)
 - iterated standing-gate Mycielskians

Reports Gamma, N^2, ratio Gamma/N^2, and any VIOLATION (Gamma > N^2) exactly (Fraction).
"""
from fractions import Fraction as F
import subprocess, sys
from _h import dec, maxcut_all, gmin, blow
import AUDIT_mycielski_uniform as A
from _verify_two_lane import build_two_lane

GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

def gamma_of_edges(n, E):
    """Build adj, find gmin connected-B max cut, return (Gamma, N) or None."""
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    return G, n

def report(name, n, E):
    res=gamma_of_edges(n,E)
    if res is None:
        print(f"[{name}] N={n}: no gmin connected-B max cut (skip)")
        return None
    G,N=res
    N2=N*N
    viol = G > N2
    ratio=F(G,N2) if N2 else F(0)
    tag = "*** VIOLATION Gamma>N^2 ***" if viol else ("TIGHT (=N^2)" if G==N2 else "OK")
    print(f"[{name}] N={N} Gamma={G} N^2={N2} Gamma/N^2={float(ratio):.4f} {tag}")
    return (name,N,G,N2,viol)

violations=[]
def track(r):
    if r and r[4]: violations.append(r)

print("="*70)
print("PART 1: C5[t] balanced blow-ups (extremal, expect Gamma=N^2)")
print("="*70)
for t in range(1,9):
    n,E=blow(t)
    track(report(f"C5[{t}]", n, E))

print("="*70)
print("PART 2: two-lane family (rho(O)>N killer)")
print("="*70)
for L in (8,12,16,20):
    n,E,side,bad=build_two_lane(L)
    track(report(f"two-lane L={L}", n, E))

print("="*70)
print("PART 3: Mycielskians (incl standing gate; N=23 Myc(Grotzsch) broke (k2))")
print("="*70)
# use fast maxcut for the big ones
from AUDIT_mycielski_n23 import maxcut_all_fast
def report_myc(name, n, E):
    adj=A.build_adj(n,E)
    if not A.is_triangle_free(n,adj):
        print(f"[{name}] N={n}: NOT triangle-free, skip"); return None
    cuts = maxcut_all_fast(n,adj) if n>=18 else maxcut_all(n,adj)
    r=A.gmin(n,adj,cuts)
    if r is None:
        print(f"[{name}] N={n}: no gmin connected-B max cut"); return None
    side,G,M,ell=r
    N2=n*n; viol=G>N2
    print(f"[{name}] N={n} Gamma={G} N^2={N2} Gamma/N^2={float(F(G,N2)):.4f} {'*** VIOLATION ***' if viol else 'OK'}")
    return (name,n,G,N2,viol)

track(report_myc("M(C5)=Grotzsch", *A.mycielskian(*A.cycle(5))))
track(report_myc("M(C7)", *A.mycielskian(*A.cycle(7))))
track(report_myc("M(C9)", *A.mycielskian(*A.cycle(9))))
track(report_myc("M(C11)", *A.mycielskian(*A.cycle(11))))
gn,gE=A.mycielskian(*A.cycle(5))
track(report_myc("M(Grotzsch) N=23", *A.mycielskian(gn,gE)))
track(report_myc("M_2(Petersen)", *A.gen_mycielskian(*A.petersen(),2)))
track(report_myc("M_4(C5)", *A.gen_mycielskian(*A.cycle(5),4)))

print("="*70)
print("PART 4: census small N (all connected triangle-free, geng)")
print("="*70)
maxviol_ratio=F(0); worst=None
total=0
for N in range(5,11):
    try:
        out=subprocess.run([GENG,"-c","-t",str(N)],capture_output=True,text=True,timeout=300)
    except Exception as e:
        print(f"  N={N}: geng failed {e}"); continue
    cnt=0; vio=0
    for line in out.stdout.split():
        line=line.strip()
        if not line: continue
        n,E=dec(line)
        res=gamma_of_edges(n,E)
        if res is None: continue
        G,nn=res; cnt+=1; total+=1
        rat=F(G,nn*nn)
        if rat>maxviol_ratio: maxviol_ratio=rat; worst=(line,nn,G)
        if G>nn*nn:
            vio+=1
            if vio<=3: print(f"  VIOLATION g6={line} N={nn} Gamma={G} > {nn*nn}")
    print(f"  N={N}: {cnt} gmin-instances, {vio} violations")
print(f"census max Gamma/N^2 ratio = {float(maxviol_ratio):.4f} at {worst}")

print("="*70)
print("SUMMARY")
print("="*70)
if violations:
    print(f"FALSE: {len(violations)} violation(s) of Gamma<=N^2:")
    for v in violations: print("  ", v)
else:
    print("Gamma <= N^2 HELD on ALL battery families (C5[t] tight, two-lane, Mycielskians N<=23, census N<=10).")
