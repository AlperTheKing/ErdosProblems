import sympy as sp
from math import comb

X,V,R,E=sp.symbols('X V R E', nonnegative=True)
a=d=f=u=y=sp.Integer(1)
x=1+X
v=1+V
m=x*(1+v)+v
M3=sp.factor(m-3)
c=1+R*M3/2
b=1+(1-R)*M3
e=b+c-1+E
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
n=a+b+c+d+e+f+x+y+u+v
phi=2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))
num,den=sp.together(phi).as_numer_denom()

def bern(poly,var):
    p=sp.Poly(poly,var)
    deg=p.degree()
    coeffs=[p.coeff_monomial(var**i) for i in range(deg+1)]
    out=[]
    for k in range(deg+1):
        s=0
        for i in range(k+1):
            s += coeffs[i]*sp.Rational(comb(k,i), comb(deg,i))
        out.append(sp.factor(s))
    return out

def stats(expr,vars):
    n,d=sp.together(expr).as_numer_denom()
    dp=sp.Poly(d,*vars)
    dc=[sp.Integer(z) for z in dp.coeffs()]
    assert all(z>0 for z in dc), (min(dc), sum(1 for z in dc if z<=0))
    p=sp.Poly(n,*vars)
    cs=[sp.Integer(z) for z in p.coeffs()]
    return len(cs), min(cs), sum(1 for z in cs if z<0)

print('M3', sp.factor(M3))
print('dom', sp.factor((b+c-1)-v))
print('den', stats(den,(R,X,V,E))[:2])
coeffs=bern(num,R)
print('R_count',len(coeffs))
total=0; mn=None; bad=[]
for i,co in enumerate(coeffs):
    st=stats(co,(X,V,E))
    total += st[0]
    mn = st[1] if mn is None else min(mn,st[1])
    if st[2] or st[1] < 0:
        bad.append((i,st))
print('DONE', total, mn, bad[:10])
