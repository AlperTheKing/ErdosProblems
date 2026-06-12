from sympy import factorint
P_MAX=500
SIZE_MAX=8
PROD_BOUND=10**18
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
            while x%p==0:x//=p
    if x>1:m|=1<<pindex[x]
    return m
cands=[(x,mask_of(x)) for x in range(2,P_MAX+1)]

def partition_product_num(prodN,targetNum):
    fac=factorint(prodN)
    if len(fac)<2:return None
    blocks=[int(p)**int(e) for p,e in fac.items()]
    r=len(blocks)
    if r>24:return None
    if sum(prodN//b for b in blocks)<targetNum:return None
    full=(1<<r)-1
    prods=[1]*(1<<r)
    for m in range(1,1<<r):
        l=m&-m; i=l.bit_length()-1; prods[m]=prods[m^l]*blocks[i]
    group=[]
    def rec(unused,acc):
        if acc>targetNum:return None
        if unused==0:return list(group) if len(group)>=2 and acc==targetNum else None
        mx=0; mm=unused
        while mm:
            l=mm&-mm; i=l.bit_length()-1; mx+=prodN//blocks[i]; mm^=l
        if acc+mx<targetNum:return None
        if acc+prodN//prods[unused]>targetNum:return None
        lsb=unused&-unused; rest=unused^lsb; opts=[]; sub=rest
        while True:
            g=sub|lsb; opts.append((prodN//prods[g],g,prods[g]))
            if sub==0:break
            sub=(sub-1)&rest
        opts.sort()
        for contrib,g,q in opts:
            group.append(q)
            z=rec(unused^g,acc+contrib)
            if z:return z
            group.pop()
        return None
    return rec(full,0)
examined=0
def dfs(start,mask,D,N,size,elems):
    global examined
    if size>=2 and N<D:
        examined+=1
        p=partition_product_num(N,D)
        if p:
            print('WITNESS_FOUND')
            print('P',sorted(p),'D',N,'N',D)
            print('Q',elems,'D',D,'N',N)
            raise SystemExit
    if size>=SIZE_MAX:return
    for j in range(start,len(cands)):
        x,m=cands[j]
        if D*x>PROD_BOUND:break
        if mask&m:continue
        D2=D*x; N2=N*x+D
        # Need final sum below 1; if already huge, still adding smaller terms only increases, prune if N2>=D2 and all future increases.
        # But subunit can become superunit later, so only skip testing, not branch? Adding increases sum, so if N2>=D2 it will never go below 1.
        if N2>=D2: continue
        dfs(j+1,mask|m,D2,N2,size+1,elems+[x])
try: dfs(0,0,1,0,0,[])
except SystemExit: raise
print('NO_WITNESS_REVERSE',P_MAX,SIZE_MAX,PROD_BOUND,'sets_examined',examined)
