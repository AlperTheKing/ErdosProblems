import sympy as sp
from math import comb
X,H,R,S,D,E=sp.symbols('X H R S D E', nonnegative=True)

def bernstein_coeffs(poly,var):
    p=sp.Poly(poly,var)
    deg=p.degree()
    coeff=[p.coeff_monomial(var**i) for i in range(deg+1)]
    out=[]
    for k in range(deg+1):
        c=0
        for i in range(k+1):
            c += coeff[i]*sp.Rational(comb(k,i), comb(deg,i))
        out.append(sp.expand(c))
    return out

def phi_expr(b,c,d,e,f,x,v):
    a=u=y=sp.Integer(1)
    m=x*(1+v)+v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))
V=X+H; x=1+X; v=1+V; M3=sp.expand(X*V+2*X+2*V)
q=R*X; T=X+S*H
b=1+T-q; c=1+q; f=sp.cancel((2+M3-q)/(2+T))
e=1+V+E; d=1+D
expr=phi_expr(b,c,d,e,f,x,v)
num,den=sp.together(expr).as_numer_denom()
print('num built', flush=True)
coeffs=[sp.expand(num)]
for var in (R,S):
    nxt=[]
    for cc in coeffs:
        nxt.extend(bernstein_coeffs(cc,var))
    coeffs=nxt
    print('after',var,'count',len(coeffs), flush=True)
neg=0; total=0; minc=None; worst=None
for i,cc in enumerate(coeffs):
    p=sp.Poly(cc,X,H,D,E)
    cs=[sp.Integer(z) for z in p.coeffs()]
    total += len(cs)
    mn=min(cs)
    if minc is None or mn < minc:
        minc=mn; worst=i
    ng=sum(1 for z in cs if z<0)
    neg += ng
    if ng:
        print('bad coeff index',i,'terms',len(cs),'min',mn,'neg',ng, flush=True)
        break
print('A1 numerator-only coeffs',len(coeffs),'terms',total,'min',minc,'neg',neg,'worst',worst, flush=True)
