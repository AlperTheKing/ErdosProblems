import itertools
from _hunt_classA2 import cycle_edges
from _rowsum import rowsum
from _opencap import opencap
from _stark1 import gmins
from _bdef_construct import is_triangle_free

acc=dict(inst=0,cuts=0,rfail=0,certok_cand=0,maxO=0,minratio=None,hits=[])

def test(m,sizes):
    n,E=cycle_edges(m,list(sizes))
    if not is_triangle_free(n,E): return
    adj,cuts=gmins(n,E)
    for s in cuts:
        rs=rowsum(adj,s,n)
        if rs is None or rs.get('skip'): continue
        acc['cuts']+=1; acc['maxO']=max(acc['maxO'],rs['O'])
        if rs['minratio'] is not None:
            fr=float(rs['minratio'])
            if acc['minratio'] is None or fr<acc['minratio']: acc['minratio']=fr
        if rs['fails']>0:
            acc['rfail']+=1
            oc=opencap(adj,s,n)
            certok=oc and not oc.get('skip') and not oc.get('singular') and oc.get('cert')
            if certok and rs['O']>=2:
                acc['certok_cand']+=1; acc['hits'].append((m,sizes,list(s),n,E))
                print('CAND',m,sizes,n,rs['O'],flush=True)

for sizes in itertools.product([1,2,3,4,5,7,9],repeat=5):
    if sum(sizes)>14: continue
    acc['inst']+=1; test(5,sizes)
print('C5<=14',{k:acc[k] for k in('inst','cuts','rfail','certok_cand','maxO','minratio')},flush=True)

for sizes in itertools.product([1,2,3],repeat=7):
    if sum(sizes)>14: continue
    acc['inst']+=1; test(7,sizes)
print('after C7',{k:acc[k] for k in('inst','cuts','rfail','certok_cand','maxO','minratio')},flush=True)
print('HITS',acc['hits'][:5])
