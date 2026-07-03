from fractions import Fraction

def phi(a,b,c,d,e,f,x,y,u,v):
    m=x*u+x*v+y*v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n*n-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))

best=None; best_tuple=None; checked=0
for Xn in range(0,5):
  for Vn in range(0,5):
    X=Fraction(Xn,1); V=Fraction(Vn,1)
    x=1+X; v=1+V; y=u=a=Fraction(1,1)
    m=x*(1+v)+v
    M3=m-3
    # q=c-1 over quarters up to M3/2
    for qn in range(0,17):
      q=Fraction(qn,4)
      c=1+q
      if q > M3/2: continue
      lo=max(c+1, x+1)
      hi=m-c
      if lo > hi: continue
      for tn in range(0,17):
        t=lo + Fraction(tn,16)*(hi-lo)
        b=t-c
        if b < 1: continue
        f=(m-c)/t
        if f < 1: continue
        for dn in range(1,12):
          d=Fraction(dn,1)
          for en in range(1,12):
            e=Fraction(en,1)
            if e < v or e < c: continue
            if d+e < b+c: continue
            val=phi(a,b,c,d,e,f,x,y,u,v)
            checked += 1
            if best is None or val < best:
              best=val; best_tuple=(X,V,q,t,b,c,d,e,f,val)
print('checked', checked)
print('best', best, best_tuple)
