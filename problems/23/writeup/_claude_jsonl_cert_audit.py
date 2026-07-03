"""Claude independent audit of tmp/bankl_lcb_certs_n11.jsonl (bankl_lcb_cert_v1).
Checks per row: schema key; certificate_status SAT; certificate_verified true;
exact Fraction re-sum of certificate_terms == certificate_target; kind/scope
consistency (underfull/equal must not use sparse/size kinds); recount totals."""
import json
import sys
from fractions import Fraction as F
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else r"E:\Projects\ErdosProblems\tmp\bankl_lcb_certs_n11.jsonl"


def to_frac(x):
    if isinstance(x, str):
        return F(x)
    if isinstance(x, (int,)):
        return F(x)
    if isinstance(x, list) and len(x) == 2:
        return F(x[0], x[1])
    raise ValueError(f"unparseable rational: {x!r}")


kinds = Counter()
scopes = Counter()
cross = Counter()
rows = 0
fails = []
with open(path, "r", encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        rows += 1
        try:
            assert rec.get("schema", rec.get("schema_key", "bankl_lcb_cert_v1")) in (
                "bankl_lcb_cert_v1",), "schema"
            kind = rec["certificate_kind"]
            scope = rec["row_scope"]
            kinds[kind] += 1
            scopes[scope] += 1
            cross[f"{scope}:{kind}"] += 1
            assert rec["certificate_status"] == "SAT", "status"
            assert rec["certificate_verified"] is True, "verified-flag"
            target = to_frac(rec["certificate_target"])
            terms = rec.get("certificate_terms", [])
            ssum = F(0)
            for t in terms:
                coeff = to_frac(t.get("coeff", t.get("coefficient", 1)))
                val = to_frac(t.get("value", t.get("term_value")))
                contrib = t.get("contribution")
                c2 = coeff * val
                if contrib is not None:
                    assert to_frac(contrib) == c2, "contribution mismatch"
                ssum += c2
            if kind != "tight":
                assert ssum == target, f"sum {ssum} != target {target}"
            else:
                assert target == 0 and ssum == 0, "tight nonzero"
            if scope in ("underfull", "equal"):
                assert kind not in ("sparse", "size", "size2"), "scope fallback"
        except AssertionError as e:
            fails.append((rows, str(e), rec.get("name"), rec.get("f"), rec.get("row")))
            if len(fails) > 5:
                break

print(f"rows={rows} fails={len(fails)}")
print("kinds:", dict(kinds))
print("scopes:", dict(scopes))
print("cross:", dict(sorted(cross.items())))
for f_ in fails:
    print("FAIL:", f_)
print("VERDICT:", "PASS independent recount+identities" if not fails else "FAIL")
