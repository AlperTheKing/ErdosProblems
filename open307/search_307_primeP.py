from sympy import primerange, factorint
P_MAX=10000
SIZE_MAX=12
PROD_BOUND=10**30
cands=list(primerange(2,P_MAX+1))

def greedy_ub(start,slots,pleft):
    s=0.0; c=0
    for x in cands[start:]:
        if c>=slots: break
        if x>pleft: break
        s += 1.0/x; c += 1; pleft//=x
    return s

def has_Q(Np,Dp):
    fac=factorint(Np)
    if len(fac)<2: return None
    blocks=[int(p)**int(e) for p,e in fac.items()]
    r=len(blocks); full=(1<<r)-1; group=[]
    # sort blocks descending? group containing lsb; keep as is
    def rec(unused,acc):
        if acc>Dp: return None
        if unused==0:
            return list(group) if len(group)>=2 and acc==Dp else None
        # lower contribution if all remaining one group
        prod=1; mm=unused; idx=0
        while mm:
            if mm&1: prod*=blocks[idx]
            idx+=1; mm>>=1
        if acc + Np//prod > Dp: return None
        lsb=unused & -unused; rest=unused^lsb; sub=rest
        while True:
            gmask=sub|lsb; q=1; mm=gmask; idx=0
            while mm:
                if mm&1: q*=blocks[idx]
                idx+=1; mm>>=1
            # Np//q is contribution; try larger q first by current sub iteration all bits first
            group.append(q)
            res=rec(unused^gmask, acc+Np//q)
            if res is not None: return res
            group.pop()
            if sub==0: break
            sub=(sub-1)&rest
        return None
    return rec(full,0)
examined=0
def dfs(start,D,N,size,elems):
    global examined
    if size>=2 and N>D:
        examined+=1
        q=has_Q(N,D)
        if q:
            print('WITNESS_FOUND')
            print('P',elems,'D',D,'N',N)
            print('Q',sorted(q),'D',N,'N',D)
            raise SystemExit
    if size>=SIZE_MAX: return
    if N/D + greedy_ub(start,SIZE_MAX-size,PROD_BOUND//D) <= 1.0: return
    for j in range(start,len(cands)):
        x=cands[j]
        if D*x>PROD_BOUND: break
        D2=D*x; N2=N*x+D
        if N2/D2 + greedy_ub(j+1,SIZE_MAX-size-1,PROD_BOUND//D2) <= 1.0: continue
        dfs(j+1,D2,N2,size+1,elems+[x])
try:
    dfs(0,1,0,0,[])
except SystemExit: raise
print('NO_WITNESS_PRIME_P',P_MAX,SIZE_MAX,PROD_BOUND,'examined',examined)
