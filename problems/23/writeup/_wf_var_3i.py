"""Find a PROVEN bound on the spread of S over supp(f) sufficient to make BD-bridge work from {N,row,ell}.
BD bridge needs (validated): N(N-row) >= ell*(Smax-mean)(mean-Smin).
Sufficient closed form: if we can prove  Smax-Smin <= W  and the bridge
   N(N-row) >= ell*(W/2)^2  (Popoviciu)  -- test if Popoviciu form with various W closes.
Also test the most promising EXACT-grounded closer:
   E1: var <= (N-row)*(N-mean)         [holds? implies main? N(N-row)>=(N-row)(N-mean) iff N>=mean YES => E1 IMPLIES main]
   E2: var <= (N-row)*(N-row/ell)
   E3: var <= (N-mean)^2
Check E1/E2/E3 hold 0-fail AND implication."""
from fractions import Fraction as F
import _wf_var_3d_data as D
data=D.data
cls={
 'E1_(N-row)(N-mean)': (lambda N,row,ell,mean:(N-row)*(N-mean), lambda N,row,ell,mean:(N-row)*(N-mean)<=N*(N-row)),
 'E2_(N-row)(N-row/ell)':(lambda N,row,ell,mean:(N-row)*(N-mean), None),
 'E3_(N-mean)^2': (lambda N,row,ell,mean:(N-mean)*(N-mean), None),
 'E4_(N-row)*N/ (1)': (lambda N,row,ell,mean:(N-row)*N - (N-row)*mean, None), #=(N-row)(N-mean) same as E1
}
rows=len(data)
for name,(fn,impl) in cls.items():
    fh=0; wh=None; fi=0; wi=None
    for rec in data:
        nm,n,f,ll,row,Q,var,Smax,Smin,pfmin=rec
        N=F(n); mean=row/ll; rhs=fn(N,row,ll,mean)
        if var>rhs:
            fh+=1; d=(var-rhs,nm,n,f)
            if wh is None or d[0]>wh[0]: wh=d
        if rhs>N*(N-row):
            fi+=1; d=(rhs-N*(N-row),nm,n,f)
            if wi is None or d[0]>wi[0]: wi=d
    print(f"{name}: hold-fails={fh} (worst {wh}); imply-fails(rhs<=N(N-row))={fi} (worst {wi})")
print("rows",rows)
