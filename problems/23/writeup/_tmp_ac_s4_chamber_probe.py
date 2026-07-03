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

def power_to_bernstein(poly, var):
    p=sp.Poly(sp.expand(poly), var)
    deg=p.degree()
    pc=[p.coeff_monomial(var**i) for i in range(deg+1)]
    out=[]
    for k in range(deg+1):
        s=0
        for i in range(k+1):
            s += pc[i]*sp.binomial(k,i)/sp.binomial(deg,i)
        out.append(sp.factor(s))
    return out

def multi_bernstein(expr, bvars):
    polys=[expr]
    for var in bvars:
        nxt=[]
        for p in polys:
            nxt.extend(power_to_bernstein(p,var))
        polys=nxt
    return polys

def stats_expr(name, expr, bvars, uvars):
    num,den=sp.together(expr).as_numer_denom()
    den_poly=sp.Poly(sp.expand(den), *bvars, *uvars)
    den_coeffs=[sp.Integer(c) for c in den_poly.coeffs()]
    den_ok=all(c>0 for c in den_coeffs)
    bad=[]; total=0; mins=[]; count=0
    for bc in multi_bernstein(num,bvars):
        count += 1
        poly=sp.Poly(sp.expand(bc), *uvars)
        coeffs=[sp.Integer(c) for c in poly.coeffs()]
        total += len(coeffs)
        mins.append(min(coeffs))
        if any(c<0 for c in coeffs):
            bad.append((count-1,len(coeffs),min(coeffs),sum(1 for c in coeffs if c<0)))
    print(name, 'bern',count,'total',total,'min',min(mins),'bad',bad[:5], 'den_ok',den_ok,'den_min',min(den_coeffs),'den_terms',len(den_coeffs))

def stats_coeff(name, expr, vars):
    num,den=sp.together(expr).as_numer_denom()
    p=sp.Poly(sp.expand(num), *vars)
    cs=[sp.Integer(c) for c in p.coeffs()]
    q=sp.Poly(sp.expand(den), *vars)
    ds=[sp.Integer(c) for c in q.coeffs()]
    print(name,'terms',len(cs),'min',min(cs),'neg',sum(1 for c in cs if c<0),'den_min',min(ds),'den_neg',sum(1 for c in ds if c<=0))

# A: X>=V. Put X=V+H. F=Rf*U, b>=v.
V,H,Rf,Rd,G=sp.symbols('V H Rf Rd G', nonnegative=True)
X=V+H; x=1+X; v=1+V
U=sp.factor(V + X/(X+2))
F=Rf*U; f=1+F
b=sp.factor((x*(1+v)+v-1-f)/f)
S=sp.factor(b-1-V)
print('A S=', sp.factor(S))
# segment D in [0,S]
D=Rd*S; E=(b-1)-D; d=1+D; e=1+E
stats_expr('A_segment', phi_expr(b,d,e,f,x,v), (Rf,Rd), (V,H))
# ray D=S+G, E=V
D=S+G; E=V; d=1+D; e=1+E
stats_expr('A_ray', phi_expr(b,d,e,f,x,v), (Rf,), (V,H,G))

# B1: V>=X and F<=W. Put V=X+H. F=Rf*W, b>=v.
X,H,Rf,Rd,G=sp.symbols('X H Rf Rd G', nonnegative=True)
V=X+H; x=1+X; v=1+V
W=sp.factor((V*X+V+2*X)/(V+2))
F=Rf*W; f=1+F
b=sp.factor((x*(1+v)+v-1-f)/f)
S=sp.factor(b-1-V)
print('B1 S=', sp.factor(S))
D=Rd*S; E=(b-1)-D; d=1+D; e=1+E
stats_expr('B1_segment', phi_expr(b,d,e,f,x,v), (Rf,Rd), (X,H))
D=S+G; E=V; d=1+D; e=1+E
stats_expr('B1_ray', phi_expr(b,d,e,f,x,v), (Rf,), (X,H,G))

# B2: V>=X and F>=W up to U. F=W+Rf*(U-W), v>=b. E=V, D=G.
X,H,Rf,G=sp.symbols('X H Rf G', nonnegative=True)
V=X+H; x=1+X; v=1+V
U=sp.factor(V+X/(X+2)); W=sp.factor((V*X+V+2*X)/(V+2))
F=sp.factor(W+Rf*(U-W)); f=1+F
b=sp.factor((x*(1+v)+v-1-f)/f)
print('B2 v-b=', sp.factor(v-b))
D=G; E=V; d=1+D; e=1+E
stats_expr('B2', phi_expr(b,d,e,f,x,v), (Rf,), (X,H,G))
