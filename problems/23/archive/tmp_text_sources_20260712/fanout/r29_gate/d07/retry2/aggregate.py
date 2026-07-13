import glob, hashlib, json
parts=[json.load(open(p)) for p in sorted(glob.glob('part_*.json'))]
h={}
for x in parts:
 for k,v in x['delta_histogram'].items(): h[int(k)]=h.get(int(k),0)+v
assert sum(x['replacements'] for x in parts)==459004
assert len(parts)==16
out={'baseline_score':30811,'replacements':459004,
 'delta_histogram':{str(k):h[k] for k in sorted(h)},
 'minimum_delta':min(h),'minimum_multiplicity':h[min(h)],
 'q_minus_p_empty_falsifier':next((x['q_minus_p_empty_falsifier'] for x in parts if x['q_minus_p_empty_falsifier']),None),
 'diagonal_collision_falsifier':next((x['diagonal_collision_falsifier'] for x in parts if x['diagonal_collision_falsifier']),None),
 'positive_owner_persistence_falsifier':next((x['positive_owner_persistence_falsifier'] for x in parts if x['positive_owner_persistence_falsifier']),None),
 'whole_active_set_persistence_falsifier':next(x['whole_active_set_persistence_falsifier'] for x in parts if x['whole_active_set_persistence_falsifier']),
 'sharp_witness':next(x['sharp_witness'] for x in parts if x['minimum_delta']==min(h)),
 'input_sha256':parts[0]['input_sha256'],'lead_source_sha256':parts[0]['lead_source_sha256']}
raw=json.dumps(out,sort_keys=True,indent=2)+'\n';open('aggregate_result.json','w').write(raw)
print(raw);print('aggregate_sha256',hashlib.sha256(raw.encode()).hexdigest())
