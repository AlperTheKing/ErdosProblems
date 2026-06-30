from collections import deque
from itertools import combinations
from fractions import Fraction as F

n=10
side=[int(c) for c in '0001111000']
E=[(0,5),(0,6),(1,5),(1,9),(2,6),(2,7),(3,7),(3,8),(4,8),(4,9),(5,7),(5,8),(6,8),(6,9),(7,9)]
row=(7,5,8,6,9)
f=(7,9)
B=[]; M=[]
for e in E:
    a,b=e
    (B if side[a]!=side[b] else M).append(e)
print('B',B)
print('M',M)
Badj=[set() for _ in range(n)]
for a,b in B:
    Badj[a].add(b); Badj[b].add(a)

def dist(src):
    d=[None]*n; d[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for v in Badj[u]:
            if d[v] is None:
                d[v]=d[u]+1; q.append(v)
    return d

d0=dist(row[0]); d4=dist(row[-1])
layers=[]
for i in range(5):
    layers.append([v for v in range(n) if d0[v]==i and d4[v]==4-i])
print('layers',layers,'sizes',[len(x) for x in layers])
for i in range(4):
    edges=[(a,b) for a in layers[i] for b in layers[i+1] if tuple(sorted((a,b))) in [tuple(sorted(e)) for e in B]]
    print('B%d%d'% (i,i+1),edges)
print('M40',[(a,b) for a in layers[4] for b in layers[0] if tuple(sorted((a,b))) in [tuple(sorted(e)) for e in M]])

# path counts between A0 and A4
Bset={tuple(sorted(e)) for e in B}; Mset={tuple(sorted(e)) for e in M}
row_internal=row[1:4]
I=F(0)
for a0 in layers[0]:
    for a4 in layers[4]:
        if tuple(sorted((a0,a4))) not in Mset: continue
        paths=[]
        through=[0,0,0]
        for x1 in layers[1]:
            if tuple(sorted((a0,x1))) not in Bset: continue
            for x2 in layers[2]:
                if tuple(sorted((x1,x2))) not in Bset: continue
                for x3 in layers[3]:
                    if tuple(sorted((x2,x3))) in Bset and tuple(sorted((x3,a4))) in Bset:
                        p=(a0,x1,x2,x3,a4); paths.append(p)
                        for k,x in enumerate(row_internal):
                            if p[k+1]==x: through[k]+=1
        endpoint = int(a0==row[0]) + int(a4==row[-1])
        contrib=F(endpoint)+sum(F(c,len(paths)) for c in through)
        I += contrib
        print('bad', (a0,a4), 'Z',len(paths),'through row',through,'endpoint',endpoint,'contrib',contrib,'paths',paths)
print('I',I)

# cut domination tight/nontrivial cuts, canonical by excluding full/complement duplicates with vertex0 not necessarily
Blist=B; Mlist=M
tight=[]
for mask in range(1,1<<n):
    if mask==(1<<n)-1: continue
    # canonical complement: keep smallest int mask representative
    comp=((1<<n)-1)^mask
    if mask>comp: continue
    db=sum(1 for a,b in Blist if ((mask>>a)&1)!=((mask>>b)&1))
    dm=sum(1 for a,b in Mlist if ((mask>>a)&1)!=((mask>>b)&1))
    if db==dm:
        S=[v for v in range(n) if (mask>>v)&1]
        if db>0:
            tight.append((len(S),db,S))
print('tight cuts count',len(tight))
for rec in sorted(tight)[:80]:
    print('tight',rec)
