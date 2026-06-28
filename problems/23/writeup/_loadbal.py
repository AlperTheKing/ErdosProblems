"""Load-balancing view of layer-price feasibility. Total budget sum_v B(v) = sum_f sum_i b_{f,i}
(since sum_{v in I_i} p_f(v)=1). By Cauchy-Schwarz (sum_i b_{f,i})(sum_i 1/b_{f,i}) >= (#layers)^2 = ell(f)^2,
and harmonic sum_i 1/b<=1 => sum_i b_{f,i} >= ell(f)^2. So total budget >= sum_f ell(f)^2 = Gamma, with equality
iff uniform b=ell(f). Feasibility (max_v B(v)<=N) requires spreading total>=Gamma over N vertices each <=N, so
NECESSARY: Gamma <= N^2 (consistent). Verify: (1) total budget at the SOLVER optimum vs Gamma and N^2;
(2) confirm uniform prices give total=Gamma exactly (min total) but max=maxT>N."""
import numpy as np
from _h import dec, loads
from _layerprice_verify import get_prices
from _layerprice import layers_of

for g6 in ["I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?","FCp`_"]:
    n,E=dec(g6); info=loads(n,E); N=n; G=info['G']; M=info['M']; T=info['T']
    b,idx,perf,Ls,_,tstar=get_prices(info)
    # total budget at optimum = sum_f sum_i b_{f,i}
    tot=sum(b[(f,i)] for fi,f in enumerate(M) for i in range(Ls[fi][2]+1))
    # uniform prices total = Gamma, max budget = max T
    maxT=max(float(t) for t in T)
    print(f"{g6:13} N={n} Gamma={G} N^2={n*n} | opt: t*(max-budget)={tstar:.3f} total-budget={tot:.3f} | uniform: total=Gamma={G} max=maxT={maxT:.3f} | Gamma<=N^2:{G<=n*n} total in [Gamma,N^2]:{G-1e-6<=tot<=n*n+1e-6}")
