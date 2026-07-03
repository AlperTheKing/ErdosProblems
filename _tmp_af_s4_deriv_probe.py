import sympy as sp
X,V,R,D,E=sp.symbols('X V R D E', nonnegative=True)
a=f=u=y=sp.Integer(1)
x=1+X; v=1+V; m=x*(1+v)+v; M3=sp.factor(m-3)
c=1+R*M3/2
b=1+(1-R)*M3
# crude boundary candidate: e=max? use e=c+V? no. For derivative test use d=1+D,e=1+E unrestricted.
d=1+D; e=1+E
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
n=a+b+c+d+e+f+x+y+u+v
phi=2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))
for name,expr in [('dD',sp.diff(phi,D)),('dE',sp.diff(phi,E))]:
    num,den=sp.together(expr).as_numer_denom()
    p=sp.Poly(num,R,X,V,D,E)
    cs=[sp.Integer(z) for z in p.coeffs()]
    print(name,'terms',len(cs),'min',min(cs),'neg',sum(1 for z in cs if z<0))
