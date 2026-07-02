import sympy as sp
a,b,c,d,e,f=sp.symbols('a b c d e f', positive=True)
x=d+e; y=sp.Integer(1)
v=a*c+f*x-x*x; u=x-v
S=a+b+c+d+e+f
m=x*x+v
N=S+y+x+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*A/Z+v*B/(e*Y)-S)
der=sp.diff(Phi,b)
num,den=sp.together(der).as_numer_denom()
print('den factor:', sp.factor(den))
fac=sp.factor(num)
print('num factor head:', str(fac)[:1000])
print('num ops', sp.count_ops(fac))
# try substitute nonneg shifts in numerator only and inspect coefficient signs after multiplying by maybe no denominators
A0,C0,D0,F0,R,H=sp.symbols('A C D F R H', nonnegative=True)
subs={a:1+A0,c:1+C0,d:1+D0,f:1+F0,e:1+C0+R,b:(1+D0)+(R)+1+H}
shift=sp.Poly(sp.expand(fac.subs(subs)), A0,C0,D0,F0,R,H)
coeffs=[coef for mon,coef in shift.terms()]
print('shift terms',len(coeffs),'pos',sum(coef>0 for coef in coeffs),'neg',sum(coef<0 for coef in coeffs),'zero',sum(coef==0 for coef in coeffs),'deg',shift.total_degree())
if any(coef<0 for coef in coeffs):
    print('first neg', next((mon,coef) for mon,coef in shift.terms() if coef<0))
else:
    print('min coef', min(coeffs), 'max', max(coeffs))
