import sympy as sp
A,C,D,F,R,H = sp.symbols('A C D F R H', nonnegative=True)
a=1+A; c=1+C; d=1+D; f=1+F; e=c+R; b=d+R+1+H
x=d+e
y=sp.Integer(1)
v=a*c + f*(d+e) - x**2
u=x-v
S=a+b+c+d+e+f
m=x*x+v
N=S+y+x+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-S)
for name,var in [('h',H),('A',A),('F',F),('D',D),('C',C)]:
    der=sp.factor(sp.diff(Phi,var))
    num=sp.factor(sp.together(der).as_numer_denom()[0])
    poly=sp.Poly(sp.expand(num), A,C,D,F,R,H)
    coeffs=[coef for mon,coef in poly.terms()]
    neg=sum(1 for coef in coeffs if coef<0); pos=sum(1 for coef in coeffs if coef>0)
    print(name, 'terms',len(coeffs),'pos',pos,'neg',neg,'totaldeg',poly.total_degree())
    print('factor head', str(num)[:240])
