from math import gcd, prod
from functools import lru_cache
from sympy import factorint

P_MAX = 100
SIZE_MAX = 8
PROD_BOUND = 10**14

# primes up to P_MAX for masks
primes=[]
for n in range(2,P_MAX+1):
    ok=True
    for p in primes:
        if p*p>n: break
        if n%p==0: ok=False; break
    if ok: primes.append(n)
pindex={p:i for i,p in enumerate(primes)}

def mask_of(n):
    m=0; x=n
    for p in primes:
        if p*p>x: break
        if x%p==0:
            m |= 1<<pindex[p]
            while x%p==0: x//=p
    if x>1:
        m |= 1<<pindex[x]
    return m

cands=[]
for x in range(2,P_MAX+1):
    cands.append((x, mask_of(x)))
# Increasing denominator gives high reciprocal early and keeps set order canonical.

# suffix greedy upper bound: computed dynamically because masks/product matter.
def greedy_ub(start, used_mask, slots, product_left):
    s=0.0; cnt=0
    for j in range(start, len(cands)):
        x,m=cands[j]
        if cnt>=slots: break
        if x>product_left: break
        if used_mask & m: continue
        s += 1.0/x; cnt += 1; product_left //= x; used_mask |= m
    return s

def divisors_from_blocks(blocks):
    ds=[(1,0)]
    for i,b in enumerate(blocks):
        ds += [(d*b, mask | (1<<i)) for d,mask in ds]
    return ds

# enumerate partitions of prime-power blocks into groups, compute sum of complements.
def has_Q(Np, Dp):
    fac=factorint(Np)
    if len(fac) < 2:
        return None
    blocks=[int(p)**int(e) for p,e in fac.items()]
    r=len(blocks)
    # If all split, numerator=sum Np/block. If one group, size 1 invalid.
    full=(1<<r)-1
    # DFS choose next group containing the least unused block; this enumerates unlabeled partitions.
    group=[]
    def rec(unused, acc):
        if acc > Dp: return None
        if unused == 0:
            if len(group) >= 2 and acc == Dp:
                return list(group)
            return None
        # Lower-bound prune: acc plus one group covering all remaining contributes at least 1.
        lsb = unused & -unused
        rest = unused ^ lsb
        sub = rest
        while True:
            gmask = sub | lsb
            # canonical group product
            q=1
            mm=gmask; idx=0
            while mm:
                if mm&1: q *= blocks[idx]
                idx += 1; mm >>= 1
            group.append(q)
            res=rec(unused ^ gmask, acc + Np//q)
            if res is not None: return res
            group.pop()
            if sub == 0: break
            sub = (sub-1) & rest
        return None
    return rec(full, 0)

examined=0
printed=0
best_sum=0

def dfs(start, used_mask, D, N, size, elems):
    global examined, printed, best_sum
    # sum = N/D. We only test the >1 side.
    if size >= 2 and N > D:
        examined += 1
        q = has_Q(N, D)
        if q is not None:
            print('WITNESS_FOUND')
            print('P', elems, 'D', D, 'N', N)
            print('Q', sorted(q), 'D', N, 'N', D)
            print('sumP', f'{N}/{D}', 'sumQ', f'{D}/{N}')
            raise SystemExit
        if examined % 1000 == 0:
            print('examined', examined, 'current', elems, 'sum', float(N/D), flush=True)
    if size >= SIZE_MAX:
        return
    if start >= len(cands):
        return
    if N / D + greedy_ub(start, used_mask, SIZE_MAX-size, PROD_BOUND//D) <= 1.0:
        return
    for j in range(start, len(cands)):
        x,m=cands[j]
        if D*x > PROD_BOUND: break
        if used_mask & m: continue
        D2 = D*x
        N2 = N*x + D
        # Even after adding this, if no future can exceed 1, skip branch.
        if N2 / D2 + greedy_ub(j+1, used_mask|m, SIZE_MAX-size-1, PROD_BOUND//D2) <= 1.0:
            continue
        dfs(j+1, used_mask|m, D2, N2, size+1, elems+[x])

try:
    dfs(0,0,1,0,0,[])
except SystemExit:
    raise
print('NO_WITNESS_UP_TO')
print('P_max:', P_MAX)
print('size_max:', SIZE_MAX)
print('product_bound:', PROD_BOUND)
print('sets_examined:', examined)
print('next_range:', 'increase P_max/size_max and add targeted rational-side search')
