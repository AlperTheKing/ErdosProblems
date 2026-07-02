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
print('groebner XR start', flush=True)
G=sp.groebner([PX,PR],X,R,order='lex')
print('groebner XR done len', len(G.polys), flush=True)
for i,g in enumerate(G.polys):
    P=sp.Poly(g.as_expr(),X,R)
    print(i,'degX',P.degree(X),'degR',P.degree(R),'terms',len(P.terms()), flush=True)
elims=[sp.Poly(g.as_expr(),R) for g in G.polys if sp.Poly(g.as_expr(),X,R).degree(X)==0]
print('elims',[(P.degree(),len(P.terms())) for P in elims], flush=True)
for P in elims:
    print('count01 start deg', P.degree(), flush=True)
    print('roots01', sp.polys.polytools.count_roots(P.as_expr(),0,1), flush=True)
print('PASS scratch R elimination')