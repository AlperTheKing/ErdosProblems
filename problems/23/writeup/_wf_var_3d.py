"""The BD bridge N(N-row)>=ell*(Smax-mean)(mean-Smin) holds 0-fail but uses Smax,Smin (graph-specific).
Need to ground it in PROVEN facts. Investigate what bounds Smax_supp, Smin_supp, and find the
tightest TRUE bridge expressible in {N, row, ell, and a PROVEN bound on S on supp(f)}.

Candidate proven facts to lean on:
 (a) S(v) <= N for all v          [L1, 0-fail]
 (b) row_f <= N                   [0-fail]
 (c) ell_f <= N                   [0-fail]
 (d) Smin_supp >= p_f-driven lower bound? S(v) >= p_f(v) for v in supp(f) (since f itself contributes p_f(v) to S(v)). So S(v)>=p_f(v).
     In particular on supp, S(v) >= p_f(v) > 0. For the geodesic-interior the contribution... test S(v)>=1 on supp?
 (e) The mean bar S = row/ell.

Test refined bridges:
 R1:  N(N-row) >= ell*(N-mean)(mean-Smin)        (use Smax<=N only; keep true Smin)  -> does worse than BD-tight, check if still 0-fail
 R2:  N(N-row) >= ell*(Smax-mean)*mean           (Smin>=0 only; keep true Smax)
 R3:  N(N-row) >= ell*(N-mean)*mean = (N-mean)*row  (both extremes; = Bridge A) -> known FAIL
Also gather: distribution of Smax_supp and Smin_supp vs N at the BD-tight equality-ish rows; and test
 KEY CLAIM:  Smax_supp + Smin_supp <= N + mean ??? or  ell*(Smax-mean)(mean-Smin) <= N(N-row) reduces via Smax-Smin<= something.
"""
from fractions import Fraction as F
import _wf_var_3d_data as D

data = D.data
N_ = lambda n: F(n)
fR1=0; fR1w=None
fR2=0; fR2w=None
# proven lower bound on S(v) on supp: S(v) >= p_f(v). min over supp -> Smin >= min_v p_f(v) =: pfmin
# Also S(v) >= p_f(v); but a cleaner: every v in supp(f) is on a geodesic of f, contributing; also endpoints u,w of f are on EVERY geodesic so p_f=1 there, S>=1.
# Test: is Smin_supp >= 1 ? (endpoints always have p_f=1, but min could be interior with p_f<1)
fSmin1=0
# Test bound: Smax_supp <= ell_f ? S(v)=sum_g p_g(v) <= number of bad edges through v's geodesics...
fSmaxEll=0
for rec in data:
    name,n,f,ll,row,Q,var,Smax,Smin,pfmin = rec
    N=F(n); mean=row/ll
    if Smin < 1: fSmin1+=1
    if Smax > ll: fSmaxEll+=1
    r1 = ll*(N-mean)*(mean-Smin)
    if N*(N-row)-r1<0:
        fR1+=1
        d=(N*(N-row)-r1,name,n,f);
        if fR1w is None or d[0]<fR1w[0]: fR1w=d
    r2 = ll*(Smax-mean)*mean
    if N*(N-row)-r2<0:
        fR2+=1
        d=(N*(N-row)-r2,name,n,f)
        if fR2w is None or d[0]<fR2w[0]: fR2w=d
print("rows", len(data))
print("Smin_supp>=1 fails:", fSmin1)
print("Smax_supp<=ell_f fails:", fSmaxEll)
print("R1 N(N-row)>=ell(N-mean)(mean-Smin) fails:", fR1, fR1w)
print("R2 N(N-row)>=ell(Smax-mean)*mean      fails:", fR2, fR2w)
