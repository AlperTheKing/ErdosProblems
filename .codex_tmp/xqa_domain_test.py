import importlib.util, pathlib, sympy as sp
p=pathlib.Path('problems/23/writeup/_codex_sib_s7_y1_symbolic_rank_certificates.py')
spec=importlib.util.spec_from_file_location('cert',p)
cert=importlib.util.module_from_spec(spec); spec.loader.exec_module(cert)
inv=cert.load_inventory(); a,b,c,d,e,f,x,u,v=inv.VARS
Y=a*c+b*f+c*f; y=sp.Integer(1); m=x*u+x*v+v; N=a+b+c+d+e+f+x+y+u+v; Z=e*Y+d*f*(b+c)
A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*(u+v)*A/Z+v*B/(e*Y)-(a+b+c+d+e+f))
(X,R),subs=cert.family_substitution(inv,'XQ_A')
phi=sp.together(Phi.subs(subs))
PX=cert.nonzero_num(sp.diff(phi,X)); PR=cert.nonzero_num(sp.diff(phi,R))
print('groebner start', flush=True)
G=sp.groebner([PX,PR],R,X,order='lex')
print('groebner done', flush=True)
elim=sp.factor(G.polys[-1].as_expr())
core=sp.Poly(elim/((X+2)**3*(X+3)**9*(X**2+4*X+2)**3*(X**2+5*X+5)**2*(3*X**2+16*X+19)), X)
print('core deg', core.degree(), flush=True)
intervals=sp.polys.polytools.intervals(core.as_expr(), eps=sp.Rational(1,1000000))
nonneg=[]
for (lohi,mult) in intervals:
    lo,hi=lohi
    if hi>=0:
        nonneg.append((lo,hi,mult))
print('nonneg', nonneg, flush=True)
lin=sp.Poly(G.polys[2].as_expr(),R)
cr=sp.Poly(lin.coeff_monomial(R),X).as_expr(); c0=sp.Poly(lin.coeff_monomial(1),X).as_expr()
for lo,hi,mult in nonneg:
    mid=(lo+hi)/2
    print('mid', sp.N(mid,12), 'cr', sp.sign(cr.subs(X,mid)), 'R', sp.sign((-c0*cr).subs(X,mid)), 'R-1', sp.sign(((-c0-cr)*cr).subs(X,mid)), flush=True)
    assert sp.polys.polytools.count_roots(cr, lo, hi) == 0
    assert sp.polys.polytools.count_roots(-c0*cr, lo, hi) == 0
    assert sp.polys.polytools.count_roots((-c0-cr)*cr, lo, hi) == 0
print('PASS scratch xqa candidates out of 0<=R<=1')