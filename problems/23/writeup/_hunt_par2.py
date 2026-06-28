"""Parallel HUNT batch 2: corridors (glued odd cycles), island+Mycielski gadget, Grotzsch vertex-blowups.
Same hit criterion as _hunt_par.py."""
import itertools
from fractions import Fraction as F
from multiprocessing import Pool
from _opencap import opencap, build_K
from _rowsum import rowsum
from _stark1 import odd_blowup, gmins
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def worker(task):
    nm,n,E=task
    if n>20 or not is_triangle_free(n,E):
        return (nm,n,0,0,None,[])
    adj,cuts=gmins(n,E)
    ocuts=0; maxO=0; minr=None; hits=[]
    for s in cuts:
        rd=rowsum(adj,s,n)
        if rd is None or rd.get('skip'): continue
        ocuts+=1; maxO=max(maxO,rd['O'])
        if rd.get('minratio') is not None:
            if minr is None or rd['minratio']<minr: minr=rd['minratio']
        if rd['fails']>0:
            oc=opencap(adj,s,n)
            if oc is None or oc.get('skip') or oc.get('singular'): continue
            if oc.get('cert') and rd['O']>=2:
                K,T=build_K(adj,s,n); N=n
                O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
                sden={q:sum(K[o2][q] for o2 in O) for q in Q}
                fo=None
                for o in O:
                    D=T[o]-N; lhs=F(0)
                    for q in Q:
                        Rq=F(N)-T[q]; den=Rq+sden[q]
                        if den>0 and K[o][q]>0: lhs+=K[o][q]*Rq/den
                    if lhs-D<0: fo=(o,T[o],N); break
                hits.append(dict(nm=nm,n=n,E=E,side=list(s),O=O,fo=fo))
    return (nm,n,ocuts,maxO,(float(minr) if minr is not None else None),hits)

def glue(m1,s1,m2,s2,link):
    n1,E1,_,_=odd_blowup(m1,list(s1)); n2,E2,_,_=odd_blowup(m2,list(s2))
    n,E=union_disjoint((n1,E1),(n2,E2))
    for (a,b) in link: E=E+[(a,n1+b)]
    return n,E

def gen():
    T=[]
    g11=mycielski(5,Cn(5)); g15=mycielski(7,Cn(7))
    # C5-C5 corridors single & double bridge
    for s1 in itertools.product([1,2,3],repeat=5):
        for s2 in itertools.product([1,2],repeat=5):
            if sum(s1)+sum(s2)>20: continue
            n,E=glue(5,s1,5,s2,[(0,0)]); T.append((f"C5{s1}-C5{s2}/b1",n,E))
    for s1 in itertools.product([1,2],repeat=5):
        for s2 in itertools.product([1,2],repeat=5):
            if sum(s1)+sum(s2)>20: continue
            n,E=glue(5,s1,5,s2,[(0,0),(2,3)]); T.append((f"C5{s1}-C5{s2}/b2",n,E))
    # C5-C7 corridors
    for s1 in itertools.product([1,2],repeat=5):
        for s2 in itertools.product([1,2],repeat=7):
            if sum(s1)+sum(s2)>20: continue
            n,E=glue(5,s1,7,s2,[(0,0)]); T.append((f"C5{s1}-C7{s2}/b1",n,E))
    # island + Mycielski gadget with bridges
    for iszt in [[1,1,1,1,1],[2,1,1,1,1],[1,2,1,2,1],[2,2,1,1,1]]:
        iN,iE,_,_=odd_blowup(5,iszt)
        for (gN,gE) in [g11,g15]:
            if iN+gN>20: continue
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)],[(0,0),(1,5)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                T.append((f"C5{iszt}+gad{gN}{br}",n,E))
    # Grotzsch single-vertex blow-ups
    g11N,g11E=g11
    for v in range(g11N):
        for t in [2,3,4,5,6]:
            extra=t-1; n=g11N+extra
            if n>20: continue
            E=list(g11E); nbr=set()
            for a,b in g11E:
                if a==v: nbr.add(b)
                if b==v: nbr.add(a)
            for c in range(extra):
                nv=g11N+c
                for w in nbr: E.append((nv,w))
            T.append((f"Grotzsch-blow-v{v}x{t}",n,E))
    return T

if __name__=="__main__":
    tasks=gen(); tasks.sort(key=lambda t:t[1])
    print(f"=== PARALLEL HUNT 2: {len(tasks)} tasks ===",flush=True)
    tot=0;toc=0;gmaxO=0;gminr=None;allhits=[]
    with Pool(48) as p:
        for i,(nm,n,ocuts,maxO,minr,hits) in enumerate(p.imap_unordered(worker,tasks,chunksize=8)):
            tot+=1; toc+=ocuts; gmaxO=max(gmaxO,maxO)
            if minr is not None and (gminr is None or minr<gminr): gminr=minr
            if hits:
                allhits.extend(hits)
                for h in hits: print(f"  *** HIT {h['nm']} n={h['n']} |O|={len(h['O'])} fo={h['fo']} ***",flush=True)
            if (i+1)%1000==0:
                print(f"  ...{i+1}/{len(tasks)} O-cuts={toc} maxO={gmaxO} min-ratio={gminr} hits={len(allhits)}",flush=True)
    print(f"=== DONE2: inst={tot} O-cuts={toc} maxO={gmaxO} min-ratio={gminr} HITS={len(allhits)} ===",flush=True)
    for h in allhits: print(h,flush=True)
