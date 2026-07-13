from itertools import product
def keys(P,R,O=frozenset()):
 K={(x,y,h) for x,y in set(P) for h in (0,1) if not(h==0 and (x,y) in R)}
 assert len(K)==sum(2-int(p in R) for p in set(P))
 assert len(set(P))<=len(K)<=2*len(set(P))
 assert len(O|K)-len(O)==len(K-O)
 return K
U=((0,1),(1,0),(0,2)); A=tuple((x,y,h) for x,y in U for h in (0,1))
for a in product((0,1),repeat=3):
 P={p for p,z in zip(U,a) if z}
 for b in product((0,1),repeat=3):
  R={p for p,z in zip(U,b) if z}
  for c in product((0,1),repeat=6): keys(P,R,{q for q,z in zip(A,c) if z})
W={(x,2930,h) for x in range(29,43) for h in (0,1)}
assert len(W)==28 and keys({(x,2930) for x in range(29,43)},set())==W
print('PASS exact identity; exhaustive 3-pair gate; R29 absorber=28')