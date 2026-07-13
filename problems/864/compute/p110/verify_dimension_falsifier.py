import argparse
import hashlib
import json
from pathlib import Path


def verify(record):
    B = tuple(record["B"])
    h = record["h"]
    p = len(B)
    assert len(set(B)) == p
    assert tuple(sorted(B)) == B
    assert B[0] == 0 and B[-1] == h - 1
    encoded = ",".join(map(str, B)).encode("ascii")
    assert hashlib.sha256(encoded).hexdigest() == record["sha256"]

    sums = {}
    for i, a in enumerate(B):
        for c in B[i:]:
            assert a + c not in sums
            sums[a + c] = (a, c)
    differences = set()
    for i, left in enumerate(B):
        for right in B[i + 1 :]:
            difference = right - left
            assert difference not in differences
            differences.add(difference)
    assert len(sums) == p * (p + 1) // 2
    assert len(differences) == p * (p - 1) // 2

    folds = []
    for low, (a, c) in sorted(sums.items()):
        if low + h not in sums:
            continue
        u, v = sums[low + h]
        assert a <= c < u <= v
        folds.append((a, c, u, v))
    ac = {(a, c): index for index, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): index for index, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): index for index, (_a, c, u, _v) in enumerate(folds)}
    triangles = []
    for a, c in ac:
        for u in B:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            assert len(set(ids)) == 3
            triangles.append(ids)

    labels = [a + c + 1 for a, c, _u, _v in folds]
    classes = [0, 0, 0]
    multiplicity = {}
    for ids in triangles:
        assert len({labels[index] for index in ids}) == 3
        role = min(range(3), key=lambda position: labels[ids[position]])
        classes[role] += 1
        key = (role, ids[role])
        multiplicity[key] = multiplicity.get(key, 0) + 1

    dimension = len(folds) + 4 * p
    assert p == record["p"]
    assert len(folds) == record["C_S"]
    assert len(triangles) == record["T_F"]
    assert dimension == record["weighted_ambient_dimension"]
    assert len(triangles) - dimension == record["dimension_excess"] > 0
    delta = (3 * p * p - p + 2) // 2 - h
    collision_counts = [
        sum(a + c + b in differences for a, c, _u, _v in folds)
        for b in (1, 2)
    ]
    return {
        "sha256": record["sha256"],
        "p": p,
        "h": h,
        "delta": delta,
        "C_S": len(folds),
        "T_F": len(triangles),
        "ambient_dimension": dimension,
        "dimension_excess": len(triangles) - dimension,
        "minimum_classes": classes,
        "maximum_same_base": max(multiplicity.values()),
        "V_1": collision_counts[0],
        "V_2": collision_counts[1],
    }


def verify_q2_lift(record):
    source = tuple(record["B"])
    B = tuple(2 * value + 1 for value in source)
    h = 2 * record["h"]
    p = len(B)
    assert B[-1] == h - 1
    sums = {}
    for i, a in enumerate(B):
        for c in B[i:]:
            assert a + c not in sums
            sums[a + c] = (a, c)
    differences = set()
    for i, left in enumerate(B):
        for right in B[i + 1 :]:
            difference = right - left
            assert difference not in differences
            differences.add(difference)
    folds = []
    for low, (a, c) in sorted(sums.items()):
        if low + h in sums:
            u, v = sums[low + h]
            assert a <= c < u <= v
            folds.append((a, c, u, v))
    ac = {(a, c): index for index, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): index for index, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): index for index, (_a, c, u, _v) in enumerate(folds)}
    triangles = 0
    for a, c in ac:
        for u in B:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            assert len(set(ids)) == 3
            triangles += 1
    assert len(folds) == record["C_S"]
    assert triangles == record["T_F"]
    assert all(a + c + 1 not in differences for a, c, _u, _v in folds)
    dimension = len(folds) + 4 * p
    assert triangles > dimension
    return {
        "p": p,
        "h": h,
        "delta": (3 * p * p - p + 2) // 2 - h,
        "C_S": len(folds),
        "T_F": triangles,
        "ambient_dimension": dimension,
        "dimension_excess": triangles - dimension,
        "V_1": 0,
        "literal_hole_b1": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="ascii"))
    result = {
        "schema_version": 1,
        "arithmetic": "independent exact Python integers",
        "smallest_failure": verify(payload["smallest_failure"]),
        "strongest_failure": verify(payload["strongest_failure"]),
        "smallest_q2_literal_hole_lift": verify_q2_lift(payload["smallest_failure"]),
        "strongest_q2_literal_hole_lift": verify_q2_lift(payload["strongest_failure"]),
        "status": "PASS",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
