"""Parallel HUNT for ROW-SUM counterexample. Each task = (name, n, E). Worker runs gmins + rowsum + opencap.
Returns (name, n, ocuts, rfail, maxO, minratio_float_or_None, hits[list of dict]).
A hit = gamma-min connected-B max cut, |O|>=2, ROW-SUM fails, opencap cert True."""
import itertools, sys
from fractions import Fraction as F
from multiprocessing import Pool
from _opencap import opencap, build_K
from _rowsum import rowsum
from _stark1 import odd_blowup, gmins
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def worker(task):
    nm,n,E=task
    if n>20 or not is_triangle_free(n,E):
        return (nm,n,0,0,0,None,[])
    adj,cuts=gmins(n,E)
    ocuts=0; rfail=0; maxO=0; minr=None; hits=[]
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
    return (nm,n,ocuts,rfail,maxO,(float(minr) if minr is not None else None),hits)

def gen_tasks():
    T=[]
    # C5 blow-ups, n<=20
    for sz in itertools.product([1,2,3,4,5,6,7,8],repeat=5):
        if sum(sz)>20: continue
        n,E,_,_=odd_blowup(5,list(sz)); T.append((f"C5{sz}",n,E))
    # C7 blow-ups n<=20
    for sz in itertools.product([1,2,3,4],repeat=7):
        if sum(sz)>20: continue
        n,E,_,_=odd_blowup(7,list(sz)); T.append((f"C7{sz}",n,E))
    # C9 small
    for sz in itertools.product([1,2],repeat=9):
        if sum(sz)>20: continue
        n,E,_,_=odd_blowup(9,list(sz)); T.append((f"C9{sz}",n,E))
    # C11 small
    for sz in itertools.product([1,2],repeat=11):
        if sum(sz)>20: continue
        n,E,_,_=odd_blowup(11,list(sz)); T.append((f"C11{sz}",n,E))
    # Mycielskian of small odd-cycle blow-ups
    for sz in itertools.product([1,2],repeat=5):
        bN,bE,_,_=odd_blowup(5,list(sz)); n,E=mycielski(bN,bE)
        if n<=20: T.append((f"Myc(C5{sz})",n,E))
    for sz in itertools.product([1,2],repeat=7):
        if sum(sz)>9: continue
        bN,bE,_,_=odd_blowup(7,list(sz)); n,E=mycielski(bN,bE)
        if n<=20: T.append((f"Myc(C7{sz})",n,E))
    return T

if __name__=="__main__":
    tasks=gen_tasks()
    # sort smaller-n first for fast incremental feedback
    tasks.sort(key=lambda t:t[1])
    print(f"=== PARALLEL HUNT: {len(tasks)} tasks ===",flush=True)
    tot_inst=0; tot_ocuts=0; tot_rfail=0; gmaxO=0; gminr=None; allhits=[]
    with Pool(48) as p:
        for i,(nm,n,ocuts,rfail,maxO,minr,hits) in enumerate(p.imap_unordered(worker,tasks,chunksize=8)):
            tot_inst+=1; tot_ocuts+=ocuts; gmaxO=max(gmaxO,maxO)
            if minr is not None and (gminr is None or minr<gminr): gminr=minr
            if hits:
                allhits.extend(hits)
                for h in hits: print(f"  *** HIT {h['nm']} n={h['n']} |O|={len(h['O'])} fo={h['fo']} ***",flush=True)
            if (i+1)%2000==0:
                print(f"  ...{i+1}/{len(tasks)} O-cuts={tot_ocuts} maxO={gmaxO} min-ratio={gminr} hits={len(allhits)}",flush=True)
    print(f"=== DONE: inst={tot_inst} O-cuts={tot_ocuts} maxO={gmaxO} min-ratio={gminr} HITS={len(allhits)} ===",flush=True)
    for h in allhits: print(h,flush=True)
