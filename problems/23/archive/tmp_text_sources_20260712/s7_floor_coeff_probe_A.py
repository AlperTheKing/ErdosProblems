import sympy as sp
E,U,X,Yv,r,d,p = sp.symbols('E U X Yv r d p', nonnegative=True)
e,u,x,y,R,D=sp.symbols('e u x y R D')
P=x+y; q=u+e; Yexpr=e*P+u*x
def FN(N,u,x,e,Y,D): return 2*N**2 + 4*u*N*x/e - 50*Y - 75*Y/e + 75*D
def target(C):
    N0=D+P+q+R+1+(Yexpr-C)/R
    return sp.expand(e*R**2*(FN(N0,u,x,e,Yexpr,D)-15))
TA=target(e)
def stats(name,subs,vars):
    Q=sp.Poly(sp.expand(TA.subs(subs)), *vars)
    coeffs=Q.coeffs(); neg=[c for c in coeffs if c<0]
    print(name,'terms',len(coeffs),'neg',len(neg),'min',min(coeffs),'degree',Q.total_degree())
    if neg: print('first neg',[(mon,c) for mon,c in zip(Q.monoms(),coeffs) if c<0][:12])
# A: use R=e+1+r, x,y>=1, P<=R not enforced, D=q+d
Rexpr=(1+E)+1+r
stats('A_Re_Dq', {e:1+E,u:1+U,x:1+X,y:1+Yv,R:Rexpr,D:(1+E)+(1+U)+d}, (E,U,X,Yv,r,d))
# A: R=e+1+r, D=R+d
stats('A_Re_DR', {e:1+E,u:1+U,x:1+X,y:1+Yv,R:Rexpr,D:Rexpr+d}, (E,U,X,Yv,r,d))
# A subcase P>=e+1: R=P+r, P=e+1+p via y=e+1+p-x? use x=1+X, e=1+E, y= e+1+p-x; require y>=1 => p>=X? set p=X+Yv.
# Then P=e+1+X+Yv, y=1+E+1+X+Yv-(1+X)=1+E+Yv.
Rexpr2=(1+E)+1+X+Yv+r
subs={e:1+E,u:1+U,x:1+X,y:1+E+Yv,R:Rexpr2,D:(1+E)+(1+U)+d}
stats('A_P_ge_e_Dq', subs, (E,U,X,Yv,r,d))
subs={e:1+E,u:1+U,x:1+X,y:1+E+Yv,R:Rexpr2,D:Rexpr2+d}
stats('A_P_ge_e_DR', subs, (E,U,X,Yv,r,d))
# A subcase e+1>=P: set R=e+1+r and e+1=P+p. Let e=1+E, x=1+X, y=1+Y, need p=e+1-P>=0. Set e+1=P+p -> e=1+X+Yv+p? Use p var; x=1+X,y=1+Yv,e=1+X+Yv+p.
Rexpr3=(1+X+Yv+p)+1+r
subs={e:1+X+Yv+p,u:1+U,x:1+X,y:1+Yv,R:Rexpr3,D:(1+X+Yv+p)+(1+U)+d}
stats('A_e_ge_P_Dq', subs, (U,X,Yv,p,r,d))
subs={e:1+X+Yv+p,u:1+U,x:1+X,y:1+Yv,R:Rexpr3,D:Rexpr3+d}
stats('A_e_ge_P_DR', subs, (U,X,Yv,p,r,d))
