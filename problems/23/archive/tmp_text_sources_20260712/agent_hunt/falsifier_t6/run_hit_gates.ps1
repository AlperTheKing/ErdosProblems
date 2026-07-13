param(
    [Parameter(Mandatory=$true)][string]$HitJson,
    [int]$HitIndex = 0
)
# Full gate pipeline for a t=6 sweep hit:
#   gate a+b replay: verify_tN_hit.py  (classifier vector, circuit axioms,
#                    constructive rows, scope replay, exact min sigma)
#   gate c:          extend_tN_hit_maxcut.py (ambient row-preserving maxcut)
$ErrorActionPreference = "Stop"
Set-Location E:\Projects\ErdosProblems\tmp\agent_hunt\falsifier_t6
$base = [System.IO.Path]::GetFileNameWithoutExtension($HitJson)
python verify_tN_hit.py $HitJson --hit-index $HitIndex --output "${base}_hit${HitIndex}_verify.json"
if ($LASTEXITCODE -ne 0) { throw "verify failed" }
python extend_tN_hit_maxcut.py $HitJson --hit-index $HitIndex --workers 8 --iterations 400 --solve-time 60 --output "${base}_hit${HitIndex}_extend.json"
if ($LASTEXITCODE -ne 0) { throw "extend failed" }
python -c "import json; v=json.load(open('${base}_hit${HitIndex}_verify.json')); e=json.load(open('${base}_hit${HitIndex}_extend.json')); print('VERIFY:', v['verdict'], 'vector', v['classifierVector'], 'scope', (v['scopeReplay'] or {}).get('capturedBadAtoms')); print('EXTEND:', e['verdict'], [s['status'] for s in e['splits']])"
