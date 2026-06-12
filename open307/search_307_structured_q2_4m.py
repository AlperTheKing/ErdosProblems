from sympy import factorint
from math import gcd

def partitions_for(N,target,limit_blocks=20):
    fac=factorint(N)
    blocks=[int(p)**int(e) for p,e in fac.items()]
    r=len(blocks)
    if r<2 or r>limit_blocks: return None
    if sum(N//b for b in blocks)<target: return None
    full=(1<<r)-1
    prods=[1]*(1<<r)
    for m in range(1,1<<r):
        l=m&-m; i=l.bit_length()-1; prods[m]=prods[m^l]*blocks[i]
    group=[]
    def rec(unused,acc):
        if acc>target: return None
        if unused==0: return list(group) if len(group)>=2 and acc==target else None
        mx=0; mm=unused
        while mm:
            l=mm&-mm; i=l.bit_length()-1; mx+=N//blocks[i]; mm^=l
        if acc+mx<target: return None
        if acc+N//prods[unused]>target: return None
        lsb=unused&-unused; rest=unused^lsb; opts=[]; sub=rest
        while True:
            g=sub|lsb; opts.append((N//prods[g],g,prods[g]))
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

def search(base,Amax):
    B=1
    for x in base: B*=x
    checked=0
    for a in range(B+1,Amax+1):
        if gcd(a,B)!=1: continue
        D=B*a
        N=(B-1)*a+B
        checked+=1
        q=partitions_for(N,D)
        if q:
            print('WITNESS_FOUND')
            print('P',sorted(q),'D',N,'N',D)
            print('Q',base+[a],'D',D,'N',N)
            return True
    print('NO_STRUCTURED_Q_BASE_A',base,Amax,'checked',checked)
    return False
search([2,3,7,43,1807], 4_000_000)
