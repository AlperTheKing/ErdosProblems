"""Write SHA256 manifest for lane09 artifacts."""
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
names=['audit_r29_fullbank.py','audit_result.json','REPORT.md','make_hashes.py']
out={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in names}
(HERE/'HASHES.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,sort_keys=True,indent=2))
