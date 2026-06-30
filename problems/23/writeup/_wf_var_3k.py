"""Reduce E1 in deficit variables d(v)=N-S(v) in [0,N]. p_f measure mass ell.
var = sum p_f d^2 - (sum p_f d)^2/ell = sum p_f d^2 - (ellN-row)^2/ell.   [since sum p_f d=ellN-row]
E1: var <= (N-row)(N-mean), mean=N-(ellN-row)/ell=row/ell. N-mean=(ellN-row)/ell=Dbar. row=ell*mean=N ell-(ellN-row)? consistent.
Let A:=sum p_f d  = ellN-row  (>=0). mean_d=A/ell=Dbar.
var = sum p_f d^2 - A^2/ell.
E1 RHS=(N-row)*Dbar = (N-row)*A/ell.
And N-row = N-(Nell-A)=A-N(ell-1)= A - N(ell-1).
So E1: sum p_f d^2 - A^2/ell <= (A-N(ell-1))*A/ell = A^2/ell - N(ell-1)A/ell.
 => sum p_f d^2 <= 2A^2/ell - N(ell-1)A/ell.        (*)  EXACT restated E1.
Test (*) directly == E1. Then test sufficient pointwise closers for sum p_f d^2:
  T1: sum p_f d^2 <= A * dmax    (dmax=max d on supp) -> = dmax-chain (FAILED).
  T2: sum p_f d^2 <= 2A^2/ell - N(ell-1)A/ell  is E1 itself.
  Investigate RHS sign and whether (*) is even an upper bound of a SUM OF SQUARES form:
  (*) <=> sum p_f d^2 - 2A^2/ell + N(ell-1)A/ell <=0.
  Note sum p_f d^2 - A^2/ell = var_d>=0, so LHS= var_d - A^2/ell + N(ell-1)A/ell = var_d + A/ell*(N(ell-1)-A).
  A=ellN-row, so N(ell-1)-A = N ell -N -ellN+row=row-N <=0 (row<=N!).
  => LHS = var_d + (A/ell)*(row-N) = var - Dbar*(N-row).   And E1 says LHS<=0 i.e. var<=Dbar(N-row)=(N-mean)(N-row). CIRCULAR (just E1 again).
So algebra is consistent; E1 is the genuine content. Test E1 EQUIVALENT clean form for proving:
  E1 <=> var <= Dbar*(N-row),  Dbar=N-mean, both factors >=0.
Compare to Bhatia-Davis: var=ell*Var(S) and we proved var<=ell(Smax-mean)(mean-Smin) [BD, 0-fail].
So SUFFICIENT to prove:  ell(Smax-mean)(mean-Smin) <= (N-mean)(N-row).   (**) [= BD-bridge, validated 0-fail]
Reduce (**): divide... use Smax<=N: ell(N-mean)(mean-Smin) <= (N-mean)(N-row)? cancel (N-mean)>0:
   ell(mean-Smin) <= N-row = N-ell*mean   => ell*mean - ell*Smin <= N-ell mean => 2 ell mean - ell Smin <= N
   => 2 row - ell Smin <= N.   (***)  Test (***): 2 row_f - ell_f*Smin_supp <= N ?"""
from fractions import Fraction as F
import subprocess
from _h import dec,GENG
from _stark1 import gmins
from _bdef_construct import mycielski,Cn,union_disjoint
import _wf_var_3 as W

cnt_star3=0; w3=None; cnt_e1=0; rows=0
# also test (**) the BD-bridge with Smax replaced by N (one-sided): ell(N-mean)(mean-Smin)<=(N-mean)(N-row)
cnt_bridgeNm=0; wNm=None
def push(name,n,E):
    global cnt_star3,w3,cnt_e1,rows,cnt_bridgeNm,wNm
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
            Smin=min(S[v] for v in d); Smax=max(S[v] for v in d)
            rows+=1
            if var>(N-row)*(N-mean): cnt_e1+=1
            # (***): 2 row - ell*Smin <= N
            if 2*row-ll*Smin>N:
                cnt_star3+=1
                if w3 is None or (2*row-ll*Smin-N)>w3[0]: w3=(2*row-ll*Smin-N,name,n,f,str(row),str(ll),str(Smin))
            # (**) bridge with Smax->N: ell(N-mean)(mean-Smin)<=(N-mean)(N-row)
            lhs=ll*(N-mean)*(mean-Smin); rhs=(N-mean)*(N-row)
            if lhs>rhs:
                cnt_bridgeNm+=1
                if wNm is None: wNm=(name,n,f)
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
print("rows",rows)
print("E1 fails:",cnt_e1)
print("(***) 2row - ell*Smin <= N  fails:",cnt_star3, "worst:",w3)
print("(**) bridge ell(N-mean)(mean-Smin)<=(N-mean)(N-row) [Smax->N] fails:",cnt_bridgeNm, wNm)
