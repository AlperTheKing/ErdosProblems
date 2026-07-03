import json, itertools, sys
sys.path.insert(0, 'problems/23/writeup')
import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pressure_term_verify as tv

def sigma(ctx,S): return len(skel.delta(ctx['blue_edges'],S))-len(skel.delta(ctx['bad_edges'],S))
rows=[json.loads(l) for l in open('tmp/bankl_completion_rhoa_trace_v2.jsonl',encoding='utf-8') if l.strip()]
cache={}
for row in rows:
    R=set(row['selected_origin']['raw_interval_verts']); F=set(row['selected_origin']['final_verts'])
    key=tv.row_key_from_lean({'row_id':row['row_id']}); gkey=(key[0],row['side'])
    if gkey not in cache: cache[gkey]=tv.graph_context(key[0],row['side'])
    ctx=cache[gkey]
    total=sigma(ctx,R)-sigma(ctx,F); raw=25*max(0,total)
    if raw==125 and len(R-F)==3 and len(F-R)==1:
        ops=[('add',v) for v in sorted(F-R)] + [('del',v) for v in sorted(R-F)]
        best=None; bestperm=None; bestqs=None
        for perm in itertools.permutations(ops):
            S=set(R); qs=[]; ok=True
            for typ,v in perm:
                S2=set(S)
                if typ=='add':
                    if v in S2: ok=False; break
                    S2.add(v)
                else:
                    if v not in S2: ok=False; break
                    S2.remove(v)
                q=sigma(ctx,S)-sigma(ctx,S2)
                qs.append(q); S=S2
            if ok and S==F:
                cost=25*sum(max(0,q) for q in qs)
                if best is None or cost<best:
                    best=cost; bestperm=perm; bestqs=qs
        print(row['row_id'], 'raw', raw, 'best', best, 'perm', bestperm, 'qs', bestqs)
