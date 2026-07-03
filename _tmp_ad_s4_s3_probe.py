import sympy as sp
from math import comb

R,S,E=sp.symbols('R S E', nonnegative=True)

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

def run(name, Xexpr, Vexpr, texpr, qexpr, eexpr, unbounded):
    a=d=u=y=sp.Integer(1)
    x=1+Xexpr; v=1+Vexpr
    m=x*(1+v)+v
    c=1+qexpr
    b=1+texpr-qexpr
    f=sp.cancel((m-c)/(b+c))
    Y=a*c+b*f+c*f
    Z=eexpr*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*eexpr+b*f+b*eexpr+c*f+c*eexpr+eexpr*f
    B=a*c+a*eexpr+b*f+b*eexpr+c*f+c*eexpr+eexpr*f
    n=a+b+c+d+eexpr+f+x+y+u+v
    phi=2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(eexpr*Y)-(a+b+c+d+eexpr+f))
    num,den=sp.together(phi).as_numer_denom()
    print(name,'fminus1',sp.factor(f-1),flush=True)
    coeffs=[num]
    for var in (R,S):
        nxt=[]
        for co in coeffs:
            nxt.extend(bern(co,var))
        coeffs=nxt
        print(name,'after',var,len(coeffs),flush=True)
    total=0; mn=None; bad=[]
    for i,co in enumerate(coeffs):
        n0,d0=sp.together(co).as_numer_denom()
        dp=sp.Poly(d0,*unbounded)
        dc=[sp.Integer(z) for z in dp.coeffs()]
        assert all(z>0 for z in dc), (name,'den',i,min(dc),sum(1 for z in dc if z<=0))
        p=sp.Poly(n0,*unbounded)
        cs=[sp.Integer(z) for z in p.coeffs()]
        total += len(cs)
        mn = min(cs) if mn is None else min(mn,min(cs))
        neg=sum(1 for z in cs if z<0)
        if neg or min(cs)<0:
            bad.append((i,len(cs),min(cs),neg))
            print('BAD',bad[-1],flush=True)
            break
    print(name,'DONE',len(coeffs),total,mn,bad[:5],flush=True)

# universal high: t in [M3/2,M3]
X,V=sp.symbols('X V', nonnegative=True)
x=1+X; v=1+V; m=x*(1+v)+v; M3=sp.factor(m-3)
t=M3/2 + R*M3/2
q=S*(M3-t)
e=1+t+E
run('C_high_all',X,V,t,q,e,(X,V,E))

# X<=V low/mid, V=X+H
X,H=sp.symbols('X H', nonnegative=True)
V=X+H
x=1+X; v=1+V; m=x*(1+v)+v; M3=sp.factor(m-3)
# low: t in [X,V]
t=X+R*H
q=S*t
e=1+V+E
run('A_x_le_v_low',X,V,t,q,e,(X,H,E))
# mid: t in [V,M3/2]
width=sp.factor(M3/2 - V)
t=V+R*width
q=S*t
e=1+t+E
run('B_x_le_v_mid',X,V,t,q,e,(X,H,E))

# X>=V mid, X=V+H
V,H=sp.symbols('V H', nonnegative=True)
X=V+H
x=1+X; v=1+V; m=x*(1+v)+v; M3=sp.factor(m-3)
width=sp.factor(M3/2 - X)
t=X+R*width
q=S*t
e=1+t+E
run('B_x_ge_v_mid',X,V,t,q,e,(V,H,E))
