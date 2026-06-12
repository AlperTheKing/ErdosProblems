from pathlib import Path
import subprocess,re
repo=Path(r'E:\Projects\ErdosProblems\workers\codex\formal-conjectures')
path='FormalConjectures/ErdosProblems/26.lean'
cur=(repo/path).read_text(encoding='utf-8')
old=subprocess.check_output(['git','show','HEAD:'+path], cwd=repo).decode('utf-8')
key='theorem erdos_26.variants.tenenbaum'
def sig(s):
    i=s.index(key)
    j=s.index(':= by', i)
    return s[i:j]
print('statement_unchanged', sig(cur)==sig(old))
patch=Path(r'E:\Projects\ErdosProblems\coordination\patches\Erdos26_tenenbaum_codex_open.patch').read_text(encoding='utf-8')
for pat in ['admit','axiom','native_decide','unsafe','macro','elab','extern','implemented_by']:
    print(pat, bool(re.search(r'(^|[^A-Za-z0-9_])'+re.escape(pat)+r'([^A-Za-z0-9_]|$)', patch)))
print('patch_path', r'E:\Projects\ErdosProblems\coordination\patches\Erdos26_tenenbaum_codex_open.patch')
