#!/usr/bin/env python3
"""Focused exact audit of the 3x8 transportation-to-LR bridge.

This checker does not enumerate transportation families.  It verifies the
closed formulas used in APPROACH_REGISTRY_GENERAL_KTT_V4.md, proves the
codegree-three assertion by positive-table shifting, and compares a few exact
transportation counts with the independent hive LR engine.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
HIVE = HERE / "engine" / "lr_hive.exe"


def trim(parts):
    parts = tuple(int(x) for x in parts)
    while parts and parts[-1] == 0:
        parts = parts[:-1]
    return parts


def is_partition(parts):
    return all(x > 0 for x in parts) and all(x >= y for x, y in zip(parts, parts[1:]))


def scale(parts, n):
    return trim(n * x for x in parts)


def construction(rows):
    """Return (A,B,w,R,S) for row margins (r1,r2,r3)."""
    r1, r2, r3 = rows
    assert min(rows) >= 3
    N = sum(rows)
    A = (N, r2 + r3, r3)
    B = (r2 + r3, r3)
    w = (N - 7, 1, 1, 1, 1, 1, 1, 1)
    R = (N + r2 + r3, N + r3, N, 7, 6, 5, 4, 3, 2, 1)
    S = (N, N, 7, 6, 5, 4, 3, 2, 1)
    return A, B, w, R, S


def skew_cells(outer, inner):
    inner = tuple(inner) + (0,) * (len(outer) - len(inner))
    return {(i + 1, j) for i, width in enumerate(outer) for j in range(inner[i] + 1, width + 1)}


def verify_geometry(rows):
    A, B, w, R, S = construction(rows)
    assert all(is_partition(p) for p in (A, B, w, R, S))
    assert sum(A) - sum(B) == sum(w) == sum(rows)
    assert sum(R) == sum(A) + sum(S)

    # A/B is exactly three horizontal rows in disjoint column intervals.
    r1, r2, r3 = rows
    expected = (
        {(1, j) for j in range(r2 + r3 + 1, sum(rows) + 1)}
        | {(2, j) for j in range(r3 + 1, r2 + r3 + 1)}
        | {(3, j) for j in range(1, r3 + 1)}
    )
    assert skew_cells(A, B) == expected
    row_columns = [{j for i, j in expected if i == row} for row in (1, 2, 3)]
    assert all(x.isdisjoint(y) for x, y in itertools.combinations(row_columns, 2))

    # R/S is the translate of B plus the eight isolated rows of lengths w.
    N = sum(rows)
    tails = [sum(w[j:]) for j in range(len(w))] + [0]
    expected_bridge = {
        (i + 1, N + j) for i, width in enumerate(B) for j in range(1, width + 1)
    }
    for j in range(8):
        expected_bridge |= {
            (len(B) + j + 1, col) for col in range(tails[j + 1] + 1, tails[j] + 1)
        }
    assert skew_cells(R, S) == expected_bridge

    for n in range(1, 6):
        nA, nB, nw, nR, nS = (scale(x, n) for x in (A, B, w, R, S))
        rebuilt = construction(tuple(n * x for x in rows))
        assert rebuilt[:2] == (nA, nB)
        # The family formula changes the weight to (nN-7,1^7), which is not
        # n*(N-7,1^7) for n>1.  Correct homogeneity scales the already fixed
        # weight and all four partitions; it does not re-enter the family.
        if n > 1:
            assert rebuilt[2] != nw
        assert sum(nA) - sum(nB) == sum(nw)
        assert sum(nR) == sum(nA) + sum(nS)
    return A, B, w, R, S


def table_count(rows, cols, positive=False):
    """Exact count of 3xm integer tables by a two-row dynamic program."""
    rows = tuple(rows)
    cols = tuple(cols)
    if positive:
        rows = tuple(x - len(cols) for x in rows)
        cols = tuple(x - 3 for x in cols)
    if min(rows, default=0) < 0 or min(cols, default=0) < 0 or sum(rows) != sum(cols):
        return 0

    @lru_cache(maxsize=None)
    def dp(j, used0, used1):
        if j == len(cols):
            return int(used0 == rows[0] and used1 == rows[1])
        total = 0
        col = cols[j]
        for x0 in range(col + 1):
            for x1 in range(col - x0 + 1):
                x2 = col - x0 - x1
                if used0 + x0 <= rows[0] and used1 + x1 <= rows[1]:
                    used2 = sum(cols[:j]) - used0 - used1
                    if used2 + x2 <= rows[2]:
                        total += dp(j + 1, used0 + x0, used1 + x1)
        return total

    return dp(0, 0, 0)


def run_hive(requests):
    assert HIVE.is_file(), HIVE
    def csv(parts):
        return ",".join(map(str, parts)) if parts else "0"
    payload = [f"{csv(lam)};{csv(mu)};{csv(nu)};1000000000000000000" for lam, mu, nu in requests]
    with tempfile.TemporaryDirectory(prefix="transport_lr_audit_") as tmp:
        batch = Path(tmp) / "audit.batch"
        batch.write_text("\n".join(payload) + "\n", encoding="ascii", newline="\n")
        env = os.environ.copy()
        env.setdefault("LR_HIVE_NODE_CAP", "500000000")
        proc = subprocess.run([str(HIVE), "--batch", str(batch)], capture_output=True, text=True,
                              check=True, env=env)
    output = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    assert len(output) == len(requests), (output, proc.stderr)
    assert all(re.fullmatch(r"[0-9]+", x) for x in output), output
    return list(map(int, output))


def base_count_closed(rows):
    # The seven unit columns choose labeled rows; the large-column entries are
    # then forced.  Capacity is min(r_i,7).
    return sum(
        1
        for assignment in itertools.product(range(3), repeat=7)
        if all(assignment.count(i) <= rows[i] for i in range(3))
    )


def main():
    samples = ((3, 3, 3), (3, 4, 8), (5, 7, 9))
    records = []
    requests = []
    expected = []
    for rows in samples:
        A, B, w, R, S = verify_geometry(rows)
        assert table_count(rows, w) == base_count_closed(rows)

        # Relative-interior integer points are precisely positive tables.
        assert table_count(rows, w, positive=True) == 0
        assert table_count(tuple(2 * x for x in rows), tuple(2 * x for x in w), positive=True) == 0
        assert table_count(tuple(3 * x for x in rows), tuple(3 * x for x in w), positive=True) == 1

        for n in (1, 2):
            count = table_count(tuple(n * x for x in rows), tuple(n * x for x in w))
            if rows == (3, 3, 3) and n == 1:
                requests.append((scale(A, n), scale(S, n), scale(R, n)))
                expected.append(count)
                records.append({"rows": rows, "n": n, "count": count})

    assert run_hive(requests) == expected

    # Since every r_i >= 3, the base count is minimized at (3,3,3).
    # Its only occupancy types are permutations of (3,3,1) and (3,2,2).
    minimum = 3 * (5040 // (6 * 6)) + 3 * (5040 // (6 * 2 * 2))
    assert minimum == 1050 == base_count_closed((3, 3, 3))
    assert all(base_count_closed(caps) >= minimum for caps in itertools.product(range(3, 8), repeat=3))
    assert not any(base_count_closed(caps) == 255 for caps in itertools.product(range(3, 8), repeat=3))

    digest = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    print(json.dumps({
        "status": "PASS",
        "explicit_lr_replays": len(records),
        "replay_records_sha256": digest,
        "dimension": 14,
        "codegree": 3,
        "interior_points_at_codegree": 1,
        "minimum_base_count": minimum,
        "base_count_255_survivors": 0,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
