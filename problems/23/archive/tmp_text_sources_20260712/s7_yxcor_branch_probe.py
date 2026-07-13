from __future__ import annotations
import math
import sympy as sp

A0,B0,C0,D0,E0,F0,T = sp.symbols('A0 B0 C0 D0 E0 F0 T')
a,b,c,d,e,f = 1+A0,1+B0,1+C0,1+D0,1+E0,1+F0
Y = a*c + b*f + c*f
R = b+c
D = d+e
Z = e*Y + d*f*R
AA = b*d + c*d + d*f + a*c + a*e + b*f + b*e + c*f + c*e + e*f
BB = a*c + a*e + b*f + b*e + c*f + c*e + e*f
S = a+b+c+d+e+f
Ms = {4:Y,5:a*e+b*f+c*f,6:a*c+d*f+e*f,7:a*e+d*f+e*f}
vars_=(A0,B0,C0,D0,E0,F0)

def pi(M,q):
    x=1; v=M-q; N=S+2+q
    return sp.expand(2*e*Y*Z*(N*N-25*M) - 75*(e*Y*x*q*AA + Z*v*BB - e*Y*Z*S))

def bernstein(poly, var):
    P=sp.Poly(sp.expand(poly), var); n=P.degree(); out=[]
    for k in range(n+1):
        s=0
        for i in range(k+1):
            ci=P.nth(i)
            if ci:
                s += ci * sp.Rational(math.comb(k,i), math.comb(n,i))
        out.append(sp.expand(s))
    return out

def st(expr):
    P=sp.Poly(sp.expand(expr), *vars_)
    coeffs=P.coeffs(); neg=[(m,c) for m,c in zip(P.monoms(), coeffs) if c<0]
    return len(coeffs), P.total_degree(), min(coeffs) if coeffs else 0, len(neg), neg[:3]

for j,M in Ms.items():
    lows={'u':(M+1)/2, 'vE':M-e}
    ups={'v':M-1, 'D':D}
    for ln,L in lows.items():
        for un,U in ups.items():
            q=L+T*(U-L)
            # multiply by 4 to clear lower half denominator safely
            expr=sp.together(4*pi(M,q)).as_numer_denom()[0]
            controls=bernstein(expr,T)
            stats=[st(c0) for c0 in controls]
            bad=[(i,s) for i,s in enumerate(stats) if s[3]]
            print('YXCOR',j,ln,un,'deg',len(controls)-1,'bad',len(bad),'min',min(s[2] for s in stats))
            if bad:
                print(' first',bad[0])
