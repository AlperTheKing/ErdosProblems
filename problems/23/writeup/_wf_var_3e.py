"""Spectral route via K=P P^T.  We have (rows=bad edges):
  row_f = (K 1)_f = sum_g K_{fg}.
  Q_f = sum_v p_f(v) S(v)^2 = sum_v p_f(v)(sum_g p_g(v))(sum_h p_h(v)) = sum_{g,h} (sum_v p_f(v)p_g(v)p_h(v)) =: sum_{g,h} T_{fgh}.
This 3-tensor is not K. But consider the vector x_f with (x_f)_v = p_f(v). Then:
  row_f = x_f . S,  Q_f = x_f . (S.^2) [elementwise].  S = P^T 1 (S_v = sum_g p_g v = (P^T 1)_v).
Try: var_f = ell_f * Var_{mu_f}(S).  Want N(N-row)>=var.

Alternative proven-fact route: maybe use the GLOBAL identity sum_f row_f relationship or per-vertex.
Test the KEY structural inequality that would close it WITHOUT Smax/Smin:
   CLAIM C:  var_f <= (N - mean) * (something proven).   Recall var = ell*Var(S), mean=row/ell.
   Test:  var_f <= (N - row_f) * mean   ??     (note RHS small)  -> would give N(N-row)>=var if mean<=N (true) BUT need var<=(N-row)*mean*?  check N(N-row) vs (N-row)*mean: N(N-row)>=(N-row)mean iff N>=mean (true). So if var<=(N-row)*mean we are DONE via N(N-row)>=N*... wait need var<=N(N-row). (N-row)*mean<=(N-row)*N? no mean<=N so (N-row)mean<=(N-row)N=N(N-row) only if N-row>=0 (true). GOOD. So CLAIM C: var_f<=(N-row_f)*mean_f  would suffice.
   Test CLAIM C and variants:
     C1: var <= (N-row)*mean
     C2: var <= (N-mean)*mean*ell  (=Bhatia-Davis with [0,N], = ell(N-mean)mean) -> = Bridge-A-ish, known insufficient? check
     C3: var <= (N-row)             (very strong)
     C4: var <= mean*(N-mean)       (per-unit)
"""
from fractions import Fraction as F
import _wf_var_3d_data as D
data=D.data
cnt={'C1':0,'C2':0,'C3':0,'C4':0}
w={'C1':None,'C2':None,'C3':None,'C4':None}
# also: does C1 + (mean<=N) actually give main? verify directly main from C1.
mainfromC1_fail=0
for rec in data:
    name,n,f,ll,row,Q,var,Smax,Smin,pfmin=rec
    N=F(n); mean=row/ll
    tests={
      'C1': (N-row)*mean,
      'C2': ll*(N-mean)*mean,
      'C3': (N-row),
      'C4': mean*(N-mean),
    }
    for k,rhs in tests.items():
        if var>rhs:
            cnt[k]+=1
            d=(var-rhs,name,n,f)
            if w[k] is None or d[0]>w[k][0]: w[k]=d
    # if C1 holds, main: N(N-row)-var >= N(N-row)-(N-row)mean=(N-row)(N-mean)>=0 since row<=N,mean<=N
    if var<=(N-row)*mean and N*(N-row)-var<0: mainfromC1_fail+=1
print("rows",len(data))
for k in ['C1','C2','C3','C4']:
    print(f"{k} fails:",cnt[k], "worst-excess:", w[k])
print("sanity (C1 => main) inconsistencies:", mainfromC1_fail)
