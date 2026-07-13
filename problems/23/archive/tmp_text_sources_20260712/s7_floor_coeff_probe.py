import sympy as sp
E,U,X,Yv,r,d,s = sp.symbols('E U X Yv r d s', nonnegative=True)
e,u,x,y,R,D=sp.symbols('e u x y R D')
P=x+y
q=u+e
Yexpr=e*P+u*x

def FN(N,u,x,e,Y,D):
    return 2*N**2 + 4*u*N*x/e - 50*Y - 75*Y/e + 75*D

def target(C):
    N0=D+P+q+R+1+(Yexpr-C)/R
    return sp.expand(e*R**2*(FN(N0,u,x,e,Yexpr,D)-15))
TA=target(e)
TB=target(R-1)

def stats(poly, subs, vars):
    Q=sp.Poly(sp.expand(poly.subs(subs)), *vars)
    coeffs=Q.coeffs()
    neg=[c for c in coeffs if c<0]
    return len(coeffs), len(neg), min(coeffs), Q
# A substitutions: e,u,x,y >=1, R=P+r, D=R+d. Larger domain except ignores q<=D and e<=R-1.
subs_A1={e:1+E,u:1+U,x:1+X,y:1+Yv,R:(1+X)+(1+Yv)+r,D:(1+X)+(1+Yv)+r+d}
for name,poly,subs,vars in [('A_RP_D_R',TA,subs_A1,(E,U,X,Yv,r,d))]:
    n,nn,m,Q=stats(poly,subs,vars)
    print(name,'terms',n,'neg',nn,'min',m,'degree',Q.total_degree())
    if nn: print('first neg',[(mon,c) for mon,c in zip(Q.monoms(),Q.coeffs()) if c<0][:10])
# A with D=q+d, R=P+r, leaves R<=D not enforced
subs_A2={e:1+E,u:1+U,x:1+X,y:1+Yv,R:(1+X)+(1+Yv)+r,D:(1+E)+(1+U)+d}
n,nn,m,Q=stats(TA,subs_A2,(E,U,X,Yv,r,d))
print('A_RP_Dq terms',n,'neg',nn,'min',m,'degree',Q.total_degree())
if nn: print('first neg',[(mon,c) for mon,c in zip(Q.monoms(),Q.coeffs()) if c<0][:10])
# B substitution: R=P+r, e=R-1+s, D=R+d. Covers e>=R-1, P<=R, D>=R; q<=D not enforced.
Rexpr=(1+X)+(1+Yv)+r
subs_B1={R:Rexpr,e:Rexpr-1+s,u:1+U,x:1+X,y:1+Yv,D:Rexpr+d}
n,nn,m,Q=stats(TB,subs_B1,(U,X,Yv,r,d,s))
print('B_eR_D_R terms',n,'neg',nn,'min',m,'degree',Q.total_degree())
if nn: print('first neg',[(mon,c) for mon,c in zip(Q.monoms(),Q.coeffs()) if c<0][:10])
# B with D=q+d after e substitution
subs_B2={R:Rexpr,e:Rexpr-1+s,u:1+U,x:1+X,y:1+Yv,D:(Rexpr-1+s)+(1+U)+d}
n,nn,m,Q=stats(TB,subs_B2,(U,X,Yv,r,d,s))
print('B_eR_Dq terms',n,'neg',nn,'min',m,'degree',Q.total_degree())
if nn: print('first neg',[(mon,c) for mon,c in zip(Q.monoms(),Q.coeffs()) if c<0][:10])
