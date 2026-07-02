import sympy as sp
X,B0=sp.symbols('X B0', nonnegative=True)
x=X+2
a=x+1; b=2+B0; c=e=v=x-1; d=f=u=y=sp.Integer(1)
m=x*u+x*v+v
N=a+b+c+d+e+f+x+y+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=sp.factor(2*(N*N-25*m)-75*(x*(u+v)*A/Z+v*B/(e*Y)-(a+b+c+d+e+f)))
num,den=sp.together(Phi).as_numer_denom()
for label,expr in [('num',num),('den',den)]:
    poly=sp.Poly(sp.factor(expr),X,B0)
    neg=[coef for mon,coef in poly.terms() if coef<0]
    print(label,'terms',len(poly.terms()),'neg',len(neg), 'origin', expr.subs({X:0,B0:0}))
    if neg: print(sp.factor(expr))