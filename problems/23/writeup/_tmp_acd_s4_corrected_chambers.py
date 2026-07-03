import sympy as sp

def phi_expr(b,e,f,x,v):
    a=c=d=u=y=sp.Integer(1)
    m=x*u+x*v+y*v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))

def coeff_stats(expr, vars):
    num, den = sp.together(expr).as_numer_denom()
    poly = sp.Poly(sp.expand(num), *vars)
    coeffs = [sp.Integer(c) for c in poly.coeffs()]
    return len(coeffs), min(coeffs), sum(1 for c in coeffs if c <= 0), num, den

def power_to_bernstein(poly, var):
    p = sp.Poly(sp.expand(poly), var)
    d = p.degree()
    coeffs = [p.coeff_monomial(var**i) for i in range(d+1)]
    out = []
    for k in range(d+1):
        s = 0
        for i in range(k+1):
            s += coeffs[i] * sp.binomial(k, i) / sp.binomial(d, i)
        out.append(sp.factor(s))
    return out

def bernstein_stats(expr, bvar, uvars):
    num, den = sp.together(expr).as_numer_denom()
    bcoeffs = power_to_bernstein(num, bvar)
    bad = []
    mins = []
    total_terms = 0
    for idx, bc in enumerate(bcoeffs):
        poly = sp.Poly(sp.expand(bc), *uvars)
        coeffs = [sp.Integer(c) for c in poly.coeffs()]
        total_terms += len(coeffs)
        m = min(coeffs)
        mins.append(m)
        if any(c <= 0 for c in coeffs):
            bad.append((idx, len(coeffs), m, sum(1 for c in coeffs if c <= 0)))
    return len(bcoeffs), total_terms, min(mins), bad, num, den

# A: s>=X, s=X+H
X,H,R,E,G = sp.symbols('X H R E G', nonnegative=True)
x = 1 + X
s = X + H
b = x + s
U = sp.factor((X**2 + 3*X + s*(1+X))/(X+s+2))
t = R*U
f = 1 + t
v = sp.factor((1 + f*(b+1) - x)/(x+1))
print('A bounded v-1=', sp.factor(v-1))
print('A bounded b-v=', sp.factor(b-v))
exprA = phi_expr(b, b+E, f, x, v)
print('A bounded Bernstein', bernstein_stats(exprA, R, (X,H,E))[:4])

t2 = U + G
f2 = 1 + t2
v2 = sp.factor((1 + f2*(b+1) - x)/(x+1))
print('A unbounded v-b=', sp.factor(v2-b))
exprA2 = phi_expr(b, v2+E, f2, x, v2)
print('A unbounded coeff', coeff_stats(exprA2, (X,H,G,E))[:3])

# B: X>=s, X=S+H2, s=S
S,H2,R2,E2,G2 = sp.symbols('S H2 R2 E2 G2', nonnegative=True)
X2 = S + H2
xB = 1 + X2
sB = S
bB = xB + sB
U2 = sp.factor((X2**2 + 3*X2 + sB*(1+X2))/(X2+sB+2))
L2 = sp.factor(H2/(X2+sB+2))
tB = sp.factor(L2 + R2*(U2-L2))
fB = 1 + tB
vB = sp.factor((1 + fB*(bB+1) - xB)/(xB+1))
print('B bounded v-1=', sp.factor(vB-1))
print('B bounded b-v=', sp.factor(bB-vB))
exprB = phi_expr(bB, bB+E2, fB, xB, vB)
print('B bounded Bernstein', bernstein_stats(exprB, R2, (S,H2,E2))[:4])

tB2 = U2 + G2
fB2 = 1 + tB2
vB2 = sp.factor((1 + fB2*(bB+1) - xB)/(xB+1))
print('B unbounded v-b=', sp.factor(vB2-bB))
exprB2 = phi_expr(bB, vB2+E2, fB2, xB, vB2)
print('B unbounded coeff', coeff_stats(exprB2, (S,H2,G2,E2))[:3])
