ns = []
# PART 1 block-case claim audit.
# Claimed flips give: pq<=pa, pq<=qd, pq<=aw, pq<=dw  (p=|U|,q=|V|,a=|A|,w=|W|,d=|D|)
# => a>=q, d>=p, a>=pq/w, d>=pq/w
# and N>=p+q+a+w+d ; claim min over feasible of (p+q+a+w+d) - 5*sqrt(pq) = 0.
# Test: is it TRUE that min (a+w+d) subject to a>=q, d>=p, aw>=pq, dw>=pq  equals
#   minimizing p+q+a+w+d >= 5 sqrt(pq)?  Check by search.
import math, itertools
worst=1e9
worst_at=None
# scan integer-ish; but constraints are continuous. Do continuous min:
# For fixed p,q, minimize f= p+q+a+w+d over a>=max(q,pq/w), d>=max(p,pq/w), w>0.
# At optimum a=max(q,pq/w), d=max(p,pq/w). Minimize over w.
def fmin(p,q):
    best=1e18
    import numpy as np
    for w in [i/200.0 for i in range(1,2000)]:
        a=max(q, p*q/w)
        d=max(p, p*q/w)
        val=p+q+a+w+d
        if val<best: best=val
    return best
import math
for p in [1,2,3,5,8,1.0,0.5,2.5]:
    for q in [1,2,3,5,8,0.5,2.5]:
        m=fmin(p,q)
        bound=5*math.sqrt(p*q)
        gap=m-bound
        if gap<worst:
            worst=gap; worst_at=(p,q,m,bound)
print("min over scanned (p+q+a+w+d) - 5sqrt(pq):", worst, "at (p,q,fmin,5sqrt):", worst_at)
