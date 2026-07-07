#!/usr/bin/env python3
"""Verify the A1 proper-mask rotation table.

The a1Proper branch reduces the 30 nonempty proper masks of Z/5 to six
canonical masks.  This checker is deliberately small and exact: it verifies
that every table row is present once, that the canonical labels match the
authoritative v2 codes, and that applying the recorded rotation sends the mask
to its canonical representative.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "a1_mask_symmetry_v2_MAIN_authoritative"
CANONICAL_CODES = {
    "M0": 1,
    "M1": 3,
    "M2": 5,
    "M3": 7,
    "M4": 11,
    "M5": 15,
}


def mask_from_code(code: int) -> list[int]:
    return [i for i in range(5) if (code >> i) & 1]


def code_from_mask(mask: list[int]) -> int:
    out = 0
    for i in mask:
        if i < 0 or i >= 5:
            raise ValueError(f"mask index out of range: {i}")
        out |= 1 << i
    return out


def rotate_mask(mask: list[int], rot: int) -> list[int]:
    return sorted((i + rot) % 5 for i in mask)


def run(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != EXPECTED_SCHEMA:
        raise AssertionError(f"unexpected schema: {data.get('schema')!r}")
    if data.get("n_orbits") != 6:
        raise AssertionError(f"unexpected n_orbits: {data.get('n_orbits')!r}")
    if data.get("canonical_codes") != CANONICAL_CODES:
        raise AssertionError("canonical code map is not the v2 authoritative map")

    rows = data.get("table")
    if not isinstance(rows, list):
        raise AssertionError("table is not a list")
    if len(rows) != 30:
        raise AssertionError(f"expected 30 rows, got {len(rows)}")

    expected_codes = set(range(1, 31))
    seen_codes: set[int] = set()
    orbit_counts = {key: 0 for key in CANONICAL_CODES}
    errors: list[str] = []

    for rec in rows:
        code = int(rec["code"])
        mask = [int(x) for x in rec["mask"]]
        ident = str(rec["id"])
        rot = int(rec["rot"])
        seen_codes.add(code)

        if code_from_mask(mask) != code:
            errors.append(f"code {code}: mask encodes as {code_from_mask(mask)}")
        if mask_from_code(code) != sorted(mask):
            errors.append(f"code {code}: mask is not sorted code mask")
        if ident not in CANONICAL_CODES:
            errors.append(f"code {code}: unknown id {ident}")
            continue
        if not 0 <= rot < 5:
            errors.append(f"code {code}: rotation out of range {rot}")
            continue

        canonical_mask = mask_from_code(CANONICAL_CODES[ident])
        rotated = rotate_mask(mask, rot)
        if rotated != canonical_mask:
            errors.append(
                f"code {code}: rot^{rot}({mask})={rotated}, expected {canonical_mask}"
            )
        orbit_counts[ident] += 1

    missing = sorted(expected_codes - seen_codes)
    extra = sorted(seen_codes - expected_codes)
    if missing:
        errors.append(f"missing codes: {missing}")
    if extra:
        errors.append(f"extra codes: {extra}")
    for ident, count in orbit_counts.items():
        if count != 5:
            errors.append(f"orbit {ident}: expected 5 rows, got {count}")

    if errors:
        raise AssertionError("; ".join(errors))

    return {
        "schema": "a1_mask_symmetry_verify_v1",
        "table": str(path),
        "table_schema": data.get("schema"),
        "rows": len(rows),
        "canonical_codes": CANONICAL_CODES,
        "orbit_counts": orbit_counts,
        "exact_ok": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--table",
        type=Path,
        default=Path("problems/23/writeup/a1_mask_symmetry_table.json"),
    )
    ap.add_argument("--summary", type=Path, default=Path("tmp/a1_mask_symmetry_verify_v1.json"))
    args = ap.parse_args()
    out = run(args.table)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"exact_ok": True, "rows": out["rows"], "summary": str(args.summary)}, sort_keys=True))


if __name__ == "__main__":
    main()
