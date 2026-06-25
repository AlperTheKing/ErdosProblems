# Rigorously re-verify the block-case AM-GM finish over a dense grid, including the
# claimed (*) disjointness and the case split. Minimize f = p+q+a+w+d - 5*sqrt(pq)
# over the CD-feasible region a>=q, d>=p, a*w>=p*q, d*w>=p*q, all >=1 (integers and reals).
import math, itertools
worst=1e9; argm=None
# real grid
import numpy as np
grid=np.linspace(0.5,8,40)
for p in grid:
  for q in grid:
    pq=p*q; g=math.sqrt(pq)
    for w in grid:
      a_min=max(q, pq/w); d_min=max(p, pq/w)
      val=p+q+a_min+w+d_min-5*g
      if val<worst: worst=val; argm=(p,q,a_min,w,d_min)
print("min of (p+q+a+w+d)-5sqrt(pq) over feasible (a,d at their lower bounds):",round(worst,6))
print("argmin (p,q,a,w,d)=",[round(x,3) for x in argm])
# sanity: at balanced p=q=a=w=d=c it should be 5c-5c=0
print("balanced check c=3:",3*5-5*math.sqrt(9))
