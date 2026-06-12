from pathlib import Path
import subprocess
repo=Path(r'E:\Projects\ErdosProblems\workers\codex\formal-conjectures')
path='FormalConjectures/ErdosProblems/26.lean'
cur=(repo/path).read_text(encoding='utf-8')
old=subprocess.check_output(['git','show','HEAD:'+path], cwd=repo).decode('utf-8')
key='theorem erdos_26.variants.tenenbaum'
def sig(s):
    i=s.index(key)
    j=s.index(':= by', i)
    return s[i:j]
print(sig(cur)==sig(old))
print(sig(cur))
