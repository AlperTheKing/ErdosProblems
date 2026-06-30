"""STRONG' on the ADVERSARIAL cases only (N=23 Myc-Grotzsch, blowups, glued) -- the ones that killed STRONG.
Plus census N=11 done separately by the full gate. Exact."""
from fractions import Fraction as F
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _wf_var_0 import build

def bridge(b1,b2,u,v):
    n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,EE

cases=[("MycGrotzschN23",)+mycielski(*mycielski(5,Cn(5))),
       ("C7brgGrot",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
       ("C5[2]",)+blowup([2,2,2,2,2]),
       ("C5[3]",)+blowup([3,3,3,3,3]),
       ("C5[4]",)+blowup([4,4,4,4,4]),
       ("C5unbal155",)+blowup([1,5,2,2,5]),
       ("C5[1,6,2,2,6]",)+blowup([1,6,2,2,6]),
       ("C7unbal",)+blowup([1,4,2,4,2,4,2]),
       ("MycC7",)+mycielski(7,Cn(7)),
       ("MycC9",)+mycielski(9,Cn(9)),
       ("MycC11",)+mycielski(11,Cn(11))]

for nm,n,E in cases:
    adj,cuts=gmins(n,E)
    rows=0; fails=0; worst=None; firstf=None
    for s in cuts:
        b=build(n,adj,s)
        if b is None: continue
        M,ell,T,mu,cyc,S,pf=b
        for f in M:
            if len(cyc[f])<2: continue
            d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); sm=row/ll
            Smax=max(S[v] for v in d); Smin=min(S[v] for v in d)
            bound=ll*((Smax-sm)*(sm-Smin)+F(n)*sm); slk=F(n)**2-bound
            rows+=1
            if slk<0:
                fails+=1
                if firstf is None: firstf=(f,str(row),str(Smax),str(Smin),str(sm),str(slk))
            if worst is None or slk<worst: worst=slk
    print(f"{nm} N={n}: rows={rows} STRONGprime-FAILS={fails} worst-slack={worst}"+(f" FIRST={firstf}" if firstf else ""),flush=True)
