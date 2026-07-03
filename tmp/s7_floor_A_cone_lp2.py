import sympy as sp
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction
E,U,X,Yv,r,d=sp.symbols('E U X Yv r d')
e,u,x,y,R,D=sp.symbols('e u x y R D')
P=x+y; q=u+e; Yexpr=e*P+u*x
def FN(N,u,x,e,Y,D): return 2*N**2 + 4*u*N*x/e - 50*Y - 75*Y/e + 75*D
def target(C):
    N0=D+P+q+R+1+(Yexpr-C)/R
    return sp.expand(e*R**2*(FN(N0,u,x,e,Yexpr,D)-15))
TA=target(e)
vars=(E,U,X,Yv,r,d)
Rexpr=(1+E)+1+X+Yv+r
subs={e:1+E,u:1+U,x:1+X,y:1+E+Yv,R:Rexpr,D:(1+E)+(1+U)+d}
Q=sp.Poly(sp.expand(TA.subs(subs)), *vars)
G=sp.Poly(U+d-X-Yv-r, *vars)  # D-R slack in shifted coords
# monomials deg<=4
mons=[]
def gen(n,deg,prefix=()):
    if n==1: yield prefix+(deg,)
    else:
        for i in range(deg+1): yield from gen(n-1, deg-i, prefix+(i,))
for total in range(5): mons += list(gen(6,total))
allmons=set(Q.monoms())
for m in mons:
    for gm in G.monoms(): allmons.add(tuple(a+b for a,b in zip(m,gm)))
allmons=sorted(allmons, reverse=True); idx={m:i for i,m in enumerate(allmons)}
c=np.array([float(Q.coeff_monomial(m)) for m in allmons])
A=np.zeros((len(allmons),len(mons)))
for j,m in enumerate(mons):
    for gm,gc in zip(G.monoms(),G.coeffs()):
        A[idx[tuple(a+b for a,b in zip(m,gm))],j]+=float(gc)
res=linprog(np.zeros(len(mons)), A_ub=A, b_ub=c, bounds=[(0,None)]*len(mons), method='highs')
print('feasible',res.success,res.message,'vars',len(mons),'constraints',len(allmons))
if res.success:
    lams=[Fraction(float(v)).limit_denominator(1000000) for v in res.x]
    mult=sum(sp.Rational(fr.numerator,fr.denominator)*sp.prod(v**a for v,a in zip(vars,m)) for m,fr in zip(mons,lams))
    Rem=sp.Poly(sp.expand(Q.as_expr()-mult*G.as_expr()), *vars)
    neg=[c for c in Rem.coeffs() if c<0]
    print('exact neg',len(neg),'min',min(Rem.coeffs()),'mult_terms',sum(1 for fr in lams if fr))
    if neg: print([(mo,co) for mo,co in zip(Rem.monoms(),Rem.coeffs()) if co<0][:10])
    else: print('nz',[(m,fr) for m,fr in zip(mons,lams) if fr][:20])
