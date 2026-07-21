"""Independent standard-library oracle for unrestricted SSNC local search.

This module is intentionally scalar and recomputes every set from raw
adjacency rows.  It shares no incremental scoring or mutation logic with a
future C++ engine.

Canonical candidate schema::

    {
      "schema": "ssnc-oriented-graph-v1",
      "n": 19,
      "out_neighbors": [[...], ..., [...]]
    }

Rows must be strictly increasing.  Missing unordered pairs are represented by
absence in both directions.  Loops, duplicates, digons, non-integers, and
out-of-range endpoints are rejected.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable, Sequence


CANDIDATE_SCHEMA = "ssnc-oriented-graph-v1"
LEDGER_SCHEMA = "ssnc-scalar-oracle-ledger-v1"


class CandidateError(ValueError):
    """Raised when raw candidate syntax or oriented-graph structure is bad."""


def _is_plain_int(value: object) -> bool:
    return type(value) is int


def normalize_rows(
    rows: Sequence[Iterable[int]],
    *,
    expected_n: int | None = None,
    require_canonical_order: bool = False,
) -> tuple[tuple[int, ...], ...]:
    """Validate and freeze adjacency rows.

    Structural validation is independent of any minimum-outdegree domain
    restriction.  Both directions absent is legal; both directions present is
    a rejected digon.
    """

    if not isinstance(rows, (list, tuple)):
        raise CandidateError("out_neighbors must be a list of rows")
    n = len(rows)
    if expected_n is not None and n != expected_n:
        raise CandidateError(f"expected {expected_n} rows, found {n}")
    if n <= 0:
        raise CandidateError("n must be positive")

    frozen: list[tuple[int, ...]] = []
    for v, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            raise CandidateError(f"row {v} must be a list")
        values = list(row)
        for endpoint in values:
            if not _is_plain_int(endpoint):
                raise CandidateError(f"row {v} contains a non-integer endpoint")
            if endpoint < 0 or endpoint >= n:
                raise CandidateError(f"row {v} endpoint {endpoint} is out of range")
            if endpoint == v:
                raise CandidateError(f"row {v} contains a loop")
        if len(set(values)) != len(values):
            raise CandidateError(f"row {v} contains a duplicate endpoint")
        if require_canonical_order and values != sorted(values):
            raise CandidateError(f"row {v} is not strictly increasing")
        frozen.append(tuple(sorted(values)))

    row_sets = [set(row) for row in frozen]
    for v in range(n):
        for w in row_sets[v]:
            if v in row_sets[w]:
                raise CandidateError(f"digon on pair {min(v,w)},{max(v,w)}")
    return tuple(frozen)


def parse_candidate_object(
    value: object, *, expected_n: int | None = None
) -> tuple[tuple[int, ...], ...]:
    if not isinstance(value, dict):
        raise CandidateError("candidate root must be an object")
    required = {"schema", "n", "out_neighbors"}
    if set(value) != required:
        raise CandidateError("candidate keys must be exactly schema,n,out_neighbors")
    if value["schema"] != CANDIDATE_SCHEMA:
        raise CandidateError("unsupported candidate schema")
    if not _is_plain_int(value["n"]) or value["n"] <= 0:
        raise CandidateError("n must be a positive integer")
    if expected_n is not None and value["n"] != expected_n:
        raise CandidateError(f"expected n={expected_n}, found {value['n']}")
    rows = value["out_neighbors"]
    if not isinstance(rows, list) or len(rows) != value["n"]:
        raise CandidateError("out_neighbors length does not equal n")
    return normalize_rows(
        rows,
        expected_n=value["n"],
        require_canonical_order=True,
    )


def parse_candidate_bytes(
    payload: bytes, *, expected_n: int | None = None
) -> tuple[tuple[int, ...], ...]:
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise CandidateError("candidate is not strict UTF-8") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CandidateError("candidate is not one complete JSON value") from exc
    return parse_candidate_object(value, expected_n=expected_n)


def candidate_object(rows: Sequence[Iterable[int]]) -> dict[str, object]:
    frozen = normalize_rows(rows)
    return {
        "schema": CANDIDATE_SCHEMA,
        "n": len(frozen),
        "out_neighbors": [list(row) for row in frozen],
    }


def candidate_bytes(rows: Sequence[Iterable[int]]) -> bytes:
    value = candidate_object(rows)
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def candidate_sha256(rows: Sequence[Iterable[int]]) -> str:
    return sha256(candidate_bytes(rows)).hexdigest().upper()


def analyze(
    rows: Sequence[Iterable[int]], *, min_outdegree: int = 0
) -> dict[str, object]:
    """Recompute the complete scalar ledger and exact objective.

    For each vertex ``v``:

    * ``N+`` is the raw adjacency row;
    * ``raw_length2`` contains every endpoint of a literal two-arc walk;
    * ``new_N2+ = raw_length2 \\ (N+ union {v})``;
    * ``row_penalty = max(0, |new_N2+|-|N+|+1)``.

    ``strict_objective`` is the sum of row penalties.  The domain deficit is
    the sum of ``max(0,min_outdegree-|N+(v)|)``.  The exact black-box score is

        objective = strict_objective + domain_deficit.

    On structurally valid oriented graphs it is zero exactly when the graph is
    inside the requested degree domain and every row satisfies the literal
    strict SSNC negation.
    """

    if not _is_plain_int(min_outdegree) or min_outdegree < 0:
        raise ValueError("min_outdegree must be a nonnegative integer")
    frozen = normalize_rows(rows)
    n = len(frozen)
    out_sets = [set(row) for row in frozen]
    ledger: list[dict[str, object]] = []
    strict_objective = 0
    domain_deficit = 0

    for v in range(n):
        out = out_sets[v]
        raw_length2: set[int] = set()
        for middle in out:
            raw_length2.update(out_sets[middle])
        new_second = raw_length2.difference(out)
        new_second.discard(v)
        unreachable = set(range(n)).difference({v}, out, new_second)
        overlap = out.intersection(raw_length2)

        out_degree = len(out)
        second_degree = len(new_second)
        row_penalty = max(0, second_degree - out_degree + 1)
        degree_deficit = max(0, min_outdegree - out_degree)
        strict_objective += row_penalty
        domain_deficit += degree_deficit

        assert ({v} | out | new_second | unreachable) == set(range(n))
        assert not ({v} & out)
        assert not (out & new_second)
        assert not (out & unreachable)
        assert not (new_second & unreachable)

        ledger.append(
            {
                "vertex": v,
                "N+": sorted(out),
                "raw_length2": sorted(raw_length2),
                "direct_raw2_overlap": sorted(overlap),
                "new_N2+": sorted(new_second),
                "unreachable": sorted(unreachable),
                "out_degree": out_degree,
                "new_second_degree": second_degree,
                "strict": second_degree < out_degree,
                "row_penalty": row_penalty,
                "degree_deficit": degree_deficit,
            }
        )

    objective = strict_objective + domain_deficit
    actual_min = min(len(row) for row in frozen)
    strict_all = strict_objective == 0
    domain_valid = domain_deficit == 0
    return {
        "schema": LEDGER_SCHEMA,
        "n": n,
        "candidate_sha256": candidate_sha256(frozen),
        "min_outdegree_required": min_outdegree,
        "min_outdegree_actual": actual_min,
        "domain_valid": domain_valid,
        "strict_all": strict_all,
        "strict_objective": strict_objective,
        "domain_deficit": domain_deficit,
        "objective": objective,
        "score_zero": objective == 0,
        "ledger": ledger,
    }


def pair_state(rows: Sequence[Iterable[int]], a: int, b: int) -> int:
    """Return 0=missing, 1=a->b, 2=b->a for an unordered pair a<b."""
    frozen = normalize_rows(rows)
    if not (0 <= a < b < len(frozen)):
        raise ValueError("pair must satisfy 0 <= a < b < n")
    if b in frozen[a]:
        return 1
    if a in frozen[b]:
        return 2
    return 0


def set_pair_state(
    rows: Sequence[Iterable[int]], a: int, b: int, state: int
) -> tuple[tuple[int, ...], ...]:
    """Pure mutation helper used only by adversarial tests."""
    frozen = normalize_rows(rows)
    if not (0 <= a < b < len(frozen)):
        raise ValueError("pair must satisfy 0 <= a < b < n")
    if state not in (0, 1, 2):
        raise ValueError("state must be 0, 1, or 2")
    mutable = [set(row) for row in frozen]
    mutable[a].discard(b)
    mutable[b].discard(a)
    if state == 1:
        mutable[a].add(b)
    elif state == 2:
        mutable[b].add(a)
    return normalize_rows([sorted(row) for row in mutable])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--expected-n", type=int, default=19)
    parser.add_argument("--min-outdegree", type=int, default=8)
    args = parser.parse_args()
    try:
        rows = parse_candidate_bytes(
            args.candidate.read_bytes(), expected_n=args.expected_n
        )
        result = analyze(rows, min_outdegree=args.min_outdegree)
    except (OSError, CandidateError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

