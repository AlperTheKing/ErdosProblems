# Fast check: all C5-blowups of 20 into 5 positive parts. beta and min 5-set drop.
# Uses the C++-equivalent exact maxcut in python but only on blowups (few graphs).
import itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h2_redteam2 import build, beta, has_triangle

N=20; TARGET=7
def blow(parts):
    grp=[]; idx=0
    for s in parts: grp.append(list(range(idx,idx+s))); idx+=s
    e=[]
    for p in range(5):
        q=(p+1)%5
        for u in grp[p]:
            for v in grp[q]: e.append((u,v))
    return e

worst=-99; worstp=None; tested=0; maxb=0; maxbp=None; maxbdrop=None
comps=set()
for parts in itertools.product(range(1,17),repeat=5):
    if sum(parts)!=20: continue
    sp=tuple(sorted(parts))  # canonical up to rotation? blowup beta is rotation-invariant, dedupe by sorted is not exact but reduces
    comps.add(parts)
print(f"compositions: {len(comps)}")
seen=set()
for parts in comps:
    # dedupe by necklace canonical form (rotations + reflection) to cut work
    rots=[tuple(parts[i:]+parts[:i]) for i in range(5)]
    rots+=[tuple(reversed(r)) for r in rots]
    canon=min(rots)
    if canon in seen: continue
    seen.add(canon)
    am=build(N, blow(parts))
    bG=beta(N,am,list(range(N)))
    if bG>maxb: maxb=bG; maxbp=parts
    if bG<11: continue  # only care about high-beta band
    # min 5set drop
    mn=999; arg=None
    for S in itertools.combinations(range(N),5):
        rem=[v for v in range(N) if v not in S]
        d=bG-beta(N,am,rem)
        if d<mn: mn=d; arg=S
        if mn<=TARGET: break
    tested+=1
    m=mn-TARGET
    if m>worst: worst=m; worstp=(parts,bG,mn,arg)
    if parts==maxbp: maxbdrop=mn
print(f"distinct necklaces tested(beta>=11): {tested}")
print(f"MAX beta over all blowups: {maxb} at parts={maxbp}")
print(f"worst margin (min5drop - 7): {worst}")
print(f"worst case (parts,beta,min5drop,argmin): {worstp}")
