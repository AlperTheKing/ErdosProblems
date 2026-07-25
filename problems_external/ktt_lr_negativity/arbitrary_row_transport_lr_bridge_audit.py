#!/usr/bin/env python3
"""Zero-trust structural and exact-count audit of the V7 LR bridge."""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
LR_ENGINE = HERE / "engine" / "lr_hive.exe"
EXPECTED_PAYLOAD_SHA256 = (
    "510aafb6878dd2db0f77ee04895a4eae4c4b9e3bdc360ce5df1bdd203d4fa443"
)
REPLAY_CASES = (
    ((1, 1, 1), 2, 1, 6),
    ((1, 1, 1), 2, 2, 21),
    ((1, 1, 2), 3, 1, 12),
    ((1, 1, 2), 3, 2, 72),
    ((1, 2, 3), 5, 1, 60),
    ((1, 2, 3), 5, 2, 1185),
)


def normalize(partition: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(part for part in partition if part != 0)


def is_partition(partition: tuple[int, ...]) -> bool:
    return all(partition[index] >= partition[index + 1]
               for index in range(len(partition) - 1)) and all(
                   part > 0 for part in partition
               )


def construct(
    rows: tuple[int, int, int], k: int
) -> dict[str, tuple[int, ...]]:
    r1, r2, r3 = rows
    total = sum(rows)
    assert min(rows) > 0 and 1 <= k < total
    A = (total, r2 + r3, r3)
    B = (r2 + r3, r3)
    weight = (total - k,) + (1,) * k
    staircase = tuple(range(k, 0, -1))
    R = (total + r2 + r3, total + r3, total) + staircase
    S = (total, total) + staircase
    return {"A": A, "B": B, "w": weight, "R": R, "S": S}


def general_skew_kostka_bridge(
    lam: tuple[int, ...],
    beta: tuple[int, ...],
    weight: tuple[int, ...],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    width = sum(weight)
    tails = tuple(sum(weight[index:]) for index in range(len(weight)))
    R = tuple(width + part for part in beta) + tails
    S = (width,) * len(beta) + tails[1:]
    return normalize(R), normalize(S)


def scale(partition: tuple[int, ...], n: int) -> tuple[int, ...]:
    return normalize(tuple(n * part for part in partition))


def transportation_count(rows: tuple[int, int, int], k: int, n: int) -> int:
    kernel = [(x, y) for x in range(n + 1) for y in range(n - x + 1)]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(k):
        updated: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (a, b), multiplicity in states.items():
            for x, y in kernel:
                updated[(a + x, b + y)] += multiplicity
        states = dict(updated)
    caps = tuple(n * row for row in rows)
    return sum(
        multiplicity
        for (a, b), multiplicity in states.items()
        if a <= caps[0]
        and b <= caps[1]
        and k * n - a - b <= caps[2]
    )


def lr_count(
    left: tuple[int, ...], right: tuple[int, ...], outer: tuple[int, ...]
) -> int:
    command = [
        str(LR_ENGINE),
        ",".join(map(str, left)),
        ",".join(map(str, right)),
        ",".join(map(str, outer)),
    ]
    completed = subprocess.run(
        command, capture_output=True, text=True, check=True, timeout=120
    )
    return int(completed.stdout.strip())


def main() -> None:
    structural_checks = 0
    homogeneity_checks = 0

    # A bounded structural calibration; the proof in the audit is symbolic.
    for r1 in range(1, 6):
        for r2 in range(1, 6):
            for r3 in range(1, 6):
                rows = (r1, r2, r3)
                total = sum(rows)
                for k in range(1, total):
                    data = construct(rows, k)
                    assert all(is_partition(data[name]) for name in data)
                    assert sum(data["A"]) - sum(data["B"]) == total
                    assert sum(data["w"]) == total
                    assert sum(data["R"]) == sum(data["A"]) + sum(data["S"])
                    assert general_skew_kostka_bridge(
                        data["A"], data["B"], data["w"]
                    ) == (data["R"], data["S"])

                    # The three A/B row intervals are adjacent and disjoint.
                    intervals = (
                        set(range(r2 + r3 + 1, total + 1)),
                        set(range(r3 + 1, r2 + r3 + 1)),
                        set(range(1, r3 + 1)),
                    )
                    assert tuple(map(len, intervals)) == rows
                    assert not (intervals[0] & intervals[1])
                    assert not (intervals[0] & intervals[2])
                    assert not (intervals[1] & intervals[2])
                    structural_checks += 1

                    for n in range(5):
                        # At n=0 every partition/content normalizes to empty;
                        # both the empty tableau and c^0_(0,0) count as one.
                        scaled = {
                            name: scale(partition, n)
                            for name, partition in data.items()
                        }
                        assert scaled["R"] == scale(data["R"], n)
                        assert scaled["S"] == scale(data["S"], n)
                        if n == 0:
                            assert all(partition == () for partition in scaled.values())
                            assert transportation_count(rows, k, 0) == 1
                        homogeneity_checks += 1

    replay_records: list[dict[str, object]] = []
    for rows, k, n, expected in REPLAY_CASES:
        data = construct(rows, k)
        table_value = transportation_count(rows, k, n)
        lr_value = lr_count(
            scale(data["A"], n),
            scale(data["S"], n),
            scale(data["R"], n),
        )
        assert table_value == lr_value == expected
        replay_records.append(
            {
                "rows": list(rows),
                "k": k,
                "n": n,
                "A": list(scale(data["A"], n)),
                "S": list(scale(data["S"], n)),
                "R": list(scale(data["R"], n)),
                "count": expected,
            }
        )

    payload = {
        "structural_checks": structural_checks,
        "homogeneity_checks_n0_to_n4": homogeneity_checks,
        "n0_convention": "empty tableau = c^0_(0,0) = 1",
        "lr_engine_replays": replay_records,
        "identity": "L(n)=K_(nA/nB,nw)=c^(nR)_(nA,nS)",
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    digest = sha256(encoded).hexdigest()
    if EXPECTED_PAYLOAD_SHA256:
        assert digest == EXPECTED_PAYLOAD_SHA256

    print("PASS")
    print(f"structural_checks={structural_checks}")
    print(f"homogeneity_checks_n0_to_n4={homogeneity_checks}")
    print(f"lr_engine_replays={len(replay_records)}")
    for record in replay_records:
        print(
            f"rows={tuple(record['rows'])} k={record['k']} n={record['n']} "
            f"count={record['count']}"
        )
    print(f"payload_sha256={digest}")


if __name__ == "__main__":
    main()
