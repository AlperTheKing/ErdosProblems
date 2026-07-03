import sympy as sp
from math import comb

R,S,P,D,E=sp.symbols('R S P D E', nonnegative=True)

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

def phi_expr(b,c,d,e,f,x,v):
    a=u=y=sp.Integer(1)
    m=x*(1+v)+v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))

def make_expr(X,V,q,T,mode,lower):
    x=1+X; v=1+V; M3=sp.factor(X*V+2*X+2*V)
    b=1+T-q; c=1+q; f=sp.cancel((2+M3-q)/(2+T))
    if mode=='tv_ray':
        e=1+V+E; d=1+D
    elif mode=='seg':
        e=1+lower + P*(T-lower); d=2+T-e+D
    elif mode=='ray':
        e=1+T+E; d=1+D
    else:
        raise ValueError(mode)
    return phi_expr(b,c,d,e,f,x,v)

def coeff_stats(expr, unbounded):
    num,den=sp.together(expr).as_numer_denom()
    dp=sp.Poly(den,*unbounded)
    dc=[sp.Integer(c) for c in dp.coeffs()]
    if (not dc) or any(c<=0 for c in dc):
        print('bad denominator', len(dc), min(dc) if dc else None, sum(1 for c in dc if c<=0), flush=True)
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
    worst=None
    for idx,c in enumerate(coeffs):
        st=coeff_stats(c, unbounded)
        if st is None:
            bad += 1; continue
        terms,mn,ng=st
        total += terms; neg += ng
        if minc is None or mn < minc:
            minc=mn; worst=idx
    print(name, 'coeffs',len(coeffs),'terms',total,'min',minc,'neg',neg,'bad',bad,'worst',worst, flush=True)

# A1/A2: T <= V, X <= V, ray only.
X,H=sp.symbols('X H', nonnegative=True)
V=X+H
M3=sp.factor(X*V+2*X+2*V)
q=R*X
T=X+S*H
check('A1_TleV_qleX_ray', make_expr(X,V,q,T,'tv_ray',None), (R,S), (X,H,D,E))
q=X+R*H
T=q+S*(V-q)
check('A2_TleV_qgeX_ray', make_expr(X,V,q,T,'tv_ray',None), (R,S), (X,H,D,E))

# B1: T>=V, q<=V, X<=V. lower e=v.
X,H=sp.symbols('X H', nonnegative=True)
V=X+H
M3=sp.factor(X*V+2*X+2*V)
q=R*V
T=V+S*(M3-q-V)
check('B1_qleV_XleV_seg', make_expr(X,V,q,T,'seg',V), (R,S,P), (X,H,D))
check('B1_qleV_XleV_ray', make_expr(X,V,q,T,'ray',None), (R,S), (X,H,D,E))

# B2: T>=V, q<=V, X>=V. lower e=v.
V,H=sp.symbols('V H', nonnegative=True)
X=V+H
M3=sp.factor(X*V+2*X+2*V)
q=R*V
T=X+S*(M3-q-X)
check('B2_qleV_XgeV_seg', make_expr(X,V,q,T,'seg',V), (R,S,P), (V,H,D))
check('B2_qleV_XgeV_ray', make_expr(X,V,q,T,'ray',None), (R,S), (V,H,D,E))

# C1: T>=V, q>=V, X<=V. lower e=c (q).
X,H=sp.symbols('X H', nonnegative=True)
V=X+H
M3=sp.factor(X*V+2*X+2*V)
q=V+R*(M3/2 - V)
T=q+S*(M3-2*q)
check('C1_qgeV_XleV_seg', make_expr(X,V,q,T,'seg',q), (R,S,P), (X,H,D))
check('C1_qgeV_XleV_ray', make_expr(X,V,q,T,'ray',None), (R,S), (X,H,D,E))

# C2: T>=V, q>=V, X>=V, q<=X. lower e=c.
V,H=sp.symbols('V H', nonnegative=True)
X=V+H
M3=sp.factor(X*V+2*X+2*V)
q=V+R*H
T=X+S*(M3-q-X)
check('C2_qgeV_qleX_seg', make_expr(X,V,q,T,'seg',q), (R,S,P), (V,H,D))
check('C2_qgeV_qleX_ray', make_expr(X,V,q,T,'ray',None), (R,S), (V,H,D,E))

# C3: T>=V, q>=V, X>=V, q>=X. lower e=c.
V,H=sp.symbols('V H', nonnegative=True)
X=V+H
M3=sp.factor(X*V+2*X+2*V)
q=X+R*(M3/2 - X)
T=q+S*(M3-2*q)
check('C3_qgeV_qgeX_seg', make_expr(X,V,q,T,'seg',q), (R,S,P), (V,H,D))
check('C3_qgeV_qgeX_ray', make_expr(X,V,q,T,'ray',None), (R,S), (V,H,D,E))
