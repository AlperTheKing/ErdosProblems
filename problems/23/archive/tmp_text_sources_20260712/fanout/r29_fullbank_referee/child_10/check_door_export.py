#!/usr/bin/env python3
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
def edge(x):
 assert isinstance(x,list) and len(x)==2 and all(isinstance(v,int) for v in x) and x[0]!=x[1]; return tuple(sorted(x))
p=argparse.ArgumentParser(); p.add_argument('export',type=Path); a=p.parse_args(); raw=a.export.read_bytes(); d=json.loads(raw)
assert d['schema']=='r29-own-door-v1' and d['vertex_count']==2943 and d['owner_shore']==[0,1,2]
shore=set(d['active_component_vertices']); assert {0,1,2}<=shore
graph={edge(e) for e in d['graph_edges']}; boundary=sorted(e for e in graph if (e[0] in shore)!=(e[1] in shore)); ports=d['ports']
assert len({x['port_id'] for x in ports})==len(ports) and len({edge(x['edge']) for x in ports})==len(ports) and sorted(edge(x['edge']) for x in ports)==boundary
tokens={x['token_id']:x for x in d['tokens']}; rows=[]; seen=set()
for x in sorted(ports,key=lambda z:z['port_id']):
 e=edge(x['edge']); tid=x['door_token_id']; assert tid not in seen; seen.add(tid); t=tokens[tid]; assert t['component_id']==d['active_component_id'] and t['source']=={'kind':'door','edge':list(e)}; cap=Fraction(str(t['capQ'])); assert cap>=25; rows.append({'port_id':x['port_id'],'edge':list(e),'token_id':tid,'raw_capQ':str(cap),'hall_capQ':str(cap/25)})
o={'input_sha256':hashlib.sha256(raw).hexdigest(),'candidate_count':len(boundary),'total_raw_capQ':str(sum(Fraction(r['raw_capQ']) for r in rows)),'total_hall_capQ':str(sum(Fraction(r['hall_capQ']) for r in rows)),'candidates':rows}; target=Path(__file__).with_name('door_candidates.json'); target.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps({'output':str(target),'candidate_count':len(rows),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},sort_keys=True))
