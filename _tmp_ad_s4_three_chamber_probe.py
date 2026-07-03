import sympy as sp
from math import comb

X,V,R,S,E=sp.symbols('X V R S E', nonnegative=True)
a=d=u=y=sp.Integer(1)
x=1+X
v=1+V
m=x*(1+v)+v
M3=sp.factor(m-3)
assert M3 == X*V+2*X+2*V

def phi_expr(b,c,e,f):
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    n=a+b+c+d+e+f+x+y+u+v
    return 2*(n**2-25*m)-75*(x*(u+v)*A/Z + y*v*B/(e*Y) - (a+b+c+d+e+f))

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

def run(name,t,q,e):
    c=1+q
    b=1+t-q
    f=sp.cancel((m-c)/(b+c))
    print(name,'fminus1',sp.factor(f-1), flush=True)
    ph=phi_expr(b,c,e,f)
    num,den=sp.together(ph).as_numer_denom()
    coeffs=[num]
    for var in (R,S):
        nxt=[]
        for co in coeffs:
            nxt.extend(bern(co,var))
        coeffs=nxt
        print(name,'after',var,len(coeffs),flush=True)
    total=0; mn=None; bad=[]
    for i,co in enumerate(coeffs):
        st=stats(co,(X,V,E))
        total += st[0]
        mn = st[1] if mn is None else min(mn,st[1])
        if st[2] or st[1] < 0:
            bad.append((i,st))
            print('BAD',bad[-1],flush=True)
            break
    print(name,'DONE',len(coeffs),total,mn,bad[:5],flush=True)

# A: 0 <= t <= V, q <= t, e=v+E
tA=R*V
qA=S*tA
eA=v+E
run('A_t_le_V',tA,qA,eA)

# B: V <= t <= M3/2, q <= t, e=1+t+E
widthB=sp.factor(M3/2 - V)
tB=V + R*widthB
qB=S*tB
eB=1+tB+E
run('B_mid',tB,qB,eB)

# C: M3/2 <= t <= M3, q <= M3-t, e=1+t+E
tC=M3/2 + R*M3/2
qC=S*(M3-tC)
eC=1+tC+E
run('C_high',tC,qC,eC)
