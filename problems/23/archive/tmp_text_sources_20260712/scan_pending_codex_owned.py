import json, glob, pathlib

d=json.load(open('tmp/eq_odl1_rung2_chart_batch_ledger_v52_codex.json'))
names=['F1','F2','F3','F4','F5','F6','F7','B0','G1','G2','G3','G4','G5','G6','G7']
claimed={(8,0),(8,5),(8,8),(8,11),(1,13),(1,14),(2,13),(0,0),(0,14),(0,11),(0,4),(9,7),(7,7),(3,1),(3,13),(4,13),(6,13),(9,13),(9,5),(4,2),(4,10)}
for r in d['pending_rows_prefix'][:54]:
    key=(r['chart'],r['dominant'])
    if key in claimed:
        continue
    fam=names[r['dominant']]
    files=glob.glob(f'tmp/eq_odl1_rung2_source_solution_check_k{r["chart"]}_{fam}*.json')+glob.glob(f'tmp/eq_odl1_rung2_source_solution_check_k{r["chart"]}_d{r["dominant"]}*.json')
    best=None
    for p in files:
        try:
            x=json.load(open(p))
            sev=(int(x.get('full_negative_residual_count',999999)), int(x.get('solution_negative_count',999999)), -pathlib.Path(p).stat().st_mtime, p)
        except Exception:
            continue
        if best is None or sev<best:
            best=sev
    print(key, r['dominant_name'], 'vars', r['variables'], 'best', best[:2] if best else None, pathlib.Path(best[3]).name if best else '-')
