import sympy as sp
A,C,F,R,H,U=sp.symbols('A C F R H U', nonnegative=True)
vars_=(A,C,F,R,H,U)
a=1+A; c=1+C; f=1+F; e=c+R; x=e+1+U; y=sp.Integer(1); v=e; u=x-e
# s4=0 solve b
b=sp.factor((x**2+e-a*c-c*f)/f)
d=b-R+H
m=x**2+e
N=a+b+c+d+e+f+x+y+u+v; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-(a+b+c+d+e+f))
print('s4', sp.factor(Y-m), 'bnum terms', len(sp.Poly(sp.together(b-1).as_numer_denom()[0], *vars_).terms()), flush=True)
num,den=sp.together(sp.diff(Phi,H)).as_numer_denom(); num=sp.factor(num)
P=sp.Poly(sp.expand(num), *vars_); neg=[(mon,coef) for mon,coef in P.terms() if coef<0]
print('terms',len(P.terms()),'neg',len(neg),'degree',P.total_degree(),'firstneg',neg[:10], flush=True)
print('subs0', sp.factor(num.subs({A:0,C:0,F:0,R:0,H:0,U:0})), flush=True)