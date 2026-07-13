from hashlib import sha256
from pathlib import Path

here=Path(__file__).resolve().parent
names=("prompt.txt","verify.py","verify.out","result.json","report.md","make_hashes.py")
lines=[f"{sha256((here/n).read_bytes()).hexdigest()}  {n}" for n in names]
(here/"hashes.sha256").write_text("\n".join(lines)+"\n",encoding="ascii")
print("\n".join(lines))
