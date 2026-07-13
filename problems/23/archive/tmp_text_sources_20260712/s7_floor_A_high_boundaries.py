import sympy as sp
E,X,Yv,r,h,d=sp.symbols('E X Yv r h d', nonnegative=True)
e,u,x,y,R,D=sp.symbols('e u x y R D')
P=x+y; q=u+e; Yexpr=e*P+u*x
def FN(N,u,x,e,Y,D): return 2*N**2 + 4*u*N*x/e - 50*Y - 75*Y/e + 75*D
def target(C):
    N0=D+P+q+R+1+(Yexpr-C)/R
    return sp.expand(e*R**2*(FN(N0,u,x,e,Yexpr,D)-15))
TA=target(e)
def pst(name,subs,vars):
    Q=sp.Poly(sp.expand(TA.subs(subs)), *vars)
    coeffs=Q.coeffs(); neg=[(m,c) for m,c in zip(Q.monoms(), coeffs) if c<0]
    print(name,'terms',len(coeffs),'neg',len(neg),'min',min(coeffs),'deg',Q.total_degree())
    if neg: print('first',neg[:12])
# F4A-high: P=e+1+X+Y, R=P+r.
Rexpr=(1+E)+1+X+Yv+r
base={e:1+E,x:1+X,y:1+E+Yv,R:Rexpr}
# q=D boundary: D=q, and D>=R means u = R-e + h? q=D, D-R=h => e+u=R+h => u=R+h-e=1+X+Y+r+h
subs=base|{u:1+X+Yv+r+h,D:Rexpr+h}
pst('high_qD_boundary',subs,(E,X,Yv,r,h))
# R=D boundary: D=R, q<=D => u = R-e-h = 1+X+Y+r-h, bounded h. Not direct nonneg. endpoint q=D with h=0 below.
subs=base|{u:1+X+Yv+r,D:Rexpr}
pst('high_qD_and_RD',subs,(E,X,Yv,r))
# u minimum boundary u=1, D=R+d
subs=base|{u:1,D:Rexpr+d}
pst('high_u1_DR',subs,(E,X,Yv,r,d))
# derivative wrt u under D=R+d high substitution
U=sp.symbols('U')
subsD=base|{u:1+U,D:Rexpr+d}
Q=sp.expand(TA.subs(subsD))
der=sp.Poly(sp.diff(Q,U), E,U,X,Yv,r,d)
coeffs=der.coeffs(); neg=[(m,c) for m,c in zip(der.monoms(),coeffs) if c<0]
print('der_U_DR terms',len(coeffs),'neg',len(neg),'min',min(coeffs),'deg',der.total_degree())
if neg: print('first der neg',neg[:12])
# negative derivative? check -der maybe
nder=sp.Poly(-sp.diff(Q,U), E,U,X,Yv,r,d)
coeffs=nder.coeffs(); neg=[(m,c) for m,c in zip(nder.monoms(),coeffs) if c<0]
print('minus_der_U_DR terms',len(coeffs),'neg',len(neg),'min',min(coeffs),'deg',nder.total_degree())
if neg: print('first -der neg',neg[:12])
