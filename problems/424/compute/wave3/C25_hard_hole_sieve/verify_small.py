import argparse
import json
import math
from fractions import Fraction
from pathlib import Path


NONE, E, O0, O2, S, H0, H2 = range(7)
D2 = (5, 17, 41, 53, 77)
D0 = (33, 69)
PRIORITY = (5, 17, 33, 41, 53, 69, 77)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def divisors_from_spf(n: int, spf: list[int]) -> list[int]:
    divisors = [1]
    while n > 1:
        p = spf[n]
        old = tuple(divisors)
        power = 1
        while n > 1 and spf[n] == p:
            n //= p
            power *= p
            divisors.extend(d * power for d in old)
    return divisors


def make_audit() -> dict[str, int]:
    return {
        "source_events": 0,
        "failure_events": 0,
        "first_failure": 0,
        "source_at_first_failure": 0,
        "capacity_at_first_failure": 0,
        "maximum_excess": -(1 << 60),
        "maximum_excess_X": 0,
        "source_at_max": 0,
        "capacity_at_max": 0,
    }


def observe(audit: dict[str, int], x: int, source: int, capacity: int) -> None:
    audit["source_events"] += 1
    excess = source - capacity
    if excess > 0:
        audit["failure_events"] += 1
        if audit["first_failure"] == 0:
            audit["first_failure"] = x
            audit["source_at_first_failure"] = source
            audit["capacity_at_first_failure"] = capacity
    if excess > audit["maximum_excess"]:
        audit["maximum_excess"] = excess
        audit["maximum_excess_X"] = x
        audit["source_at_max"] = source
        audit["capacity_at_max"] = capacity


