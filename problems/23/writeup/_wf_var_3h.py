"""K=P P^T route (rows=bad edges). For fixed f, let k_g=K_{fg}=sum_v p_f(v)p_g(v) (>=0). row_f=sum_g k_g.
Q_f = sum_v p_f(v)S(v)^2. Express Q_f via K?  S(v)=sum_g p_g(v).
 Q_f=sum_v p_f(v)(sum_g p_g v)(sum_h p_h v)=sum_{g,h} sum_v p_f p_g p_h.
Define A_{gh}=sum_v p_f(v) p_g(v) p_h(v) (depends on f). Then Q_f=sum_{gh}A_{gh}, row_f=sum_g A_{gg}? no: A_{gg}=sum_v p_f p_g^2, but k_g=sum_v p_f p_g. Not equal.
Hmm. Instead consider weighting: row_f=sum_g k_g where k_g=<x_f,x_g>, x_g=(p_g(v))_v.
Q_f=<x_f, S.^2>= sum_v p_f S^2.  By Cauchy-Schwarz-like on the measure mu_f(v)=p_f(v):
  Q_f = E_mu[S^2]*ell = (Var_mu(S)+mean^2)*ell. trivially identity.
KEY proven-fact candidate from prompt: O entrywise>=0, O_ff<=ell(f), rho(O)<=N is to-be-avoided.
Reinterpret O as VERTEX Gram O=P^T P: O_{uv}=sum_g p_g(u)p_g(v)>=0. (O 1)_u=sum_v O_uv=sum_g p_g(u) ell_g.
 diag O_uu=sum_g p_g(u)^2. row_f as prompt: (O 1)_f? but f is an edge not vertex. The prompt notation is loose.
Let me instead test a CLEAN spectral closer that uses only proven O-facts:
  Claim S1:  sum_v p_f(v) S(v)^2 <= N * sum_v p_f(v) S(v)   [=Q<=N*row, i.e. L4, since S<=N]. PROVEN from S<=N. holds.
  Then var=Q-row^2/ell <= N row - row^2/ell. main needs N(N-row)>=N row-row^2/ell i.e. N^2-2N row+row^2/ell>=0.
  Define D:=N^2-2N row+row^2/ell. Test sign of D on gate (this is the gap quantity)."""
from fractions import Fraction as F
import _wf_var_3d_data as D
data=D.data
neg=0; negw=None; rows=len(data)
# D = N^2 - 2N row + row^2/ell  ; main-via-L4 works iff D>=0
for rec in data:
    nm,n,f,ll,row,Q,var,Smax,Smin,pfmin=rec
    N=F(n); Dq=N*N-2*N*row+row*row/ll
    if Dq<0:
        neg+=1
        if negw is None or Dq<negw[0]: negw=(Dq,nm,n,f,str(row),str(ll))
print("rows",rows)
print("gap D=N^2-2N row+row^2/ell  NEGATIVE count:",neg, "worst:",negw)
# So L4 route fails exactly where D<0. Characterize: D<0 iff row in (root1,root2). row=ell*mean.
# D = N^2-2N ell mean + ell mean^2 = ... treat as quadratic in mean: ell mean^2 -2N ell mean + N^2.
# disc=4N^2ell^2-4ell N^2=4N^2 ell(ell-1)>=0 for ell>=1. roots mean=(2Nell +-2N sqrt(ell(ell-1)))/(2ell)=N(1+-sqrt((ell-1)/ell)).
# mean<=N always, and N(1-sqrt((ell-1)/ell))<=mean? D<0 when mean>N(1-sqrt(1-1/ell)). For ell large that's ~N/(2ell)... small.
# So whenever mean>~N/(2ell), L4-route fails. Confirms gap is real and L4 alone insufficient.
