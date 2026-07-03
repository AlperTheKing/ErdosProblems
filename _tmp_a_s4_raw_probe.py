import sympy as sp
R,S,P,D,E=sp.symbols('R S P D E', nonnegative=True)

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
    return phi_expr(b,c,d,e,f,x,v)

def raw(name, expr, vars):
    num,den=sp.together(expr).as_numer_denom()
    p=sp.Poly(num,*vars)
    cs=[sp.Integer(c) for c in p.coeffs()]
    dp=sp.Poly(den,*vars)
    dcs=[sp.Integer(c) for c in dp.coeffs()]
    print(name,'terms',len(cs),'min',min(cs),'neg',sum(1 for c in cs if c < 0),'denmin',min(dcs),'denneg',sum(1 for c in dcs if c <= 0),flush=True)

# Use ordinary cone stats for each chamber parameterization.
X,H=sp.symbols('X H', nonnegative=True); V=X+H; M3=sp.factor(X*V+2*X+2*V)
q=R*X; T=X+S*H; raw('A1_TleV_qleX_ray', make_expr(X,V,q,T,'tv_ray',None), (X,H,R,S,D,E))
q=X+R*H; T=q+S*(V-q); raw('A2_TleV_qgeX_ray', make_expr(X,V,q,T,'tv_ray',None), (X,H,R,S,D,E))
q=R*V; T=V+S*(M3-q-V); raw('B1_qleV_XleV_seg', make_expr(X,V,q,T,'seg',V), (X,H,R,S,P,D))
raw('B1_qleV_XleV_ray', make_expr(X,V,q,T,'ray',None), (X,H,R,S,D,E))
V,H=sp.symbols('V H', nonnegative=True); X=V+H; M3=sp.factor(X*V+2*X+2*V)
q=R*V; T=X+S*(M3-q-X); raw('B2_qleV_XgeV_seg', make_expr(X,V,q,T,'seg',V), (V,H,R,S,P,D))
raw('B2_qleV_XgeV_ray', make_expr(X,V,q,T,'ray',None), (V,H,R,S,D,E))
X,H=sp.symbols('X H', nonnegative=True); V=X+H; M3=sp.factor(X*V+2*X+2*V)
q=V+R*(M3/2 - V); T=q+S*(M3-2*q); raw('C1_qgeV_XleV_seg', make_expr(X,V,q,T,'seg',q), (X,H,R,S,P,D))
raw('C1_qgeV_XleV_ray', make_expr(X,V,q,T,'ray',None), (X,H,R,S,D,E))
V,H=sp.symbols('V H', nonnegative=True); X=V+H; M3=sp.factor(X*V+2*X+2*V)
q=V+R*H; T=X+S*(M3-q-X); raw('C2_qgeV_qleX_seg', make_expr(X,V,q,T,'seg',q), (V,H,R,S,P,D))
raw('C2_qgeV_qleX_ray', make_expr(X,V,q,T,'ray',None), (V,H,R,S,D,E))
q=X+R*(M3/2 - X); T=q+S*(M3-2*q); raw('C3_qgeV_qgeX_seg', make_expr(X,V,q,T,'seg',q), (V,H,R,S,P,D))
raw('C3_qgeV_qgeX_ray', make_expr(X,V,q,T,'ray',None), (V,H,R,S,D,E))

