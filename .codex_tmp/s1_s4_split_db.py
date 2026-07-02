import sympy as sp
B,C,F,R,K,U=sp.symbols('B C F R K U', nonnegative=True)
vars_=(B,C,F,R,K,U)
b=1+B; c=1+C; f=1+F; e=c+R; x=e+1+U; y=sp.Integer(1); v=e; u=x-e
d=b+K
a=sp.factor((x**2+e-f*(b+c))/c)
m=x**2+e
N=a+b+c+d+e+f+x+y+u+v; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-(a+b+c+d+e+f))
print('s4',sp.factor(Y-m),'H',sp.factor(d+e-b-c), flush=True)
for var in [K,R]:
    num=sp.Poly(sp.expand(sp.together(sp.diff(Phi,var)).as_numer_denom()[0]), *vars_)
    neg=[(mon,coef) for mon,coef in num.terms() if coef<0]
    print('d',var,'terms',len(num.terms()),'neg',len(neg),'degree',num.total_degree(),'firstneg',neg[:8],'subs0',num.as_expr().subs({vv:0 for vv in vars_}), flush=True)