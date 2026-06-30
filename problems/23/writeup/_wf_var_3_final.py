"""FINAL reduction chain for main: N(N-row_f) >= var_f  (NONUNIQUE f).
PROVEN steps (exact, 0-fail on standing gate = census N<=11 + Mycielskians N<=23 + blow-ups):
  (P0) S(v) <= N for all v               [L1; 0-fail. relies on ROWSUM-O for column sums = the proven envelope]
  (P1) row_f <= N                        [0-fail]
  (P2) deficit identity: sum_v p_f(v)(N-S(v)) = ell_f N - row_f   [pure algebra; 0-fail]
  (P3) Bhatia-Davis:  var_f <= ell_f (Smax-mean)(mean-Smin)       [classical theorem; 0-fail]
        with mean=row_f/ell_f, Smax/Smin = max/min of S over supp(f).
REDUCTION:
  (R1) main  <==  E1: var_f <= (N-row_f)(N-mean_f).
        Proof of implication: (N-row)(N-mean) <= N(N-row) since 0<=mean (=> N-mean<=N) and N-row>=0 (P1). IDENTITY.
  (R2) E1   <==  BD-bridge: ell(Smax-mean)(mean-Smin) <= (N-row)(N-mean).   [via (P3)]
GAP: BD-bridge holds 0-fail on the gate but is NOT yet derived from {P0,P1,P2}.
     One-sided relaxations Smax->N  OR  Smin->0  BOTH fail (validated). So BD-bridge needs the
     genuine concentration of S on supp(f): small spread (Smax-Smin) tied to (N-row).
This script re-verifies every PROVEN step and the two reductions are tight/consistent."""
from fractions import Fraction as F
import subprocess
from _h import dec,GENG
from _stark1 import gmins
from _bdef_construct import mycielski,Cn,union_disjoint
import _wf_var_3 as W

c=dict(rows=0,P0=0,P1=0,P2=0,P3=0,R1impl=0,E1=0,R2bridge=0,main=0)
w=dict()
def push(name,n,E):
    adj,cuts=gmins(n,E)
    for s in cuts:
        b=W.build(n,adj,s)
        if b is None: continue
        M,ell,cyc,P,S=b
        for f in M:
            if len(cyc[f])<2: continue
            d=P[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
            var=sum(d[v]*S[v]*S[v] for v in d)-row*row/ll
            N=F(n); mean=row/ll
            Sm=[S[v] for v in d]; Smax=max(Sm); Smin=min(Sm)
            c['rows']+=1
            # P0 over ALL vertices, not just supp:
            if any(S[v]>N for v in range(n)): c['P0']+=1
            if row>N: c['P1']+=1
            if sum(d[v]*(N-S[v]) for v in d)!=ll*N-row: c['P2']+=1
            if var>ll*(Smax-mean)*(mean-Smin): c['P3']+=1
            # R1 implication: (N-row)(N-mean)<=N(N-row)
            if (N-row)*(N-mean)>N*(N-row): c['R1impl']+=1
            # E1
            if var>(N-row)*(N-mean): c['E1']+=1
            # R2 bridge
            if ll*(Smax-mean)*(mean-Smin)>(N-row)*(N-mean): c['R2bridge']+=1
            # main
            if N*(N-row)-var<0: c['main']+=1
for nn in range(7,12):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg:
        n,E=dec(g6); push(f"cN{nn}",n,E)
def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,EE
def br(b1,b2,u,v):
    n,E=union_disjoint(b1,b2); n1=b1[0]; return n,E+[(u,n1+v)]
for it in [("M(C7)",)+mycielski(7,Cn(7)),("M(C9)",)+mycielski(9,Cn(9)),("M(C11)",)+mycielski(11,Cn(11)),
           ("MGrot23",)+mycielski(*mycielski(5,Cn(5))),("C7brgGrot",)+br((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9brgC9",)+br((9,Cn(9)),(9,Cn(9)),0,0),("C5b2",)+blowup([2,2,2,2,2]),("C5b3",)+blowup([3,3,3,3,3]),
           ("C5un",)+blowup([1,5,2,2,5]),("C7un",)+blowup([1,4,2,4,2,4,2]),("C5b16226",)+blowup([1,6,2,2,6])]:
    push(it[0],it[1],it[2])
print("=== FINAL CHAIN VALIDATION (all counts are FAIL counts; 0 = holds exactly) ===")
for k in ['rows','P0','P1','P2','P3','R1impl','E1','R2bridge','main']:
    print(f"  {k}: {c[k]}")
