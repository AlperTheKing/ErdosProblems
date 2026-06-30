"""Verify CYCLIC-MIN-PRODUCT: for n_0..n_4>=0 with sum=N, 25*min_i(n_i*n_{i+1}) <= N^2.
Proof: min_i(n_i n_{i+1}) <= geomean of the 5 cyclic products = (prod n_i)^{2/5} <= (N/5)^2 by AM-GM. Brute N<=45."""
from itertools import product
bad=0; tight=0; tightex=None
for N in range(5,46):
    for t in product(range(N+1),repeat=4):
        s=sum(t)
        if s>N: continue
        n=list(t)+[N-s]
        mp=min(n[i]*n[(i+1)%5] for i in range(5))
        if 25*mp>N*N: bad+=1
        if 25*mp==N*N:
            tight+=1
            if tightex is None: tightex=(N,n)
print("cyclic-min-product 25*min(n_i n_{i+1}) <= N^2: violations=%d, equality_cases=%d"%(bad,tight))
print("example equality:",tightex,"(expect balanced n_i=N/5)")
