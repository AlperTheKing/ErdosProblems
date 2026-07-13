import sympy as sp
E,U,X,Yv,r,d=sp.symbols('E U X Yv r d')
e,u,x,y,R,D=sp.symbols('e u x y R D')
P=x+y; q=u+e; Yexpr=e*P+u*x
def FN(N,u,x,e,Y,D): return 2*N**2 + 4*u*N*x/e - 50*Y - 75*Y/e + 75*D
def target(C):
    N0=D+P+q+R+1+(Yexpr-C)/R
    return sp.expand(e*R**2*(FN(N0,u,x,e,Yexpr,D)-15))
TA=target(e)
Rexpr=(1+E)+1+X+Yv+r
subs={e:1+E,x:1+X,y:1+E+Yv,R:Rexpr,u:1+U,D:Rexpr+d}
Q=sp.expand(TA.subs(subs))
polyU=sp.Poly(Q,U)
print('degreeU',polyU.degree())
for i,c in enumerate(reversed(polyU.all_coeffs())):
    # all_coeffs high to low; reversed gives U^0...
    Pcoef=sp.Poly(sp.expand(c), E,X,Yv,r,d)
    coeffs=Pcoef.coeffs(); neg=[(m,cc) for m,cc in zip(Pcoef.monoms(), coeffs) if cc<0]
    print('Ucoeff',i,'terms',len(coeffs),'neg',len(neg),'min',min(coeffs),'degree',Pcoef.total_degree())
    if neg: print(' first',neg[:8])
# second derivative wrt U
sec=sp.Poly(sp.diff(Q,U,2), E,U,X,Yv,r,d)
coeffs=sec.coeffs(); neg=[(m,c) for m,c in zip(sec.monoms(),coeffs) if c<0]
print('second deriv terms',len(coeffs),'neg',len(neg),'min',min(coeffs),'deg',sec.total_degree())
if neg: print('first sec neg',neg[:8])
