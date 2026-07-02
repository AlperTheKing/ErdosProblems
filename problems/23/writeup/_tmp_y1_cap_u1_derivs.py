import sympy as sp

def check(cap):
    a,b,c,d,e,f,v=sp.symbols('a b c d e f v', positive=True); vars_=(a,b,c,d,e,f,v); y=sp.Integer(1); u=sp.Integer(1)
    S=a+b+c+d+e+f; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}; M=caps[cap]
    q=1+v; x=(M-v)/q; N=S+1+x+q; Phi=2*(N*N-25*M)-75*(x*q*A/Z+v*B/(e*Y)-S)
    for varname,var in [('f',f),('a',a),('v',v)]:
        num=sp.together(sp.diff(Phi,var)).as_numer_denom()[0]
        xs=sp.symbols('x0:7'); sh={vv:xx+1 for vv,xx in zip(vars_,xs)}
        P=sp.Poly(sp.expand(num.subs(sh)),*xs)
        coeff=[c for m,c in P.terms()]
        print(cap,varname,'terms',len(coeff),'min',min(coeff),'neg',sum(1 for c in coeff if c<0),'const',P.coeff_monomial((0,0,0,0,0,0,0)))
for cap in ['s4','s5','s6','s7']:
    check(cap)