def run(limit: int) -> dict:
    spectral_a = sum((Fraction(1, d) for d in D2), Fraction())
    spectral_b = sum((Fraction(1, d) for d in D0), Fraction())
    spectral_gate = (
        3 - 10 * spectral_a + 3 * spectral_a**2 - 3 * spectral_b
    )
    rejected_gate = spectral_gate - Fraction(3, 87)
    trace = Fraction(1, 3) + spectral_a
    determinant = (
        (spectral_a / 2) * (Fraction(1, 3) + spectral_a / 2)
        - Fraction(1, 2) * (Fraction(5, 6) + spectral_b / 2)
    )
    rho = (
        float(trace)
        + math.sqrt(float(trace * trace - 4 * determinant))
    ) / 2
    assert spectral_a == Fraction(4480997, 14222285)
    assert spectral_b == Fraction(34, 759)
    assert spectral_gate == Fraction(59225568637646, 4652287984288175)
    assert rejected_gate == Fraction(
        -2934746493796441, 134916351544357075
    )
    assert rho < 1

    spf = list(range(limit + 2))
    p = 2
    while p * p <= limit + 1:
        if spf[p] == p:
            for multiple in range(p * p, limit + 2, p):
                if spf[multiple] == multiple:
                    spf[multiple] = p
        p += 1

    member = bytearray(limit + 1)
    hole_type = bytearray(limit + 1)
    member[2] = member[3] = 1
    for n in range(4, limit + 1):
        product = n + 1
        has_split = False
        for left in divisors_from_spf(product, spf):
            if left < 2:
                continue
            right = product // left
            if left >= right or not allowed(left) or not allowed(right):
                continue
            has_split = True
            if member[left] and member[right]:
                member[n] = 1
        if not allowed(n) or member[n]:
            continue
        if not has_split:
            hole_type[n] = E
        elif n & 1:
            hole_type[n] = O0 if n % 3 == 0 else O2
        else:
            parent = (n + 1) // 3
            if (n + 1) % 3 == 0 and allowed(parent) and parent != 3:
                assert not member[parent]
                hole_type[n] = S
            elif n % 3 == 0:
                hole_type[n] = H0
            else:
                assert n % 18 == 2
                hole_type[n] = H2

    assert all(member[d] for d in PRIORITY)
    prefix_o0 = [0] * (limit + 1)
    prefix_o2 = [0] * (limit + 1)
    for n in range(2, limit + 1):
        prefix_o0[n] = prefix_o0[n - 1] + (hole_type[n] == O0)
        prefix_o2[n] = prefix_o2[n - 1] + (hole_type[n] == O2)

    def cap0(x: int) -> int:
        return sum(prefix_o2[(x + 1) // d] for d in D2)

    def cap2(x: int) -> int:
        return sum(prefix_o0[(x + 1) // d] for d in D2) + sum(
            prefix_o2[(x + 1) // d] for d in D0
        )

    counts = {name: 0 for name in ("M0", "M2", "E", "O0", "O2", "S", "H0", "H2")}
    residual0 = residual2 = forced11 = forced11_residual = 0
    assigned0 = {d: 0 for d in D2}
    assigned2 = {d: 0 for d in PRIORITY}
    audit0 = make_audit()
    audit2 = make_audit()
    combined = make_audit()

    for n in range(2, limit + 1):
        if allowed(n) and not member[n]:
            counts["M0" if n % 3 == 0 else "M2"] += 1
        kind = hole_type[n]
        if kind == E:
            counts["E"] += 1
        elif kind == O0:
            counts["O0"] += 1
        elif kind == O2:
            counts["O2"] += 1
        elif kind == S:
            counts["S"] += 1
        elif kind == H0:
            counts["H0"] += 1
            handled = False
            for d in D2:
                if (n + 1) % d:
                    continue
                parent = (n + 1) // d
                if parent == d:
                    continue
                assert hole_type[parent] == O2
                assigned0[d] += 1
                handled = True
                break
            if not handled:
                residual0 += 1
            if (n + 1) % 11 == 0:
                q = (n + 1) // 11
                if q >= 5 and q != 11 and spf[q] == q and member[q]:
                    forced11 += 1
                    forced11_residual += not handled
            observe(audit0, n, counts["H0"], cap0(n))
            observe(
                combined,
                n,
                counts["H0"] + counts["H2"],
                cap0(n) + cap2(n),
            )
        elif kind == H2:
            counts["H2"] += 1
            handled = False
            for d in PRIORITY:
                if (n + 1) % d:
                    continue
                parent = (n + 1) // d
                if parent == d:
                    continue
                assert hole_type[parent] == (O0 if d in D2 else O2)
                assigned2[d] += 1
                handled = True
                break
            if not handled:
                residual2 += 1
            observe(audit2, n, counts["H2"], cap2(n))
            observe(
                combined,
                n,
                counts["H0"] + counts["H2"],
                cap0(n) + cap2(n),
            )

    assert counts["M0"] + counts["M2"] == sum(
        counts[name] for name in ("E", "O0", "O2", "S", "H0", "H2")
    )
    result = {
        "schema_version": 1,
        "limit": limit,
        "spectral": {
            "a": str(spectral_a),
            "b": str(spectral_b),
            "gate": str(spectral_gate),
            "gate_with_87": str(rejected_gate),
            "rho": rho,
        },
        "counts": counts,
        "sieve": {
            "residual0": residual0,
            "residual2": residual2,
            "forced11": forced11,
            "forced11_residual": forced11_residual,
            "assigned0": assigned0,
            "assigned2": assigned2,
        },
        "recurrences": {
            "H0_le_D2O2": audit0,
            "H2_le_D2O0_plus_D0O2": audit2,
            "combined": combined,
        },
    }
    if limit == 100_000:
        assert counts == {
            "M0": 16823,
            "M2": 10000,
            "E": 11928,
            "O0": 3589,
            "O2": 4152,
            "S": 2046,
            "H0": 4388,
            "H2": 720,
        }
        assert residual0 + residual2 == 3018
        assert (forced11, forced11_residual) == (350, 346)
        assert (
            audit0["first_failure"],
            audit0["source_at_first_failure"],
            audit0["capacity_at_first_failure"],
        ) == (252, 7, 6)
        assert audit2["failure_events"] == 0
        assert (
            combined["first_failure"],
            combined["source_at_first_failure"],
            combined["capacity_at_first_failure"],
        ) == (18938, 1006, 1005)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.limit)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        f"limit={args.limit} H={result['counts']['H0'] + result['counts']['H2']} "
        f"residual={result['sieve']['residual0'] + result['sieve']['residual2']} "
        f"first_combined_failure="
        f"{result['recurrences']['combined']['first_failure']}"
    )


if __name__ == "__main__":
    main()
