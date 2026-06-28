"""Verify GPT's (CORR) reformulation of (LPD):
   sum_f sum_{i<j} sqrt(w_fi * w_fj)  <=  (1/2) sum_v (N - S(v)) y_v   for all y>=0,
   w_{f,i}=sum_{v in I_i(f)} y_v p_f(v),  S(v)=sum_g p_g(v).
Algebraically (LPD)<=>(CORR) since (sum_i sqrt w_i)^2 = sum_i w_i + 2 sum_{i<j} sqrt(w_i w_j),
sum_f sum_i w_fi = <S,y>, so (LPD) LHS = <S,y> + 2*sum_f sum_{i<j}sqrt(w_i w_j) <= N sum y
<=> sum_f sum_{i<j}sqrt(w_i w_j) <= (1/2)(N sum y - <S,y>) = (1/2) sum_v (N-S(v)) y_v.
Verify lhs<=rhs on random y + indicators (= (LPD) holds, tight at extremals)."""
import numpy as np, random
from fractions import Fraction as F
from _h import dec, loads
from _layerprice import layers_of

def Svec(info):
    S={}
    for f in info['M']:
        Ps=info['cyc'][f]; nf=len(Ps); cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): S[v]=S.get(v,0.0)+c/nf
    return S

def corr(info,y):
    n=info['n']; N=n; M=info['M']; S=Svec(info)
    lhs=0.0
    for f in M:
        lay,pf,h=layers_of(info,f)
        w=[sum(y[v]*pf[v] for v in lay[i]) for i in range(h+1)]
        for i in range(h+1):
            for j in range(i+1,h+1):
                lhs+=np.sqrt(max(w[i],0.0)*max(w[j],0.0))
    rhs=0.5*sum((N-S.get(v,0.0))*y[v] for v in range(n))
    return lhs,rhs

rng=random.Random(7)
print("=== (CORR) lhs <= rhs (= (LPD)) ===")
for g6 in ["I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?","FCp`_"]:
    n,E=dec(g6); info=loads(n,E); worst=None
    ys=[[1.0]*n]+[[1.0 if v==k else 0.0 for v in range(n)] for k in range(n)]+[[rng.random() for _ in range(n)] for _ in range(40)]
    for y in ys:
        lhs,rhs=corr(info,y)
        if worst is None or (lhs-rhs)>worst: worst=lhs-rhs
    print(f"  {g6:13} N={n}: max(lhs-rhs) over {len(ys)} y = {worst:+.5f}  ({'OK <=0' if worst<=1e-7 else 'FAILS'})")
# N=22 witness
n,E=dec("J???E?pNu\\?"); nn=n*2; EE=[]
for (a,b) in E:
    for i in range(2):
        for j in range(2): EE.append((a*2+i,b*2+j))
info=loads(nn,EE); worst=None
ys=[[1.0]*nn]+[[rng.random() for _ in range(nn)] for _ in range(40)]
for y in ys:
    lhs,rhs=corr(info,y)
    if worst is None or (lhs-rhs)>worst: worst=lhs-rhs
print(f"  J???E?pNu?[2] N={nn}: max(lhs-rhs) = {worst:+.5f}  ({'OK' if worst<=1e-6 else 'FAILS'})")
