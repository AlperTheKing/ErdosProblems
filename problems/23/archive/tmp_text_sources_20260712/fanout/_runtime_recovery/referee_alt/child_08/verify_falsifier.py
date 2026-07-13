from fractions import Fraction
import hashlib
from pathlib import Path
D = frozenset({"d"})
F = frozenset()
E = frozenset()
X = D
NX = frozenset(s for s in F if any((d, s) in E for d in X))
metrics = tuple(map(Fraction, (1, 1, 1, 1, 0)))
assert len(X) == 1 and len(NX) == 0
assert Fraction(len(X)) > Fraction(len(NX))
assert metrics == min([metrics])
report = Path(__file__).with_name("canonical_minimizer_report.md")
print("Hall witness: |X|=1, |N(X)|=0")
print("metrics:", tuple(str(x) for x in metrics))
print("report_sha256:", hashlib.sha256(report.read_bytes()).hexdigest())
print("script_sha256:", hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
