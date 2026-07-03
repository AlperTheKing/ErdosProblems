import sympy as sp
from math import comb


def phi_expr(b,d,e,f,x,v):
    a=c=u=y=sp.Integer(1)
    m=x*u+x*v+y*v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n**2-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))

def bernstein_coeffs_from_poly(poly, var):
    p = sp.Poly(poly, var)
    deg = p.degree()
    coeffs = [p.coeff_monomial(var**i) for i in range(deg+1)]
    out = []
    for k in range(deg+1):
        s = 0
        for i in range(k+1):
            s += coeffs[i] * sp.Rational(comb(k,i), comb(deg,i))
        out.append(s)
    return out

X,H,R,Q=sp.symbols('X H R Q', nonnegative=True)
V=X+H; x=1+X; v=1+V
W=sp.factor((V*X+V+2*X)/(V+2))
F=R*W; f=1+F
b=sp.factor((x*(1+v)+v-1-f)/f)
S=sp.factor(b-1-V)
D=Q*S; E=(b-1)-D; d=1+D; e=1+E
print('build expr', flush=True)
expr=phi_expr(b,d,e,f,x,v)
num,den=sp.together(expr).as_numer_denom()
print('got num/den', flush=True)
# Clear obviously positive denominator only through numerator; positivity of denominator checked separately later.
R_coeffs = bernstein_coeffs_from_poly(num, R)
print('after R', len(R_coeffs), flush=True)
all_bad=[]; total=0; global_min=None
for i,rc in enumerate(R_coeffs):
    q_coeffs = bernstein_coeffs_from_poly(rc, Q)
    print('Ridx', i, 'Qcount', len(q_coeffs), flush=True)
    for j,qc in enumerate(q_coeffs):
        poly = sp.Poly(sp.expand(qc), X, H)
        coeffs = [sp.Integer(c) for c in poly.coeffs()]
        total += len(coeffs)
        m = min(coeffs)
        if global_min is None or m < global_min:
            global_min = m
        bad = sum(1 for c in coeffs if c < 0)
        if bad:
            all_bad.append((i,j,len(coeffs),m,bad))
            print('BAD', all_bad[-1], flush=True)
            raise SystemExit(2)
print('DONE total', total, 'min', global_min, 'bad', all_bad, flush=True)
PY
