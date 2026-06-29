"""Verify: global max cut value of C_m[sizes] equals best PART-LEVEL assignment value.
Also verify whether any vertex-level global max cut splits a part."""
import itertools
from _h import maxcut_all
from _wf_mhunt_1 import build_blowup, cutsize

def partlevel_maxval(m,sizes):
    best=-1; bestassigns=[]
    for bits in range(1<<m):
        side=[(bits>>i)&1 for i in range(m)]
        val=sum(sizes[i]*sizes[(i+1)%m] for i in range(m) if side[i]!=side[(i+1)%m])
        if val>best: best=val; bestassigns=[side]
        elif val==best: bestassigns.append(side)
    return best,bestassigns

bad=0
for m,sset in [(5,[1,2,3,4]),(7,[1,2]),(9,[1,2])]:
    for sizes in itertools.product(sset,repeat=m):
        if sum(sizes)>20: continue
        n,adj,E,start=build_blowup(m,sizes)
        cuts=maxcut_all(n,adj)
        truemax=cutsize(n,adj,cuts[0])
        pmax,_=partlevel_maxval(m,sizes)
        # does any global max cut split a part?
        split=False
        for s in cuts:
            for i in range(m):
                vs=set(s[start[i]+a] for a in range(sizes[i]))
                if len(vs)>1: split=True; break
            if split: break
        if truemax!=pmax:
            bad+=1
            print("MISMATCH",m,sizes,"true",truemax,"part",pmax)
        if split:
            print("SPLIT-in-globalmax",m,sizes,"true",truemax)
print("done; value-mismatches=",bad)
