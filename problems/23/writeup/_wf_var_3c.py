"""Spectral route. Build K=P P^T (badedge x badedge), and examine var_f via K.
row_f = sum_g K_{fg}  (=(K 1)_f).
K_{ff}=sum_v p_f(v)^2.
Note S(v)=sum_g p_g(v). Q_f=sum_v p_f(v)S(v)^2.

Identity attempt: var_f = sum_v p_f(v)(S(v)-row_f/ell_f)^2.
Let's see relation: define for fixed f, the measure dmu_f(v)=p_f(v)/ell_f (prob measure, sum=1).
Then row_f/ell_f = E_mu[S], var_f/ell_f = Var_mu(S) (true variance under prob measure).
So var_f = ell_f * Var_{mu_f}(S),  row_f = ell_f * E_{mu_f}(S).
Inequality: N(N-row_f) >= ell_f Var_mu(S).
We KNOW S(v)<=N (L1, validated 0-fail). Under any prob measure with S in [0,N]:
   Var(S) <= E(S)(N-E(S))   [Bhatia-Davis / Popoviciu-type: variance of a [0,N] RV <= mean*(N-mean)].
So ell_f Var_mu(S) <= ell_f * E_mu(S)(N-E_mu(S)) = ell_f*(row_f/ell_f)(N-row_f/ell_f)
   = row_f*(N - row_f/ell_f) = N row_f - row_f^2/ell_f.
Need: N(N-row_f) >= N row_f - row_f^2/ell_f ?  i.e. N^2 - N row >= N row - row^2/ell
   i.e. N^2 - 2N row + row^2/ell >= 0.  NOT always (that's bridge-A-like). So Bhatia-Davis alone insufficient too.
BUT we also have S(v)>=0 AND a lower structural bound? Test the SHARPER Bhatia-Davis using actual min m=min S over support:
   Var(S) <= (M - E)(E - m) with M=max,m=min of S on support of f.
Test BD-tight bridge: N(N-row) >= ell_f*(Smax_supp - row/ell)(row/ell - Smin_supp)."""
from fractions import Fraction as F
import _wf_var_3 as W

def smm(P, S, f):
    vs = [S[v] for v in P[f]]
    return max(vs), min(vs)

accs_data = []
import subprocess
from _h import dec, GENG
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

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
                Smax, Smin = smm(P, S, f)
                out.append((name, n, f, ll, row, Q, var, Smax, Smin))
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
print("rows", len(data))
# Bridge BD-tight: N(N-row) >= ell*(Smax-row/ell)(row/ell-Smin)
fBD = 0; fBD_worst = None
# also the SDP/popoviciu form: ell*Var <= ell * (Smax-Smin)^2/4
fPOP = 0
# verify BD identity bound holds: var <= ell*(Smax-row/ell)(row/ell-Smin)
fBDident = 0; fBDident_worst=None
for (name, n, f, ll, row, Q, var, Smax, Smin) in data:
    N = F(n); mean = row/ll
    bd = ll*(Smax-mean)*(mean-Smin)
    if var > bd + F(0):
        fBDident += 1
        if fBDident_worst is None: fBDident_worst=(name,n,f,str(var),str(bd))
    if N*(N-row) - bd < 0:
        fBD += 1
        d=(N*(N-row)-bd,name,n,f,str(row),str(ll),str(Smax),str(Smin))
        if fBD_worst is None or d[0]<fBD_worst[0]: fBD_worst=d
print("BD identity var<=ell*(Smax-mean)(mean-Smin) fails:", fBDident, fBDident_worst)
print("BRIDGE BD-tight N(N-row)>=ell(Smax-mean)(mean-Smin) fails:", fBD, "worst:", fBD_worst)
