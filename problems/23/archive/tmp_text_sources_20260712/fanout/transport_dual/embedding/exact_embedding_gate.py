"""Exact exhaustive gates for component containment and capacitated Hall."""
from itertools import combinations

def edges(n): return list(combinations(range(n), 2))

def comps(n, mask, es):
    unseen, out = set(range(n)), []
    while unseen:
        root = min(unseen); stack = [root]; seen = {root}; unseen.remove(root)
        while stack:
            x = stack.pop()
            for k, (a, b) in enumerate(es):
                if not (mask >> k) & 1: continue
                y = b if a == x else a if b == x else None
                if y is not None and y in unseen:
                    unseen.remove(y); seen.add(y); stack.append(y)
        out.append(frozenset(seen))
    return out

def graph_gate(max_n=5):
    pairs = persistent = fiber_fail = 0; first = None
    for n in range(1, max_n + 1):
        es = edges(n)
        for old in range(1 << len(es)):
          oc = comps(n, old, es)
          for new in range(1 << len(es)):
            changed = {v for k,e in enumerate(es) if ((old>>k)^(new>>k))&1 for v in e}
            pairs += 1; image = {}
            for c in comps(n, new, es):
                if c & changed: continue
                persistent += 1
                owners = [j for j,d in enumerate(oc) if c <= d]
                assert len(owners) == 1
                image.setdefault(owners[0], []).append(c)
            bad = [(j,cs) for j,cs in image.items() if len(cs)>1]
            if bad:
                fiber_fail += 1
                w=(n,old.bit_count()+new.bit_count(),old,new,tuple(sorted(changed)),bad)
                if first is None or w[:2] < first[:2]: first=w
    return pairs,persistent,fiber_fail,first

def hall_gate(max_d=4,max_s=4):
    systems=subset_checks=mismatches=0; first=None
    for d in range(max_d+1):
      for s in range(max_s+1):
       for rel in range(1<<(d*s)):
        eligible=[(rel>>(x*s))&((1<<s)-1) for x in range(d)]
        for outside in range(d+1):
          systems += 1; hall=True
          for X in range(1<<d):
            subset_checks += 1; neigh=0
            for x in range(d):
                if (X>>x)&1: neigh |= eligible[x]
            if X.bit_count()>outside+neigh.bit_count(): hall=False; break
          def search(x,used):
            if x==d:return True
            allowed=((1<<outside)-1)|(eligible[x]<<outside); free=allowed&~used
            while free:
                bit=free&-free
                if search(x+1,used|bit):return True
                free-=bit
            return False
          match=search(0,0)
          if hall!=match:
            mismatches+=1; first=first or (d,s,outside,eligible,hall,match)
    return systems,subset_checks,mismatches,first

if __name__=='__main__':
    gp=graph_gate(); hg=hall_gate()
    print('GRAPH_PAIRS',gp[0]); print('PERSISTENT_COMPONENTS',gp[1])
    print('NONINJECTIVE_COMPONENT_MAP_PAIRS',gp[2]); print('SMALLEST_COMPONENT_FALSIFIER',gp[3])
    print('HALL_SYSTEMS',hg[0]); print('HALL_SUBSET_CHECKS',hg[1])
    print('HALL_EQUIV_MISMATCHES',hg[2]); print('HALL_FIRST_MISMATCH',hg[3])
