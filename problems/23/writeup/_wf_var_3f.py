"""C4: var_f <= mean_f*(N-mean_f), mean=row/ell, held 0-fail. Does C4 => main?
main: N(N-row) >= var.  Suppose var <= mean(N-mean). Is mean(N-mean) <= N(N-row)?
  N(N-row) - mean(N-mean) = N^2 - N row - N mean + mean^2 = N^2 - N(row+mean) + mean^2.
  row = ell*mean, so = N^2 - N mean(ell+1) + mean^2. With ell>=2 (nonunique). Not obviously >=0.
So C4 alone may NOT imply main. TEST whether C4 implies main numerically, and find a sufficient PROVEN closer.

Also reconsider: maybe the RIGHT closer is  var <= (N-row)*(N - row/ell)  or uses row<=N AND ell<=N jointly.
Enumerate candidate closers G that (i) hold 0-fail AND (ii) provably imply main.
A closer G(var,N,row,ell) implies main if  G_rhs <= N(N-row) as an ALGEBRAIC identity given 0<=mean<=N, ell>=2, row<=N.
Test set of closers and for each: 0-fail? and  does rhs<=N(N-row) hold 0-fail (the implication side)?"""
from fractions import Fraction as F
import _wf_var_3d_data as D
data=D.data

closers = {
  # name: function(N,row,ell,mean)-> rhs
  'G_C4':   lambda N,row,ell,mean: mean*(N-mean),
  'G_meanNrow': lambda N,row,ell,mean: mean*(N-row),
  'G_rowNrow_over_ell': lambda N,row,ell,mean: row*(N-row)/ell,   # = mean*(N-row)
  'G_Nrow_minus_rowsq_l': lambda N,row,ell,mean: N*row - row*row/ell,  # Bhatia-Davis [0,N]*ell (=C2)
  'G_half': lambda N,row,ell,mean: (N-row)*(N+row)/F(ell+1),
}
rows=len(data)
for name,fn in closers.items():
    fail_hold=0; fail_impl=0; wh=None; wi=None
    for rec in data:
        nm,n,f,ll,row,Q,var,Smax,Smin,pfmin=rec
        N=F(n); mean=row/ll; rhs=fn(N,row,ll,mean)
        if var>rhs:
            fail_hold+=1
            d=(var-rhs,nm,n,f)
            if wh is None or d[0]>wh[0]: wh=d
        if rhs > N*(N-row):
            fail_impl+=1
            d=(rhs-N*(N-row),nm,n,f)
            if wi is None or d[0]>wi[0]: wi=d
    print(f"{name}: var<=rhs fails={fail_hold} (worst {wh}); rhs<=N(N-row) fails={fail_impl} (worst {wi})")
print("rows",rows)
