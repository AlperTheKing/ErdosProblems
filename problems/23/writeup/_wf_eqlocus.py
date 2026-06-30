import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _wf_var_0 import build
eq=0; eq_const=0; eq_n5=0
for nn in range(7,11):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg:
        n,E=dec(g6); adj,cuts=gmins(n,E)
        for s in cuts:
            b=build(n,adj,s)
            if b is None: continue
            M,ell,T,mu,cyc,S,pf=b
            for f in M:
                if len(cyc[f])<2: continue
                d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mean=row/ll
                var=sum(d[v]*(S[v]-mean)**2 for v in d)
                margin=F(n)*(F(n)-row)-var
                if margin==0:
                    eq+=1
                    vals=set(S[v] for v in d)
                    if len(vals)==1: eq_const+=1
                    if all(S[v]==F(n,5) for v in d): eq_n5+=1
print("census<=10: margin==0 rows",eq,"S-constant-on-support",eq_const,"S==n/5",eq_n5)
