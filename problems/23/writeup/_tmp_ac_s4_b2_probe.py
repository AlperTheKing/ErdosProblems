import sympy as sp

def phi_expr(b,d,e,f,x,v):
    a=c=u=y=sp.Integer(1)
    m=x*u+x*v+y*v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))

def power_to_bernstein(poly,var):
    p=sp.Poly(sp.expand(poly),var); deg=p.degree(); pc=[p.coeff_monomial(var**i) for i in range(deg+1)]
    out=[]
    for k in range(deg+1):
        s=0
        for i in range(k+1): s += pc[i]*sp.binomial(k,i)/sp.binomial(deg,i)
        out.append(sp.factor(s))
    return out
X,H,R,G=sp.symbols('X H R G', nonnegative=True)
V=X+H; x=1+X; v=1+V
U=sp.factor(V+X/(X+2)); W=sp.factor((V*X+V+2*X)/(V+2))
F=sp.factor(W+R*(U-W)); f=1+F
b=sp.factor((x*(1+v)+v-1-f)/f)
D=G; E=V; d=1+D; e=1+E
print('v-b=', sp.factor(v-b), flush=True)
expr=phi_expr(b,d,e,f,x,v)
num,den=sp.together(expr).as_numer_denom()
print('den expanded', flush=True)
bs=power_to_bernstein(num,R)
print('bern count',len(bs), flush=True)
bad=[]; total=0; mins=[]
for idx,bc in enumerate(bs):
    poly=sp.Poly(sp.expand(bc),X,H,G)
    cs=[sp.Integer(c) for c in poly.coeffs()]
    total += len(cs); mins.append(min(cs))
    if any(c<0 for c in cs): bad.append((idx,len(cs),min(cs),sum(1 for c in cs if c<0)))
print('total',total,'min',min(mins),'bad',bad[:10], flush=True)
PY
