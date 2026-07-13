from fractions import Fraction
from itertools import product
def ss(n):
 for m in range(1,1<<n): yield [i for i in range(n) if m>>i&1]
def obs(e):
 for X in ss(len(e)):
  N={t for z in X for t in e[z]}
  if len(N)<len(X): return X,N
def inj(e):
 def f(z,u): return z==len(e) or any(t not in u and f(z+1,u|{t}) for t in e[z])
 return f(0,set())
c=0
for a in range(1,4):
 for b in range(1,4):
  for bits in product((0,1),repeat=a*b):
   e=[{t for t in range(b) if bits[z*b+t]} for z in range(a)]; o=obs(e); assert inj(e)==(o is None)
   if o:
    X,N=o; al=[Fraction(int(z in X)) for z in range(a)]; be=[Fraction(int(t in N)) for t in range(b)]
    assert all(al[z]<=be[t] for z in range(a) for t in e[z]) and sum(al)>sum(be)
   c+=1
print(c)
