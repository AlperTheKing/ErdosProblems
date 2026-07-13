import sympy as sp
E,X,Yv,r,d,U=sp.symbols('E X Yv r d U')
e,u,x,y,R,D=sp.symbols('e u x y R D')
P=x+y; q=u+e; Yexpr=e*P+u*x
def FN(N,u,x,e,Y,D): return 2*N**2 + 4*u*N*x/e - 50*Y - 75*Y/e + 75*D
def target(C):
    N0=D+P+q+R+1+(Yexpr-C)/R
    return sp.expand(e*R**2*(FN(N0,u,x,e,Yexpr,D)-15))
TA=target(e)
Rexpr=(1+E)+1+X+Yv+r
subs={e:1+E,x:1+X,y:1+E+Yv,R:Rexpr,u:1+U,D:Rexpr+d}
Q=sp.Poly(sp.expand(TA.subs(subs)), U)
c,b,a = list(reversed(Q.all_coeffs()))
M=X+Yv+r+d
B0=sp.expand(c)
B1=sp.expand(c + b*M/2)
B2=sp.expand(c + b*M + a*M*M)
for name,expr in [('B0',B0),('2B1',2*B1),('B2',B2)]:
    Pcoef=sp.Poly(sp.expand(expr),E,X,Yv,r,d)
    coeffs=Pcoef.coeffs(); neg=[(m,cc) for m,cc in zip(Pcoef.monoms(),coeffs) if cc<0]
    print(name,'terms',len(coeffs),'neg',len(neg),'min',min(coeffs),'degree',Pcoef.total_degree())
    if neg: print('first',neg[:12])
