import sympy as sp
from math import comb

X,V,R,S,D,E=sp.symbols('X V R S D E', nonnegative=True)

def bernstein_coeffs(poly,var):
    p=sp.Poly(poly,var)
    deg=p.degree()
    coeff=[p.coeff_monomial(var**i) for i in range(deg+1)]
    out=[]
    for k in range(deg+1):
        c=0
        for i in range(k+1):
            c += coeff[i]*sp.Rational(comb(k,i), comb(deg,i))
        out.append(sp.factor(c))
    return out

def phi_expr(b,c,d,e,x,v):
    a=f=u=y=sp.Integer(1)
    m=x*(1+v)+v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))

def coeff_stats(expr, unbounded):
    num,den=sp.together(expr).as_numer_denom()
    dp=sp.Poly(den,*unbounded)
    dc=[sp.Integer(c) for c in dp.coeffs()]
    if not dc or any(c<=0 for c in dc):
        print('bad denominator', len(dc), min(dc) if dc else None, sum(1 for c in dc if c<=0))
        return None
    p=sp.Poly(num,*unbounded)
    cs=[sp.Integer(c) for c in p.coeffs()]
    return len(cs), min(cs), sum(1 for c in cs if c<0)

def check(name, expr, bounded, unbounded):
    num,_=sp.together(expr).as_numer_denom()
    coeffs=[num]
    for var in bounded:
        nxt=[]
        for c in coeffs:
            nxt.extend(bernstein_coeffs(c,var))
        coeffs=nxt
    total=0; minc=None; neg=0; bad=0
    for c in coeffs:
        st=coeff_stats(c, unbounded)
        if st is None:
            bad+=1; continue
        terms,mn,ng=st
        total += terms; neg += ng; minc = mn if minc is None else min(minc,mn)
    print(name, 'coeffs',len(coeffs),'terms',total,'min',minc,'neg',neg,'bad',bad, flush=True)

x=1+X; v=1+V; m=x*(1+v)+v; M3=sp.factor(m-3)
# q <= V chamber
q=R*V
b=1+M3-2*q; c=1+q; H=1+M3-q
# segment e v..H, d=b+c-e+D
e=v+S*(H-v); d=b+c-e+D
check('q_le_v_segment', phi_expr(b,c,d,e,x,v), (R,S), (X,V,D))
# ray e=H+E, d=1+D
e=H+E; d=1+D
check('q_le_v_ray', phi_expr(b,c,d,e,x,v), (R,), (X,V,D,E))
# q >= V chamber
width=sp.factor(M3/2 - V)
q=V+R*width
b=1+M3-2*q; c=1+q; H=1+M3-q
# segment e c..H, d=b+c-e+D
e=c+S*(H-c); d=b+c-e+D
check('q_ge_v_segment', phi_expr(b,c,d,e,x,v), (R,S), (X,V,D))
# ray e=H+E, d=1+D
e=H+E; d=1+D
check('q_ge_v_ray', phi_expr(b,c,d,e,x,v), (R,), (X,V,D,E))
