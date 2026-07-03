"""Cross-profile CD bridge failures against the surviving pressure-cover artifact."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cd", default="tmp/bankl_cd_superset_gate_v1.jsonl")
    ap.add_argument("--lean", default="tmp/bankl_pressure_cover_lean_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_cd_failure_cover_profile_v1.json")
    args = ap.parse_args()

    lean = {}
    with Path(args.lean).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            rid = rec["row_id"]
            lean[(rid["name"], tuple(rid["row"]), tuple(rid["f"]), rid["n"])] = rec

    counts: Counter[tuple[str, str | None]] = Counter()
    by_n_m_case: Counter[tuple[int, int, str, str | None]] = Counter()
    examples = {}
    missing = []
    fail = 0
    with Path(args.cd).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            cd = json.loads(line)
            if cd.get("status") != "FAIL":
                continue
            fail += 1
            key = (cd["name"], tuple(cd["row"]), tuple(cd["f"]), cd["n"])
            lr = lean.get(key)
            if lr is None:
                missing.append({"name": cd["name"], "n": cd["n"], "f": cd["f"], "row": cd["row"]})
                continue
            case = lr["proof_case"]
            termkind = None if not lr["terms"] else lr["terms"][0]["kind"]
            counts[(case, termkind)] += 1
            m = lr["row_id"]["m"]
            by_n_m_case[(cd["n"], m, case, termkind)] += 1
            ex_key = repr((case, termkind))
            examples.setdefault(
                ex_key,
                {
                    "cd": {
                        "name": cd["name"],
                        "n": cd["n"],
                        "row": cd["row"],
                        "P_Q": cd["P_Q"],
                        "margin": cd["margin"],
                        "sum_25sigma0": cd["sum_25sigma0"],
                        "sum_best_nuK": cd["sum_best_nuK"],
                    },
                    "lean": {
                        "proof_case": case,
                        "terms": lr["terms"][:1],
                        "identity": lr["identity"],
                        "mu_bound": lr["mu_bound"],
                    },
                },
            )

    summary = {
        "cd_input": args.cd,
        "lean_input": args.lean,
        "cd_fail_rows": fail,
        "missing_in_lean": len(missing),
        "counts": {repr(k): v for k, v in sorted(counts.items(), key=lambda kv: repr(kv[0]))},
        "by_n_m_case": {repr(k): v for k, v in sorted(by_n_m_case.items(), key=lambda kv: repr(kv[0]))},
        "examples": examples,
        "missing_examples": missing[:5],
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": args.output,
        "cd_fail_rows": fail,
        "missing_in_lean": len(missing),
        "counts": summary["counts"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
