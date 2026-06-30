"""E1: var_f <= (N-row_f)(N-mean_f), mean=row/ell. holds 0-fail & implies main.
Now PROVE E1. var=ell*Var_mu(S), mean=E_mu(S), row=ell*mean.
E1: ell*Var(S) <= (N-ell*mean)(N-mean).
Try to derive from Bhatia-Davis Var(S)<=(Smax-mean)(mean-Smin) with Smax<=N:
   ell*(Smax-mean)(mean-Smin) <= (N-ell mean)(N-mean) ??  -> this is exactly BD-bridge, validated 0-fail.
But BD-bridge uses Smax,Smin. To get E1 in closed form we used E1 directly (validated). Let's see if
E1 follows from a SIMPLER proven inequality:
   E1 <=> ell*E_mu(S^2) - ell*mean^2 <= N^2 - N mean - ell mean N + ell mean^2
      <=> ell*E(S^2) <= N^2 - N mean - ell mean N + 2 ell mean^2
      Q = ell*E(S^2) = sum_v p_f S^2.  So E1 <=> Q <= N^2 - N mean - ell N mean + 2 ell mean^2.
   Hmm messy. Test an EQUIVALENT clean form:
   Claim E1':  Q_f + row_f*mean_f <= N^2 - (N)(mean_f) ... let me just verify E1 algebra by recomputing both sides from raw P,S and confirm identity-level equality of the two encodings.
Also test the SHARPER provable lemma:
   PROVEN-CANDIDATE F1: for each v in supp(f): S(v) <= N AND sum_v p_f(v)(N-S(v)) >= (N-row)*?
   Let define deficit d(v)=N-S(v)>=0 (from S<=N). Then:
     N-row = N - sum p_f S = sum p_f (N-S) + (N - ell? ) NO: sum_v p_f(v)=ell, so sum p_f (N-S)= ell N - row.
     So sum_v p_f(v) d(v) = ell*N - row.   (identity, uses S<=N for d>=0)
   And var = sum p_f (S-mean)^2 = sum p_f ((N-mean)-(N-S))^2 = sum p_f (Dbar - d)^2 where Dbar=N-mean.
     = sum p_f d^2 - 2 Dbar sum p_f d + Dbar^2 ell
     = [sum p_f d^2] - 2 Dbar(ellN-row) + Dbar^2 ell.
   E1 RHS=(N-row)(N-mean)=(N-row)Dbar.
   So E1 <=> sum p_f d^2 - 2Dbar(ellN-row)+Dbar^2 ell <= (N-row)Dbar.
   Use sum p_f d^2 <= (max d) * sum p_f d = (max_v (N-S(v))) (ellN-row). max d = N - Smin.
   Test FINAL reduced inequality with dmax:=N-Smin_supp:
     LHS<= dmax*(ellN-row) -2Dbar(ellN-row)+Dbar^2 ell  <=? (N-row)Dbar.
   Test this chain numerically (uses Smin only, not Smax)."""
from fractions import Fraction as F
import _wf_var_3d_data as D
data=D.data
# verify identity sum p_f d = ellN-row, and var encoding, then test dmax-chain
f_id=0; f_chain=0; wchain=None
import subprocess
from _h import dec,GENG
from _stark1 import gmins
from _bdef_construct import mycielski,Cn,union_disjoint
import _wf_var_3 as W
# need per-row S on supp to compute sum p_f d^2 exactly; recompute lightweight on a subset+full battery
def battery_push(push):
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

cntE1=0; wE1=None; cntID=0; cntChain=0; wChain=None; rows=0
def push(name,n,E):
    global cntE1,wE1,cntID,cntChain,wChain,rows
    adj,cuts=gmins(n,E)
    for s in cuts:
        b=W.build(n,adj,s)
        if b is None: continue
        M,ell,cyc,P,S=b
        for f in M:
            if len(cyc[f])<2: continue
            d=P[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
            var=sum(d[v]*S[v]*S[v] for v in d)-row*row/ll
            N=F(n); mean=row/ll; Dbar=N-mean
            rows+=1
            # E1
            if var>(N-row)*Dbar:
                cntE1+=1
                if wE1 is None: wE1=(name,n,f)
            # identity sum p_f (N-S) = ellN-row
            spd=sum(d[v]*(N-S[v]) for v in d)
            if spd!=ll*N-row: cntID+=1
            # dmax chain: sum p_f d^2 <= dmax*(ellN-row); LHS_chain:
            dmax=max(N-S[v] for v in d)
            sumpd2=sum(d[v]*(N-S[v])**2 for v in d)
            # exact var via this encoding:
            var2=sumpd2-2*Dbar*spd+Dbar*Dbar*ll
            # chain bound on var:
            chain= dmax*spd-2*Dbar*spd+Dbar*Dbar*ll
            if chain>(N-row)*Dbar:
                cntChain+=1
                if wChain is None: wChain=(name,n,f,str(dmax),str(min(S[v] for v in d)))
battery_push(push)
print("rows",rows)
print("E1 var<=(N-row)(N-mean) fails:",cntE1, wE1)
print("identity sum p_f(N-S)=ellN-row fails:",cntID)
print("dmax-chain  fails:",cntChain, wChain)
