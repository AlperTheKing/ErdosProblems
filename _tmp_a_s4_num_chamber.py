import sys
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

def make_expr(X,V,q,T,mode,lower):
    x=1+X; v=1+V; M3=sp.expand(X*V+2*X+2*V)
    b=1+T-q; c=1+q; f=sp.cancel((2+M3-q)/(2+T))
    if mode=='tv_ray':
        e=1+V+E; d=1+D
    elif mode=='seg':
        e=1+lower + P*(T-lower); d=2+T-e+D
    elif mode=='ray':
        e=1+T+E; d=1+D
    return phi_expr(b,c,d,e,f,x,v)

def build(name):
    if name in {'A2'}:
        X,H=sp.symbols('X H', nonnegative=True); V=X+H
        q=X+R*H; T=q+S*(V-q)
        return make_expr(X,V,q,T,'tv_ray',None),(R,S),(X,H,D,E)
    if name in {'B1_seg','B1_ray'}:
        X,H=sp.symbols('X H', nonnegative=True); V=X+H; M3=sp.expand(X*V+2*X+2*V)
        q=R*V; T=V+S*(M3-q-V)
        return (make_expr(X,V,q,T,'seg',V),(R,S,P),(X,H,D)) if name.endswith('seg') else (make_expr(X,V,q,T,'ray',None),(R,S),(X,H,D,E))
    if name in {'B2_seg','B2_ray'}:
        V,H=sp.symbols('V H', nonnegative=True); X=V+H; M3=sp.expand(X*V+2*X+2*V)
        q=R*V; T=X+S*(M3-q-X)
        return (make_expr(X,V,q,T,'seg',V),(R,S,P),(V,H,D)) if name.endswith('seg') else (make_expr(X,V,q,T,'ray',None),(R,S),(V,H,D,E))
    if name in {'C1_seg','C1_ray'}:
        X,H=sp.symbols('X H', nonnegative=True); V=X+H; M3=sp.expand(X*V+2*X+2*V)
        q=V+R*(M3/2 - V); T=q+S*(M3-2*q)
        return (make_expr(X,V,q,T,'seg',q),(R,S,P),(X,H,D)) if name.endswith('seg') else (make_expr(X,V,q,T,'ray',None),(R,S),(X,H,D,E))
    if name in {'C2_seg','C2_ray'}:
        V,H=sp.symbols('V H', nonnegative=True); X=V+H; M3=sp.expand(X*V+2*X+2*V)
        q=V+R*H; T=X+S*(M3-q-X)
        return (make_expr(X,V,q,T,'seg',q),(R,S,P),(V,H,D)) if name.endswith('seg') else (make_expr(X,V,q,T,'ray',None),(R,S),(V,H,D,E))
    if name in {'C3_seg','C3_ray'}:
        V,H=sp.symbols('V H', nonnegative=True); X=V+H; M3=sp.expand(X*V+2*X+2*V)
        q=X+R*(M3/2-X); T=q+S*(M3-2*q)
        return (make_expr(X,V,q,T,'seg',q),(R,S,P),(V,H,D)) if name.endswith('seg') else (make_expr(X,V,q,T,'ray',None),(R,S),(V,H,D,E))
    raise SystemExit(f'unknown chamber {name}')

def check(name):
    expr,bounded,unbounded=build(name)
    num,_=sp.together(expr).as_numer_denom()
    coeffs=[sp.expand(num)]
    print('START',name,flush=True)
    for var in bounded:
        nxt=[]
        for cc in coeffs:
            nxt.extend(bernstein_coeffs(cc,var))
        coeffs=nxt
        print(' after',var,'count',len(coeffs),flush=True)
    total=0; minc=None; worst=None; neg=0
    for i,cc in enumerate(coeffs):
        p=sp.Poly(cc,*unbounded)
        cs=[sp.Integer(z) for z in p.coeffs()]
        total+=len(cs)
        mn=min(cs)
        if minc is None or mn<minc:
            minc=mn; worst=i
        ng=sum(1 for z in cs if z<0)
        if ng:
            neg+=ng
            print('FAIL',name,'idx',i,'terms',len(cs),'min',mn,'neg',ng,flush=True)
            return 1
    print('PASS',name,'coeffs',len(coeffs),'terms',total,'min',minc,'neg',neg,'worst',worst,flush=True)
    return 0

if __name__=='__main__':
    sys.exit(check(sys.argv[1]))
