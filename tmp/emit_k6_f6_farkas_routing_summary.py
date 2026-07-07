import json, pathlib, hashlib
ray=json.loads(pathlib.Path('tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_exact_replay_v1.json').read_text())
known=json.loads(pathlib.Path('tmp/eq_odl1_rung2_k6_F6_known_cert_vs_step3_farkas_ray_v1.json').read_text())
float_ray=json.loads(pathlib.Path('tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_support_v1.json').read_text())
pos_fams=[]
for f in known['families_by_weighted_score']:
    if f['positive_count']>0:
        pos_fams.append({
            'family': f['family'],
            'known_support_count': f['count'],
            'positive_ray_score_count': f['positive_count'],
            'max_ray_score': f['max_score'],
        })
pos_fams.sort(key=lambda r: (r['positive_ray_score_count'], r['max_ray_score']['num']/r['max_ray_score']['den']), reverse=True)
def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest().upper()
out={
    'schema':'eq_odl1_rung2_k6_F6_step3_farkas_routing_summary_v1',
    'restricted_pool':'step3 40696-column target-active tier3-derived {F5,G2_UZ_T,G3_XY_T,G7_B2_4T}',
    'farkas_exact_replay':'tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_exact_replay_v1.json',
    'farkas_exact_replay_sha256':sha('tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_exact_replay_v1.json'),
    'farkas_float_support':'tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_support_v1.json',
    'farkas_float_support_sha256':sha('tmp/eq_odl1_rung2_k6_F6_step3_farkas_ray_support_v1.json'),
    'known_cert_cross_score':'tmp/eq_odl1_rung2_k6_F6_known_cert_vs_step3_farkas_ray_v1.json',
    'known_cert_cross_score_sha256':sha('tmp/eq_odl1_rung2_k6_F6_known_cert_vs_step3_farkas_ray_v1.json'),
    'exact_farkas':{
        'support_count':ray['support_count'],
        'y_dot_b':ray['y_dot_b'],
        'max_column_score':ray['max_column_score'],
        'positive_column_score_count':ray['positive_column_score_count'],
        'zero_column_score_count':ray['zero_column_score_count'],
        'negative_column_score_count':ray['negative_column_score_count'],
    },
    'ray_support_rows':ray['ray_support'],
    'known_good_positive_score_families':pos_fams,
    'float_seed_score_max':float_ray['ray_summary']['seed_score_max'],
}
path=pathlib.Path('tmp/eq_odl1_rung2_k6_F6_step3_farkas_routing_summary_v1.json')
path.write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
print(path)
print(sha(path))
print('positive_families', [(f['family'], f['positive_ray_score_count'], f['max_ray_score']['str']) for f in pos_fams])
