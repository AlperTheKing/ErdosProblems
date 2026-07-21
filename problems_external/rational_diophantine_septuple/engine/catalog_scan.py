"""Scan Rathbun's finite sextuple catalogue for septuple-compatible seeds.

For every exact rational triple contained in a catalogued sextuple, collect
all other entries seen with that triple.  Two collected extensions are joined
when their product plus one is a rational square.  A 4-clique, together with
the fixed triple, is exactly a rational Diophantine septuple certificate.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
from collections import defaultdict
from fractions import Fraction
from math import isqrt
from pathlib import Path


RECORD_RE = re.compile(r"^\((\d+)\)\s+\[([^\]]+)\]\s*(.*)$")
TORSION_RE = re.compile(r"(Z[46]x2)<<([a-f]),([a-f]),([a-f])>>")
LETTERS = "abcdef"


def parse_fraction(text: str) -> Fraction:
    return Fraction(text.strip())


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def rational_square_root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    nr = isqrt(value.numerator)
    dr = isqrt(value.denominator)
    if nr * nr != value.numerator or dr * dr != value.denominator:
        return None
    return Fraction(nr, dr)


def is_compatible(left: Fraction, right: Fraction) -> bool:
    return rational_square_root(left * right + 1) is not None


def parse_catalog(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = RECORD_RE.match(line)
        if match is None:
            continue
        index = int(match.group(1))
        values = tuple(parse_fraction(part) for part in match.group(2).split(","))
        if len(values) != 6:
            raise ValueError(f"record {index} has {len(values)} entries")
        annotation = match.group(3)
        torsion: list[tuple[str, tuple[Fraction, Fraction, Fraction]]] = []
        for tag, l1, l2, l3 in TORSION_RE.findall(annotation):
            triple = tuple(sorted(values[LETTERS.index(letter)] for letter in (l1, l2, l3)))
            torsion.append((tag, triple))
        records.append(
            {"index": index, "values": values, "annotation": annotation, "torsion": torsion}
        )
    return records


def maximum_clique(vertices: set[Fraction]) -> tuple[Fraction, ...]:
    ordered = sorted(vertices)
    neighbors = {
        v: {w for w in ordered if w != v and is_compatible(v, w)} for v in ordered
    }
    best: tuple[Fraction, ...] = ()

    def bronk(r: tuple[Fraction, ...], p: set[Fraction], x: set[Fraction]) -> None:
        nonlocal best
        if len(r) + len(p) <= len(best):
            return
        if not p and not x:
            if len(r) > len(best):
                best = r
            return
        pivot_candidates = p | x
        pivot = max(pivot_candidates, key=lambda v: len(p & neighbors[v]), default=None)
        candidates = p - (neighbors[pivot] if pivot is not None else set())
        for vertex in sorted(candidates):
            bronk(r + (vertex,), p & neighbors[vertex], x & neighbors[vertex])
            p.remove(vertex)
            x.add(vertex)

    bronk((), set(ordered), set())
    return tuple(sorted(best))


def validate_sextuple(index: int, values: tuple[Fraction, ...]) -> None:
    if any(value == 0 for value in values) or len(set(values)) != 6:
        raise ValueError(f"record {index} is zero or non-distinct")
    for left, right in itertools.combinations(values, 2):
        if not is_compatible(left, right):
            raise ValueError(f"record {index} fails pair {left}, {right}")


def scan(records: list[dict[str, object]]) -> dict[str, object]:
    extension_sets: dict[tuple[Fraction, ...], set[Fraction]] = defaultdict(set)
    record_ids: dict[tuple[Fraction, ...], set[int]] = defaultdict(set)
    torsion_tags: dict[tuple[Fraction, ...], set[str]] = defaultdict(set)

    for record in records:
        index = int(record["index"])
        values = tuple(record["values"])  # type: ignore[arg-type]
        validate_sextuple(index, values)
        for positions in itertools.combinations(range(6), 3):
            triple = tuple(sorted(values[position] for position in positions))
            extension_sets[triple].update(value for value in values if value not in triple)
            record_ids[triple].add(index)
        for tag, triple in record["torsion"]:  # type: ignore[union-attr]
            torsion_tags[triple].add(tag)

    rows: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []
    for triple, vertices in extension_sets.items():
        # This also independently checks that catalog aggregation did not add
        # a value which fails to extend the fixed triple.
        for base in triple:
            for extension in vertices:
                if not is_compatible(base, extension):
                    raise ArithmeticError(f"aggregation failure for {triple} and {extension}")
        clique = maximum_clique(vertices)
        row = {
            "triple": [fraction_text(value) for value in triple],
            "extension_count": len(vertices),
            "maximum_clique_size": len(clique),
            "maximum_clique": [fraction_text(value) for value in clique],
            "catalog_records": sorted(record_ids[triple]),
            "torsion_tags": sorted(torsion_tags[triple]),
        }
        rows.append(row)
        if len(clique) >= 4:
            candidate = tuple(triple) + clique[:4]
            validate_sextuple(-1, candidate)
            hits.append(row)

    rows.sort(
        key=lambda row: (
            int(row["maximum_clique_size"]),
            int(row["extension_count"]),
            len(row["catalog_records"]),
        ),
        reverse=True,
    )
    multiplicities: dict[str, int] = defaultdict(int)
    clique_histogram: dict[str, int] = defaultdict(int)
    for row in rows:
        multiplicities[str(row["extension_count"])] += 1
        clique_histogram[str(row["maximum_clique_size"])] += 1

    return {
        "status": "HIT" if hits else "NO_HIT",
        "catalog_sextuples": len(records),
        "induced_triples": len(rows),
        "extension_count_histogram": dict(sorted(multiplicities.items(), key=lambda p: int(p[0]))),
        "maximum_clique_histogram": dict(sorted(clique_histogram.items(), key=lambda p: int(p[0]))),
        "hit_count": len(hits),
        "hits": hits,
        "top_seeds": rows[:100],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expect", type=int, default=2001)
    args = parser.parse_args()

    records = parse_catalog(args.catalog)
    if len(records) != args.expect:
        raise SystemExit(f"expected {args.expect} records, parsed {len(records)}")
    result = scan(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "catalog_sextuples", "induced_triples", "hit_count")}))
    return 0 if result["status"] in {"HIT", "NO_HIT"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
