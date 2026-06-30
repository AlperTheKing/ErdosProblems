"""Locate the single R2-bridge fail: ell(Smax-mean)(mean-Smin) > (N-row)(N-mean) while E1 holds.
This means BD bound is LOOSER than E1 there -> BD-bridge is NOT a valid route in that row.
Print it fully."""
from fractions import Fraction as F
import subprocess
from _h import dec,GENG
from _stark1 import gmins
from _bdef_construct import mycielski,Cn,union_disjoint
import _wf_var_3 as W
def push(name,n,E,out):
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
            bd=ll*(Smax-mean)*(mean-Smin); e1rhs=(N-row)*(N-mean)
            if bd>e1rhs:
                out.append((name,n,f,str(ll),str(row),str(mean),str(var),str(Smax),str(Smin),str(bd),str(e1rhs),str(var<=e1rhs)))
out=[]
for nn in range(7,12):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg:
        n,E=dec(g6); push(f"cN{nn}",n,E,out)
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
    push(it[0],it[1],it[2],out)
print("R2-bridge fails (name,n,f,ell,row,mean,var,Smax,Smin,BDbound,E1rhs,var<=E1rhs):")
for o in out: print("  ",o)
