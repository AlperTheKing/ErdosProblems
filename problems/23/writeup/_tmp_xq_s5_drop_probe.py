import sympy as sp

a,b,c,d,e,f,x,u,v=sp.symbols('a b c d e f x u v')
y=sp.Integer(1)
m=x*u+x*v+v
Y=a*c+b*f+c*f
sl={
'a1':a-1,
's1':e-v,
's3':b+c-x-1,
's4':Y-m,
's5':a*e+b*f+c*f-m,
's6':a*c+d*f+e*f-m,
's7':a*e+d*f+e*f-m,
'u1':u-1,
'xq':x-u-v,
}
active=('a1','s1','s3','s4','s5','s6','s7','u1','xq')
target_exprs=[a-1,c-(x-1),e-(x-1),v-(x-1),u-1,b-2,d-2,(x+1)*f-x**2]
for missing in ('a1','s1','s3','s4','s6','s7','u1'):
    eqs=[sl[n] for n in active if n!=missing]
    G=sp.groebner(eqs,a,b,c,d,e,f,u,v,x,order='lex')
    basis=[sp.factor(p.as_expr()) for p in G.polys]
    rem=[sp.factor(G.reduce(t)[1]) for t in target_exprs]
    print('DROP',missing,'len',len(basis),'remzero',all(r==0 for r in rem))
    if not all(r==0 for r in rem):
        print(' basis', basis)
        print(' rem', rem)