import sympy as sp
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction
E,U,X,Yv,Rv,Dv=sp.symbols('E U X Yv Rv Dv')
e,u,x,y,R,D=sp.symbols('e u x y R D')
P=x+y; q=u+e; Yexpr=e*P+u*x
def FN(N,u,x,e,Y,D): return 2*N**2 + 4*u*N*x/e - 50*Y - 75*Y/e + 75*D
def target(C):
    N0=D+P+q+R+1+(Yexpr-C)/R
    return sp.expand(e*R**2*(FN(N0,u,x,e,Yexpr,D)-15))
TA=target(e)
vars=(E,U,X,Yv,Rv,Dv)
subs={e:1+E,u:1+U,x:1+X,y:1+Yv,R:1+Rv,D:1+Dv}
Q=sp.Poly(sp.expand(TA.subs(subs)), *vars)
slacks=[
    sp.Poly((1+Rv)-((1+X)+(1+Yv)), *vars), # R-P
    sp.Poly((1+Dv)-((1+U)+(1+E)), *vars), # D-q
    sp.Poly((1+Dv)-(1+Rv), *vars), # D-R
    sp.Poly((1+Rv)-(1+E)-1, *vars), # R-e-1
]
# also variable nonnegativity is coefficient cone.
def gen(n,deg,prefix=()):
    if n==1: yield prefix+(deg,)
    else:
        for i in range(deg+1): yield from gen(n-1, deg-i, prefix+(i,))
for md in [1,2,3,4]:
    mons=[]
    for total in range(md+1): mons += list(gen(6,total))
    cols=[]
    for si,S in enumerate(slacks):
        for m in mons:
            cols.append((si,m))
    allmons=set(Q.monoms())
    for si,m in cols:
        S=slacks[si]
        for gm in S.monoms(): allmons.add(tuple(a+b for a,b in zip(m,gm)))
    allmons=sorted(allmons, reverse=True); idx={m:i for i,m in enumerate(allmons)}
    c=np.array([float(Q.coeff_monomial(m)) for m in allmons])
    A=np.zeros((len(allmons), len(cols)))
    for j,(si,m) in enumerate(cols):
        S=slacks[si]
        for gm,gc in zip(S.monoms(),S.coeffs()): A[idx[tuple(a+b for a,b in zip(m,gm))],j]+=float(gc)
    res=linprog(np.zeros(len(cols)), A_ub=A, b_ub=c, bounds=[(0,None)]*len(cols), method='highs')
    print('md',md,'feasible',res.success,'vars',len(cols),'constraints',len(allmons),res.message)
    if res.success:
        lams=[Fraction(float(v)).limit_denominator(1000000) for v in res.x]
        mult=0
        for (si,m),fr in zip(cols,lams):
            if fr:
                mult += sp.Rational(fr.numerator,fr.denominator)*sp.prod(v**a for v,a in zip(vars,m))*slacks[si].as_expr()
        Rem=sp.Poly(sp.expand(Q.as_expr()-mult), *vars)
        neg=[c for c in Rem.coeffs() if c<0]
        print(' exact neg',len(neg),'min',min(Rem.coeffs()),'mult_terms',sum(1 for fr in lams if fr))
        if not neg:
            print(' success md',md); break
        else: print([(mo,co) for mo,co in zip(Rem.monoms(),Rem.coeffs()) if co<0][:10])
