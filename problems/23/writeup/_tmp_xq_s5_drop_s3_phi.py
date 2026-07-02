import sympy as sp

def bern(poly,var):
    P=sp.Poly(poly,var); n=P.degree(); out=[]
    for i in range(n+1):
        s=0
        for k in range(i+1):
            s += P.coeff_monomial(var**k)*sp.Rational(sp.binomial(i,k), sp.binomial(n,k))
        out.append(sp.factor(s))
    return out

X,R=sp.symbols('X R', nonnegative=True)
x=X+2
b=2+R*(x**2-x-1)
d=b
a=sp.Integer(1); c=e=v=x-1; u=y=sp.Integer(1)
f=x**2/(b+x-1)
m=x*u+x*v+y*v
N=a+b+c+d+e+f+x+y+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=sp.factor(2*(N*N-25*m)-75*(x*(u+v)*A/Z+v*B/(e*Y)-(a+b+c+d+e+f)))
num,den=sp.together(Phi).as_numer_denom()
print('f-1', sp.factor(f-1))
print('s3', sp.factor(b-2))
for label,expr in [('num',num),('den',den)]:
    coeffs=bern(sp.factor(expr),R)
    print(label,'coeffs',len(coeffs))
    for i,c0 in enumerate(coeffs):
        poly=sp.Poly(sp.factor(c0),X)
        neg=[cc for cc in poly.all_coeffs() if cc<0]
        print(' idx',i,'deg',poly.degree(),'neg',len(neg), 'expr', sp.factor(c0) if neg else 'coefpos')