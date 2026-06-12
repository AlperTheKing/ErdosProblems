from sympy import factorint
from math import gcd

def partitions_for(N,target,limit_blocks=18):
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
base=[2,3,7,43]
B=1
for x in base:B*=x
AMAX=10000; BMAX=10000
checked=0
for a in range(B+1,AMAX+1):
    if gcd(a,B)!=1: continue
    # need 1/a+1/b < 1/B -> b > B*a/(a-B)
    blo=max(a+1, (B*a)//(a-B)+1)
    if blo>BMAX: continue
    for b in range(blo,BMAX+1):
        if gcd(b,B*a)!=1: continue
        D=B*a*b
        N=(B-1)*a*b + B*(a+b)
        checked+=1
        q=partitions_for(N,D)
        if q:
            print('WITNESS_FOUND')
            print('P',sorted(q),'D',N,'N',D)
            print('Q',base+[a,b],'D',D,'N',N)
            raise SystemExit
print('NO_STRUCTURED_Q_23743_AB',AMAX,BMAX,'checked',checked)
