# Derivation of F(N) as defined in "Toward a Lower Bound for Sorting Networks", D.C. Van Voorhis, 1972.
# for N>2, we have for the minimum size S(N) for any sorting network with N inputs:
# S(N) >= S(N-2) + P(2,N)   with   P(2,N) >= ceil(log2(F(N)))

from functools import lru_cache

@lru_cache(maxsize=None)
def minf(size,depth):
	if size==1:
		return 0
	vmin,dr = None, depth-1
	for sl in range(1,size-dr):
		sr = size-sl
		for dl in range(min(depth,sl)):
			fl,fr=minf(sl,dl),minf(sr,dr)
			if fl!=None and fr!=None:
				v=2*(fl+fr+2**(dl+dr))
				if vmin==None or v<vmin:
					vmin=v
	return vmin

@lru_cache(maxsize=None)
def F(n):
	return min(minf(n,d) for d in range(n) if minf(n,d)!=None)
