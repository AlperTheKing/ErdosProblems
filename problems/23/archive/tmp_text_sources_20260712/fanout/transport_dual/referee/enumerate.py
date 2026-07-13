from itertools import product
import json
from pathlib import Path

def instances(limit=4):
    for dA, sA, out, new in product(range(limit + 1), repeat=4):
        if not (sA < dA): continue
        collision_delta = new - (dA + out)
        collision_bound = sA - dA
        target_card = out + sA
        if collision_delta <= collision_bound and new <= target_card and new > out:
            yield dict(dA=dA,sA=sA,outside_old=out,new=new,
              collision_delta=collision_delta,collision_bound=collision_bound,
              hitneed_delta=0,target_card=target_card,eligible_source_edges=0,
              abstract_components={'old_shore':'C_a','new':'C_b'},
              changed_row_touches_new=False,
              persistent_embedding='C_b(new) subset C_b(old)')
models=sorted(instances(),key=lambda m:(sum(m[k] for k in ('dA','sA','outside_old','new')),m['dA'],m['sA'],m['outside_old'],m['new']))
assert models
w=models[0]
assert (w['dA'],w['sA'],w['outside_old'],w['new'])==(2,1,0,1)
assert w['collision_delta']==w['collision_bound']==-1
assert not [m for m in models if sum(m[k] for k in ('dA','sA','outside_old','new'))<4]
Path(__file__).with_name('smallest_falsifier.json').write_text(json.dumps({'search_box':'0<=dA,sA,outside_old,new<=4; one alternative; integer exact','models_found':len(models),'smallest_total_entities_counted_with_multiplicity':4,'witness':w,'necessary_and_sufficient_extra_axiom_finite':'For every X of new demands, |X| <= outside_slots + |N_eligible(X)|'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'models_found':len(models),'smallest':w},sort_keys=True))
