"""Classify Codex's cond3-failing instance (block 117): does canonical cond3 fail while SPEC + conjecture hold?"""
from fractions import Fraction as F
m=7; n=[5,715,303,12,304,12,715]; N=sum(n)
prods=[(n[i]*n[(i+1)%m],i) for i in range(m)]; pmin,a=min(prods); b=(a+1)%m; nbad=n[a]*n[b]
def Pi(i):
    if i==a: return F(n[b])
    if i==b: return F(n[a])
    return F(nbad,n[i])
T=[m*Pi(i) for i in range(m)]
O=[i for i in range(m) if T[i]>N]; Q=[i for i in range(m) if i not in O]
A=sum(F(N)-T[i] for i in Q); B=sum(Pi(i) for i in Q); S=A/(F(N)-B)
cond3=[(p, F(N)-T[p]+Pi(p)*S) for p in O]
rhoK=sum(Pi(i) for i in range(m)); Gamma=m*m*nbad
print("N", N, "minprod edge a", a, "nbad", nbad, "ell", m)
print("O parts", O, " T_O", [round(float(T[p]),2) for p in O])
c3ok = all(v>=0 for _,v in cond3)
print("cond3 canonical O-row margins:", [(p,round(float(v),3)) for p,v in cond3], "-> cond3", "HOLDS" if c3ok else "FAILS")
print("rho(K)=sum Pi =", round(float(rhoK),2), " N=", N, "-> SPEC", "HOLDS" if rhoK<=N else "FAILS")
print("Gamma=ell^2*|M| =", Gamma, " N^2=", N*N, "-> Gamma<=N^2", "HOLDS" if Gamma<=N*N else "FAILS")
print("VERDICT: canonical-cond3", "FAILS" if not c3ok else "holds",
      "| SPEC(rho<=N)", "HOLDS" if rhoK<=N else "FAILS",
      "| conjecture(Gamma<=N^2)", "HOLDS" if Gamma<=N*N else "FAILS")
