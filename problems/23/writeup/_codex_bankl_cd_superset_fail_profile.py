"""Profile failures of the all-superset aggregate CD gate."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from _codex_bankl_cd_superset_gate import graph_from_name  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_cd_superset_gate_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_cd_superset_fail_profile_v1.json")
    args = ap.parse_args()

    by_n_m: Counter[tuple[int, int]] = Counter()
    by_margin_p: Counter[tuple[int, str]] = Counter()
    by_n_m_p: Counter[tuple[int, int, str]] = Counter()
    examples = {}
    fail = 0

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("status") != "FAIL":
                continue
            fail += 1
            _n, edges = graph_from_name(rec["name"])
            side = [int(x) for x in rec["side"]]
            m = sum(1 for u, v in edges if side[u] == side[v])
            by_n_m[(rec["n"], m)] += 1
            by_margin_p[(rec["margin"], rec["P_Q"])] += 1
            by_n_m_p[(rec["n"], m, rec["P_Q"])] += 1
            key = f"n{rec['n']}_m{m}"
            examples.setdefault(
                key,
                {
                    "name": rec["name"],
                    "side": rec["side"],
                    "row": rec["row"],
                    "P_Q": rec["P_Q"],
                    "rho_Q": rec["rho_Q"],
                    "margin": rec["margin"],
                    "sum_25sigma0": rec["sum_25sigma0"],
                    "sum_best_nuK": rec["sum_best_nuK"],
                    "raw_sigma0": [x["raw_sigma0"] for x in rec["intervals"]],
                    "best_nuK": [None if x["best"] is None else x["best"]["nuK"] for x in rec["intervals"]],
                },
            )

    summary = {
        "input": args.input,
        "fail": fail,
        "by_n_m": {repr(k): v for k, v in sorted(by_n_m.items(), key=lambda kv: repr(kv[0]))},
        "by_n_m_p": {repr(k): v for k, v in sorted(by_n_m_p.items(), key=lambda kv: repr(kv[0]))},
        "top_margin_P_Q": [(repr(k), v) for k, v in by_margin_p.most_common(30)],
        "examples": examples,
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output, "fail": fail, "by_n_m": summary["by_n_m"]}, sort_keys=True))


if __name__ == "__main__":
    main()
