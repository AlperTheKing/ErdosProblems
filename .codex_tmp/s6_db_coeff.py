import sympy as sp
a,b,c,d,e,f=sp.symbols('a b c d e f')
x=d+e; y=sp.Integer(1)
v=a*c+f*x-x*x; u=x-v
S=a+b+c+d+e+f
m=x*x+v
N=S+y+x+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-S)
num=sp.factor(sp.together(sp.diff(Phi,b)).as_numer_denom()[0])
A0,C0,D0,F0,R,H=sp.symbols('A0 C0 D0 F0 R H')
subs={a:1+A0,c:1+C0,d:1+D0,f:1+F0,e:1+C0+R,b:2+D0+R+H}
shift=sp.Poly(sp.expand(num.subs(subs)), A0,C0,D0,F0,R,H)
terms=shift.terms()
pos=[]; neg=[]; zero=[]
for mon,coef in terms:
    if coef>0: pos.append((mon,coef))
    elif coef<0: neg.append((mon,coef))
    else: zero.append((mon,coef))
print('shift terms',len(terms),'pos',len(pos),'neg',len(neg),'zero',len(zero),'deg',shift.total_degree())
if neg:
    print('first neg', neg[0])
else:
    print('mincoef', min(coef for mon,coef in pos), 'maxcoef', max(coef for mon,coef in pos))
