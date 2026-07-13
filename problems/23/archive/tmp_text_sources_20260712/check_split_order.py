import json
from collections import Counter
import sys
sys.path.insert(0, 'problems/23/writeup')
import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pressure_term_verify as tv

def sigma(ctx,S):
    return len(skel.delta(ctx['blue_edges'], S))-len(skel.delta(ctx['bad_edges'], S))

def count(edges,A,B):
    return sum(1 for u,v in edges if ((u in A and v in B) or (v in A and u in B)))

def qstep(ctx,A,B):
    A=set(A); B=set(B)
    X=B-A; O=set(range(ctx['n']))-B
    return count(ctx['blue_edges'],X,A)-count(ctx['bad_edges'],X,A)-count(ctx['blue_edges'],X,O)+count(ctx['bad_edges'],X,O)

def rho(qs):
    return 25*sum(max(0,q) for q in qs)

rows=[json.loads(l) for l in open('tmp/bankl_completion_rhoa_trace_v2.jsonl',encoding='utf-8') if l.strip()]
cache={}
C=Counter(); examples=[]
for row in rows:
    n=int(row['row_id']['n']); V=set(range(n))
    R=set(row['selected_origin']['raw_interval_verts']); F=set(row['selected_origin']['final_verts'])
    key=tv.row_key_from_lean({'row_id':row['row_id']}); gkey=(key[0],row['side'])
    if gkey not in cache: cache[gkey]=tv.graph_context(key[0],row['side'])
    ctx=cache[gkey]
    U=R|F; I=R&F
    qs_add=[qstep(ctx,R,U), qstep(ctx,V-U,V-F)]
    qs_rem=[qstep(ctx,V-R,V-I), qstep(ctx,I,F)]
    total=sigma(ctx,R)-sigma(ctx,F)
    raw=25*max(0,total)
    assert sum(qs_add)==total, (row['row_id'], qs_add, total)
    assert sum(qs_rem)==total, (row['row_id'], qs_rem, total)
    ra, rr = rho(qs_add), rho(qs_rem)
    C[(raw,ra,rr)] += 1
    if min(ra,rr)!=raw and len(examples)<10:
        examples.append((row['row_id'], sorted(R), sorted(F), total, raw, qs_add, ra, qs_rem, rr))
print('patterns')
for k,v in C.most_common(30): print(k,v)
print('bad_min_examples', len(examples))
for e in examples: print(e)
