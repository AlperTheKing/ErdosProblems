#!/usr/bin/env python3
"""Emit uniform O14 per-chart bridge modules.

Each generated bridge mirrors the accepted Chart000Bridge theorem: a chart's
chunked cone witness proves `CoreODLGoal` once the instance-specific semantic
bindings provide env nonnegativity, slack nonnegativity, combo equality, and
target/core-defect equality.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "problems/23/lean/Erdos23Delta0/O14/Generated/ChartPayloads"


def parse_slots(raw: str) -> list[int]:
    out: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return sorted(out)


def bridge_text(slot: int) -> str:
    chart = f"Chart{slot:03d}Cone"
    bridge = f"Chart{slot:03d}Bridge"
    witness = f"chart{slot:03d}Witness"
    return f"""import Erdos23Delta0.O14.Generated.ChartPayloads.{chart}

/-!
# Chart {slot:03d} bridge

This generated bridge connects the accepted `{chart}` witness factory to the
ODL core goal.  It does not claim structural chart coverage: callers still
provide the instance-specific semantic equalities and nonnegativity facts.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated
namespace ChartPayloads
namespace {bridge}

open ODLFull
open PolyCert

/-- The generated Chart {slot:03d} chunked cone witness proves the corresponding
ODL core goal once the structural/core binding layer supplies its semantic
inputs. -/
theorem coreODLGoal_of_chart{slot:03d}Cone
    {{G : CertGraph.GraphData}} {{c : CertGraph.CutData}}
    {{rows : CertGraph.RowDB}} {{Q : CertGraph.RowCert}}
    (core : ODLCoreData G c rows Q) (env : Var → ℚ)
    (hvars : ∀ v, 0 ≤ env v)
    (hslacks :
      ∀ s ∈ {chart}.Main.slacks, 0 ≤ NF.eval env s)
    (hcombo :
      NF.eval env (({chart}.Main.pairs.map Prod.snd).flatten) =
        NF.eval env
          (comboNF {chart}.Main.base {chart}.Main.mults
            {chart}.Main.slacks))
    (htarget :
      NF.eval env (({chart}.Main.pairs.map Prod.fst).flatten) =
        coreDefect core) :
    CoreODLGoal G c rows Q core := by
  exact
    ({chart}.Main.{witness} core env hvars hslacks hcombo
      htarget).sound

end {bridge}
end ChartPayloads
end Generated
end O14
end Erdos23Delta0
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", default="1-107")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for slot in parse_slots(args.slots):
        path = args.out_dir / f"Chart{slot:03d}Bridge.lean"
        text = bridge_text(slot)
        if path.exists() and not args.force and path.read_text(encoding="utf-8") == text:
            skipped += 1
            continue
        path.write_text(text, encoding="utf-8", newline="\n")
        written += 1
    print(f"written={written} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
