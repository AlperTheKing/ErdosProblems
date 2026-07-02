import sympy as sp

def check(cap):
    a,b,c,e,f=sp.symbols('a b c e f', positive=True); vars_=(b,c,e,f); d=sp.Integer(1); u=sp.Integer(1); y=sp.Integer(1); v=e; x=b+c-1
    S=a+b+c+d+e+f; N=S+x+y+u+v; m=x*u+x*v+y*v
    Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c); A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}; sl={name:expr-m for name,expr in caps.items()}
    sola=sp.solve(sp.Eq(sl[cap],0),a)[0]
    Phi=2*(N*N-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-S)
    Ph=sp.factor(Phi.subs(a,sola))
    for var in [f,b,c,e]:
        num=sp.together(sp.diff(Ph,var)).as_numer_denom()[0]
        xs=sp.symbols('x0:4'); sh={b:xs[0]+1,c:xs[1]+1,e:xs[2]+1,f:xs[3]+1}
        P=sp.Poly(sp.expand(num.subs(sh)),*xs)
        coeff=[cc for m,cc in P.terms()]
        print(cap,var,'terms',len(coeff),'min',min(coeff),'neg',sum(1 for cc in coeff if cc<0),'const',P.coeff_monomial((0,0,0,0)))
for cap in ['s4','s5','s6','s7']:
    check(cap)
