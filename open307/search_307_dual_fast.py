from sympy import factorint

P_MAX=500
SIZE_MAX=8
PROD_BOUND=10**18

# prime masks for pairwise-coprime generation
primes=[]
for n in range(2,P_MAX+1):
    ok=True
    for p in primes:
        if p*p>n: break
        if n%p==0: ok=False; break
    if ok: primes.append(n)
pindex={p:i for i,p in enumerate(primes)}
def mask_of(n):
    x=n;m=0
    for p in primes:
        if p*p>x: break
        if x%p==0:
            m|=1<<pindex[p]
            while x%p==0: x//=p
    if x>1: m|=1<<pindex[x]
    return m
cands=[(x,mask_of(x)) for x in range(2,P_MAX+1)]

def greedy_ub(start,mask,slots,pleft):
    s=0.0;c=0
    for j in range(start,len(cands)):
        x,m=cands[j]
        if c>=slots: break
        if x>pleft: break
        if mask&m: continue
        s += 1.0/x; c += 1; pleft//=x; mask|=m
    return s

def has_Q(Np,Dp):
    fac=factorint(Np)
    if len(fac)<2: return None
    blocks=[int(p)**int(e) for p,e in fac.items()]
    r=len(blocks)
    # maximum numerator for any partition is splitting all prime-power blocks.
    if sum(Np//b for b in blocks) < Dp:
        return None
    full=(1<<r)-1
    prod_subset=[1]*(1<<r)
    for mask in range(1,1<<r):
        lsb=mask & -mask; i=lsb.bit_length()-1
        prod_subset[mask]=prod_subset[mask^lsb]*blocks[i]
    group=[]
    def rec(unused,acc):
        if acc>Dp: return None
        if unused==0:
            return list(group) if len(group)>=2 and acc==Dp else None
        # maximum possible remaining contribution by splitting all unused blocks
        mm=unused; mx=0
        while mm:
            l=mm & -mm; i=l.bit_length()-1; mx += Np//blocks[i]; mm ^= l
        if acc + mx < Dp: return None
        # minimum possible contribution with one group for remaining.
        if acc + Np//prod_subset[unused] > Dp: return None
        lsb=unused & -unused; rest=unused^lsb
        subs=[]; sub=rest
        while True:
            g=sub|lsb; q=prod_subset[g]
            subs.append((Np//q,g,q))
            if sub==0: break
            sub=(sub-1)&rest
        # low contributions first helps hit target Dp near product/near one.
        subs.sort()
        for contrib,g,q in subs:
            group.append(q)
            res=rec(unused^g,acc+contrib)
            if res is not None: return res
            group.pop()
        return None
    return rec(full,0)

examined=0
factored=0

def dfs(start,mask,D,N,size,elems):
    global examined,factored
    if size>=2 and N>D:
        examined += 1
        # quick necessary condition: Q sum target D/N; if N is too small no.
        q=has_Q(N,D)
        factored += 1
        if q is not None:
            print('WITNESS_FOUND')
            print('P', elems, 'D', D, 'N', N)
            print('Q', sorted(q), 'D', N, 'N', D)
            raise SystemExit
    if size>=SIZE_MAX: return
    if start>=len(cands): return
    if N/D + greedy_ub(start,mask,SIZE_MAX-size,PROD_BOUND//D) <= 1.0:
        return
    for j in range(start,len(cands)):
        x,m=cands[j]
        if D*x>PROD_BOUND: break
        if mask&m: continue
        D2=D*x; N2=N*x+D
        if N2/D2 + greedy_ub(j+1,mask|m,SIZE_MAX-size-1,PROD_BOUND//D2) <= 1.0:
            continue
        dfs(j+1,mask|m,D2,N2,size+1,elems+[x])

try:
    dfs(0,0,1,0,0,[])
except SystemExit:
    raise
print('NO_WITNESS_UP_TO')
print('P_max:',P_MAX)
print('size_max:',SIZE_MAX)
print('product_bound:',PROD_BOUND)
print('sets_examined:',examined)
print('next_range:','increase size/P bound and run reverse numerator-product search')
