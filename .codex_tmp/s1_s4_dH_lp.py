import sympy as sp
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

C,R,U,H,A0,F=sp.symbols('C R U H A0 F', nonnegative=True)
vars=(C,R,U,H,A0,F)
c=1+C; e=c+R; x=e+1+U; a=1+A0; f=1+F
S=sp.factor((x*x+e-a*c)/f - x - 1)
Snum=sp.factor(sp.together(S).as_numer_denom()[0])
b=x+1-c+S; d=b-R+H; y=1; v=e; q=x; u=x-e; m=x*x+e
N=a+b+c+d+e+f+x+y+u+v
Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*q*AA/Z+v*BB/(e*Y)-(a+b+c+d+e+f))
P=sp.Poly(sp.expand(sp.together(sp.diff(Phi,H)).as_numer_denom()[0]), *vars)
print('target terms', len(P.terms()), 'neg', sum(1 for _,coef in P.terms() if coef<0), 'deg', P.total_degree())
print('Snum', Snum)

def monoms(n,d):
    if n==0:
        yield ()
    elif n==1:
        for i in range(d+1): yield (i,)
    else:
        for i in range(d+1):
            for rest in monoms(n-1,d-i): yield (i,)+rest

for deg in range(0,5):
    cands=list(monoms(len(vars),deg))
    polys=[]
    for mono in cands:
        expr=Snum
        for var,pow in zip(vars,mono): expr*=var**pow
        polys.append(sp.Poly(sp.expand(expr), *vars))
    all_m=set(P.monoms())
    for poly in polys: all_m.update(poly.monoms())
    all_m=sorted(all_m)
    idx={m:i for i,m in enumerate(all_m)}
    rows=[]; cols=[]; vals=[]
    rhs=np.zeros(len(all_m), dtype=float)
    for m,coef in zip(P.monoms(), P.coeffs()): rhs[idx[m]]=float(coef)
    for j,poly in enumerate(polys):
        for m,coef in zip(poly.monoms(), poly.coeffs()):
            rows.append(idx[m]); cols.append(j); vals.append(float(coef))
    A=coo_matrix((vals,(rows,cols)), shape=(len(all_m), len(cands))).tocsr()
    # Need P - A lam >=0 => A lam <= rhs
    res=linprog(np.zeros(len(cands)), A_ub=A, b_ub=rhs, bounds=(0,None), method='highs')
    print('deg',deg,'rows',len(all_m),'cands',len(cands),'success',res.success,'minrhs',rhs.min())
    if res.success:
        print('nz', sum(res.x>1e-9)); break
