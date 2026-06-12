from sympy import factorint
from math import gcd, prod
from fractions import Fraction
from time import time

partition_count=0

def partition_product_num(prodN, targetNum, limit_blocks=32):
    global partition_count
    fac=factorint(int(prodN))
    blocks=[int(p)**int(e) for p,e in fac.items()]
    r=len(blocks)
    if r<2 or r>limit_blocks: return None
    if sum(prodN//b for b in blocks)<targetNum: return None
    full=(1<<r)-1
    prods=[1]*(1<<r)
    for m in range(1,1<<r):
        l=m&-m; i=l.bit_length()-1; prods[m]=prods[m^l]*blocks[i]
    group=[]
    def rec(unused,acc):
        global partition_count
        partition_count += 1
        if acc>targetNum: return None
        if unused==0: return list(group) if len(group)>=2 and acc==targetNum else None
        mx=0; mm=unused
        while mm:
            l=mm&-mm; i=l.bit_length()-1; mx += prodN//blocks[i]; mm ^= l
        if acc+mx<targetNum: return None
        if acc+prodN//prods[unused]>targetNum: return None
        lsb=unused&-unused; rest=unused^lsb
        opts=[]; sub=rest
        while True:
            g=sub|lsb; opts.append((prodN//prods[g],g,prods[g]))
            if sub==0: break
            sub=(sub-1)&rest
        opts.sort()
        for contrib,g,q in opts:
            group.append(q)
            z=rec(unused^g,acc+contrib)
            if z: return z
            group.pop()
        return None
    return rec(full,0)

# For fixed Q, target P sum = Dq/Nq. Since D(P)=Nq and N(P)=Dq,
# enumerate pairwise-coprime factor partitions of Nq and check numerator exactly.
def check_fixed_Q(Q):
    D=prod(Q); N=sum(D//q for q in Q)
    P=partition_product_num(N,D)
    if P:
        print('WITNESS_FOUND:')
        print('P:',P,'Dp:',N,'Np:',D)
        print('Q:',Q,'Dq:',D,'Nq:',N)
        raise SystemExit

def pairwise(xs):
    for i,a in enumerate(xs):
        for b in xs[i+1:]:
            if gcd(a,b)!=1: return False
    return True

def search_small_Q(max_el=5000, max_size=8, seconds=900):
    global partition_count
    start=time(); examined=0
    vals=list(range(2,max_el+1))
    # prime-support mask for pruning
    facs={x:tuple(factorint(x).keys()) for x in vals}
    def rec(start_idx, elems, D, N, used):
        nonlocal examined
        if time()-start>seconds: return False
        if len(elems)>=2 and N<D:
            examined += 1
            P=partition_product_num(N,D)
            if P:
                print('WITNESS_FOUND:')
                print('P:',P,'Dp:',N,'Np:',D)
                print('Q:',elems,'Dq:',D,'Nq:',N)
                raise SystemExit
        if len(elems)>=max_size: return False
        for idx in range(start_idx,len(vals)):
            x=vals[idx]
            fs=facs[x]
            if any(p in used for p in fs): continue
            D2=D*x; N2=N*x+D
            # keep Q subunit, otherwise adding positives only increases
            if N2>=D2: continue
            rec(idx+1, elems+[x], D2, N2, used|set(fs))
        return False
    rec(0,[],1,0,set())
    print('NO_WITNESS_UP_TO:')
    print('phase: fixed_Q')
    print('P_max:',max_el)
    print('size_max:',max_size)
    print('product_bound: adaptive')
    print('sets_examined:',examined)
    print('partition_count:',partition_count)
    print('runtime:',int(time()-start),'s')
    print('next_phase: randomized local search')

for Q in ([2,3],[2,3,7],[2,3,7,43],[2,3,7,43,1807]):
    check_fixed_Q(list(Q))
search_small_Q(200,8,600)
