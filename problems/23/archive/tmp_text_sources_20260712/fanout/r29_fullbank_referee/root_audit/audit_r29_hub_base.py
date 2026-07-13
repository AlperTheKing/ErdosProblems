#!/usr/bin/env python3
"""Exact clean-room audit of R29 hub-shore base-transfer sources."""
from fractions import Fraction
from itertools import product
N=2943; HUBS=(0,1,2); LEFT=tuple(range(3,29)); RIGHT=tuple(range(29,55)); LEAVES=LEFT+RIGHT
RIGID=tuple((l,1,0,2,r) for l,r in product(LEFT,RIGHT)); assert len(RIGID)==676
companions={h:set() for h in HUBS}
for row in RIGID:
 for h in HUBS: companions[h].update(row); companions[h].discard(h)
assert all(companions[h]==(set(HUBS)-{h})|set(LEAVES) for h in HUBS)
def same_first(h): return {(h,y,b) for y in range(N) for b in (0,1) if y!=h and y not in companions[h]}
raw=set().union(*(same_first(h) for h in HUBS)); assert len(raw)==17328
reserved={(h,2940+h,0) for h in HUBS}; assert reserved<=raw
same=raw-reserved; assert len(same)==17325
bad_neighbours={h:set() for h in HUBS}
common={(x,y,b) for h in HUBS for x in bad_neighbours[h] for y in bad_neighbours[h] for b in (0,1) if x!=y}; assert not common
aux,demand=19925,19953; assert aux-len(same)==2600 and demand-aux==28
print(f'N={N}\nrigid_double_star_rows={len(RIGID)}\nhub_companions_each={len(companions[0])}')
print(f'sameFirst_raw_half_keys={len(raw)}\nScopedReserved_hub_keys={len(reserved)}')
print(f'sameFirst_available_half_keys={len(same)}\ncommonBad_available_half_keys={len(common)}\nbase_union_half_keys={len(same|common)}')
print(f'base_capacity=17325/(2*K); at_K_1={len(same)*Fraction(1,2)}\ncommonBad_capacity=0')
print(f'aux_rowCompanion_increment={aux-len(same)}\naux_scoped_total={aux}\nall_anchor_demand={demand}')
print(f'base_only_defect={demand-len(same)}\naux_scoped_defect={demand-aux}')
print('selector_invariant=hub pairCount, raw sameFirst, hub bad-neighbours')
print('selector_variable=ActiveOwner, activeDegree/hitNeed, ScopedReserved')
