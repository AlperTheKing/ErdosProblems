import sympy as sp

a,b,c,d,e,f,x,u,v=sp.symbols('a b c d e f x u v')
y=sp.Integer(1)
m=x*u+x*v+v
Y=a*c+b*f+c*f
sl={
'd1':d-1,
'f1':f-1,
's1':e-v,
's2':d+e-u-v,
's3':b+c-x-1,
's6':a*c+d*f+e*f-m,
's7':a*e+d*f+e*f-m,
'u1':u-1,
'xq':x-u-v,
}
active=('d1','f1','s1','s2','s3','s6','s7','u1','xq')
target=[d-1,f-1,e-(x-1),v-(x-1),u-1,b-2,c-(x-1),a-(x+1)]
for missing in ('d1','f1','s1','s2','s3','s6','s7','u1'):
    eqs=[sl[n] for n in active if n!=missing]
    G=sp.groebner(eqs,a,b,c,d,e,f,u,v,x,order='lex')
    basis=[sp.factor(p.as_expr()) for p in G.polys]
    rem=[sp.factor(G.reduce(t)[1]) for t in target]
    print('DROP',missing,'len',len(basis),'targetzero',all(r==0 for r in rem))
    if not all(r==0 for r in rem):
        print(' basis',basis)
        print(' rem',rem)