P_MAX=5000
SIZE_MAX=8
PROD_BOUND=10**24
primes=[]
for n in range(2,P_MAX+1):
    ok=True
    for p in primes:
        if p*p>n: break
        if n%p==0: ok=False; break
    if ok: primes.append(n)
pidx={p:i for i,p in enumerate(primes)}
def mask(n):
    x=n;m=0
    for p in primes:
        if p*p>x: break
        if x%p==0:
            m|=1<<pidx[p]
            while x%p==0:x//=p
    if x>1:m|=1<<pidx[x]
    return m
cands=[(x,mask(x)) for x in range(2,P_MAX+1)]
# order small first
def greedy(start,used,slots,pleft):
    s=0.0;c=0
    for j in range(start,len(cands)):
        x,m=cands[j]
        if c>=slots: break
        if x>pleft: break
        if used&m: continue
        s += 1/x; c+=1; used|=m; pleft//=x
    return s
count=0; nodes=0
def dfs(start,used,D,N,size):
    global count,nodes
    nodes+=1
    if size>=2 and N>D: count+=1
    if size>=SIZE_MAX: return
    if N/D + greedy(start,used,SIZE_MAX-size,PROD_BOUND//D) <= 1.0: return
    for j in range(start,len(cands)):
        x,m=cands[j]
        if D*x>PROD_BOUND: break
        if used&m: continue
        D2=D*x; N2=N*x+D
        if N2/D2 + greedy(j+1,used|m,SIZE_MAX-size-1,PROD_BOUND//D2) <= 1.0: continue
        dfs(j+1,used|m,D2,N2,size+1)
dfs(0,0,1,0,0)
print('count',count,'nodes',nodes)
