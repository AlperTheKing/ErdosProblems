from math import isqrt
P_MAX=2000
SIZE_MAX=10
PROD_BOUND=10**24
# prime masks up to P_MAX
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
        s+=1/x;c+=1;pleft//=x;mask|=m
    return s
examined=0
def dfs(start,mask,D,N,size,elems):
    global examined
    if size>=2 and N>D:
        examined+=1
        disc=D*D-4*N
        if disc>=0:
            s=isqrt(disc)
            if s*s==disc and (D+s)%2==0:
                a=(D-s)//2; b=(D+s)//2
                if a>1 and b>1 and a*b==N and a+b==D and __import__('math').gcd(a,b)==1:
                    print('WITNESS_FOUND')
                    print('P',elems,'D',D,'N',N)
                    print('Q',[a,b],'D',N,'N',D)
                    raise SystemExit
    if size>=SIZE_MAX: return
    if N/D + greedy_ub(start,mask,SIZE_MAX-size,PROD_BOUND//D) <= 1.0: return
    for j in range(start,len(cands)):
        x,m=cands[j]
        if D*x>PROD_BOUND: break
        if mask&m: continue
        D2=D*x; N2=N*x+D
        if N2/D2 + greedy_ub(j+1,mask|m,SIZE_MAX-size-1,PROD_BOUND//D2) <= 1.0: continue
        dfs(j+1,mask|m,D2,N2,size+1,elems+[x])
try:
    dfs(0,0,1,0,0,[])
except SystemExit: raise
print('NO_WITNESS_QSIZE2',P_MAX,SIZE_MAX,PROD_BOUND,'examined',examined)
