"""Shared data collector (cached build) for bridge experiments. Adds pfmin per row."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
import _wf_var_3 as W

def collect():
    out = []
    def push(name, n, E):
        adj, cuts = gmins(n, E)
        for s in cuts:
            b = W.build(n, adj, s)
            if b is None: continue
            M, ell, cyc, P, S = b
            for f in M:
                if len(cyc[f]) < 2: continue
                d = P[f]; ll = sum(d.values())
                row = sum(d[v]*S[v] for v in d)
                Q = sum(d[v]*S[v]*S[v] for v in d)
                var = Q - row*row/ll
                vs = [S[v] for v in d]
                Smax = max(vs); Smin = min(vs)
                pfmin = min(d.values())
                out.append((name, n, f, ll, row, Q, var, Smax, Smin, pfmin))
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); push(f"cN{nn}", n, E)
    def blowup(parts):
        m=len(parts); off=[0]*(m+1)
        for i in range(m): off[i+1]=off[i]+parts[i]
        nn=off[m]; EE=[]
        for i in range(m):
            j=(i+1)%m
            for a in range(off[i],off[i+1]):
                for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
        return nn,EE
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("M(C7)",)+mycielski(7,Cn(7)),("M(C9)",)+mycielski(9,Cn(9)),
           ("M(C11)",)+mycielski(11,Cn(11)),("MGrot23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7brgGrot",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9brgC9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0),
           ("C5b2",)+blowup([2,2,2,2,2]),("C5b3",)+blowup([3,3,3,3,3]),
           ("C5un",)+blowup([1,5,2,2,5]),("C7un",)+blowup([1,4,2,4,2,4,2]),
           ("C5b16226",)+blowup([1,6,2,2,6])]
    for it in extra: push(it[0], it[1], it[2])
    return out

data = collect()
