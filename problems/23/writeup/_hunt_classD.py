"""CLASS D hunt: near-extremal perturbations of C_{2k+1}[t] uniform blow-ups.
Goal: triangle-free + gamma-min connected-B MAX cut where ROW-SUM FAILS but full-g (opencap cert) HOLDS,
with |O|>=2. EXACT (Fraction). Route blow-ups through gmins (real gamma-min max cuts only)."""
import itertools, sys
from fractions import Fraction as F
from _opencap import opencap
from _rowsum import rowsum
from _stark1 import gmins
from _bdef_construct import is_triangle_free

def edges_from_sizes(m, sizes):
    n=sum(sizes); start=[0]*m
    for i in range(1,m): start[i]=start[i-1]+sizes[i-1]
    E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                E.append((start[i]+a, start[j]+b))
    return n,E

best_ratio=None  # smallest LB/D over ALL rowsum-evaluated o (held cases)
best_ratio_info=None
min_rowsum_seen=None  # smallest minratio dict value across rowsum calls
maxO=0
rowsum_fails_total=0
instances=0
counterexamples=[]
seen_graphs=set()

def test(m, sizes, tag):
    global best_ratio,best_ratio_info,maxO,rowsum_fails_total,instances,min_rowsum_seen,counterexamples
    n,E=edges_from_sizes(m,sizes)
    if n>20: return
    key=(n,frozenset((min(a,b),max(a,b)) for a,b in E))
    if key in seen_graphs: return
    seen_graphs.add(key)
    if not is_triangle_free(n,E): return
    print(f"  [n={n}] {tag} sizes={sizes} ...",flush=True)
    adj,cuts=gmins(n,E)   # real gamma-min connected-B max cuts
    if not cuts: return
    for side in cuts:
        rs=rowsum(adj,side,n)
        if rs is None or rs.get('skip'): continue
        instances+=1
        O=rs['O']; maxO=max(maxO,O)
        if rs['minratio'] is not None:
            mr=rs['minratio']
            if min_rowsum_seen is None or mr<min_rowsum_seen:
                min_rowsum_seen=mr; best_ratio_info=(tag,sizes,O,float(mr))
        if rs['fails']>0:
            rowsum_fails_total+=1
            oc=opencap(adj,side,n)
            if oc and not oc.get('skip') and oc.get('cert')==True and O>=2:
                # REAL counterexample: rowsum fails, full-g holds, |O|>=2, gamma-min max cut
                # find a failing o
                from _opencap import build_K
                K,T=build_K(adj,side,n)
                Os=[v for v in range(n) if T[v]>n]; Q=[v for v in range(n) if T[v]<=n]
                s={q:sum(K[o][q] for o in Os) for q in Q}
                fo=None; To=None
                for o in Os:
                    D=T[o]-n; lhs=F(0)
                    for q in Q:
                        Rq=F(n)-T[q]; den=Rq+s[q]
                        if den>0 and K[o][q]>0: lhs+=K[o][q]*Rq/den
                    if lhs-D<0: fo=o; To=T[o]; break
                counterexamples.append(dict(n=n,E=E,side=side,o=O,To=str(To),N=n,
                    note=f"{tag} sizes={sizes} failing_o={fo} T(o)={To} N={n}"))
                print(f"!!! COUNTEREXAMPLE {tag} sizes={sizes} O={O} fail_o={fo} T(o)={To} N={n}",flush=True)

# Base uniform blow-ups C5[t],C7[t],C9[t] and +-1/+-2 perturbations of part sizes.
for m,ks in [(5,[2,3,4]),(7,[2,3]),(9,[2])]:
    for t in ks:
        base=[t]*m
        # uniform itself
        test(m,base,f"C{m}[{t}]uniform")
        # single perturbations
        for i in range(m):
            for d in (-2,-1,1,2):
                s=base[:]; s[i]+=d
                if min(s)<1: continue
                if sum(s)>20: continue
                test(m,tuple(s),f"C{m}[{t}]+d{d}@{i}")
        # double perturbations (two parts)
        for i in range(m):
            for j in range(i+1,m):
                for di in (-2,-1,1,2):
                    for dj in (-2,-1,1,2):
                        s=base[:]; s[i]+=di; s[j]+=dj
                        if min(s)<1 or sum(s)>20: continue
                        test(m,tuple(s),f"C{m}[{t}]dd")

print(f"instances_tested={instances}",flush=True)
print(f"maxO={maxO}",flush=True)
print(f"rowsum_fails_total={rowsum_fails_total}",flush=True)
print(f"min_rowsum_ratio_seen={min_rowsum_seen} ({float(min_rowsum_seen) if min_rowsum_seen else None}) info={best_ratio_info}",flush=True)
print(f"counterexamples={len(counterexamples)}",flush=True)
for c in counterexamples:
    print(c,flush=True)
