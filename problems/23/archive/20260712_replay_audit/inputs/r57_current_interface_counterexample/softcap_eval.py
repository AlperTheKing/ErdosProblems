import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
soft_path = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate" / "global_softcap.py"
spec = importlib.util.spec_from_file_location("r53_global_softcap", soft_path)
soft = importlib.util.module_from_spec(spec)
assert spec.loader is not None
import sys
sys.modules[spec.name] = soft
spec.loader.exec_module(soft)

names = ["s", "t", "a1", "a2", "a3", "b1", "b2", "b3"]
core = {name: i for i, name in enumerate(names)}
leaves = {name: i + 8 for i, name in enumerate(names)}

def edge(u, v):
    return (u, v) if u < v else (v, u)

P = tuple(core[x] for x in ("s", "a1", "a2", "a3", "t"))
Q = tuple(core[x] for x in ("s", "b1", "b2", "b3", "t"))
blue = {edge(u, v) for row in (P, Q) for u, v in zip(row, row[1:])}
blue |= {edge(core[x], leaves[x]) for x in names}
bad = {edge(core["s"], core["t"])}
ctx = soft.make_graph_context(16, blue, bad)
for label, row in (("P", P), ("Q", Q)):
    summary, _ = soft.analyze_global(ctx, (row,))
    print(label, "demand", summary["state"]["globalCollisionHalfDemand"], "defect", summary["minimumDefect"], "flow", summary.get("maximumFlow"))
    assert summary["minimumDefect"] == 0
print("PASS_R57_FORK_GRAPH_SOFTCAP_DEFECT_ZERO")
