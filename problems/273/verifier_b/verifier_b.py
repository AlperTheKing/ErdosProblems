#!/usr/bin/env python3
"""Independent reduced-fiber verifier for the p >= 3 baseline of Problem 273.

This verifier deliberately does not import, execute, or share a full-period
coverage formulation with Verifier A.  It checks a sequential partition of
the reduced coordinate n modulo 180, then proves that x = 2*n + 1 lifts each
reduced leaf to the stated congruence modulo 360.  The even fiber is handled
by the single leaf 0 (mod 2).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "erdos273.reduced-half-cover.v1"
MASK_RE = re.compile(r"0x[0-9a-f]+\Z")


class CertificateError(ValueError):
    """Raised when any exact certificate obligation fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def exact_keys(value: Any, keys: set[str], where: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{where}: expected object")
    actual = set(value)
    require(actual == keys, f"{where}: keys {sorted(actual)} != {sorted(keys)}")
    return value


def exact_int(value: Any, where: str) -> int:
    require(type(value) is int, f"{where}: expected integer")
    return value


def decode_mask(value: Any, width: int, where: str) -> int:
    require(isinstance(value, str), f"{where}: expected hexadecimal string")
    digits = (width + 3) // 4
    require(MASK_RE.fullmatch(value) is not None, f"{where}: noncanonical hex")
    require(len(value) == digits + 2, f"{where}: expected {digits} hex digits")
    mask = int(value, 16)
    require(mask < (1 << width), f"{where}: bit outside width {width}")
    require(value == f"0x{mask:0{digits}x}", f"{where}: noncanonical padding")
    return mask


def progression_mask(residue: int, modulus: int, period: int) -> int:
    """Bit mask of one normalized residue class in [0, period)."""
    require(modulus > 0, "progression: modulus must be positive")
    require(0 <= residue < modulus, "progression: residue is not normalized")
    require(period % modulus == 0, "progression: modulus does not divide period")
    result = 0
    for n in range(residue, period, modulus):
        result |= 1 << n
    return result


def set_bits(mask: int) -> Iterable[int]:
    """Yield indices of set bits, from least to greatest."""
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def check_distinct(values: list[int], where: str) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    require(not duplicates, f"{where}: duplicate values {duplicates}")


def verify_prime_trial_certificate(item: Any, expected_number: int, where: str) -> tuple[int, int]:
    item = exact_keys(item, {"number", "trial_bound", "remainders"}, where)
    number = exact_int(item["number"], f"{where}.number")
    bound = exact_int(item["trial_bound"], f"{where}.trial_bound")
    remainders = item["remainders"]
    require(number == expected_number, f"{where}: number {number} != {expected_number}")
    require(number >= 2, f"{where}: number is below 2")
    require(bound == math.isqrt(number), f"{where}: trial bound is not floor(sqrt(number))")
    require(isinstance(remainders, list), f"{where}.remainders: expected array")
    expected = [number % divisor for divisor in range(2, bound + 1)]
    require(remainders == expected, f"{where}: incorrect exact remainder vector")
    require(all(remainder != 0 for remainder in remainders), f"{where}: composite divisor found")
    # Every composite integer has a divisor in [2, floor(sqrt(number))].
    # Thus the checked nonzero remainder vector is a complete primality proof.
    return bound, len(remainders)


def verify_certificate(
    document: Any,
    *,
    certificate_path: Path | None = None,
    verifier_path: Path | None = None,
) -> list[str]:
    root = exact_keys(
        document,
        {
            "schema",
            "description",
            "periods",
            "coordinate_map",
            "even_leaf",
            "odd_fiber_chain",
            "prime_trial_certificates",
        },
        "root",
    )
    require(root["schema"] == SCHEMA, f"root.schema: expected {SCHEMA}")
    require(isinstance(root["description"], str), "root.description: expected string")

    periods = exact_keys(root["periods"], {"reduced", "full"}, "periods")
    reduced_period = exact_int(periods["reduced"], "periods.reduced")
    full_period = exact_int(periods["full"], "periods.full")
    require(reduced_period > 0, "periods.reduced: must be positive")
    require(full_period == 2 * reduced_period, "periods: full must equal 2*reduced")

    coordinate_map = exact_keys(
        root["coordinate_map"], {"even_formula", "odd_formula"}, "coordinate_map"
    )
    require(coordinate_map["even_formula"] == "x=2*t", "coordinate_map.even_formula mismatch")
    require(coordinate_map["odd_formula"] == "x=2*n+1", "coordinate_map.odd_formula mismatch")

    even = exact_keys(root["even_leaf"], {"id", "residue", "modulus"}, "even_leaf")
    require(even["id"] == "E", "even_leaf.id: expected E")
    even_residue = exact_int(even["residue"], "even_leaf.residue")
    even_modulus = exact_int(even["modulus"], "even_leaf.modulus")
    require((even_residue, even_modulus) == (0, 2), "even_leaf: expected 0 (mod 2)")

    leaves = root["odd_fiber_chain"]
    require(isinstance(leaves, list) and leaves, "odd_fiber_chain: expected nonempty array")
    universe = (1 << reduced_period) - 1
    residual = universe
    transitions: list[dict[str, int | str]] = []
    lifted_pairs: list[tuple[int, int]] = []

    leaf_keys = {"id", "reduced_class", "lifted_class", "transition"}
    class_keys = {"residue", "modulus"}
    transition_keys = {
        "before_count",
        "removed_count",
        "after_count",
        "before_mask",
        "removed_mask",
        "after_mask",
    }

    for index, raw_leaf in enumerate(leaves, start=1):
        where = f"odd_fiber_chain[{index - 1}]"
        leaf = exact_keys(raw_leaf, leaf_keys, where)
        leaf_id = leaf["id"]
        require(leaf_id == f"R{index}", f"{where}.id: expected R{index}")
        reduced = exact_keys(leaf["reduced_class"], class_keys, f"{where}.reduced_class")
        lifted = exact_keys(leaf["lifted_class"], class_keys, f"{where}.lifted_class")
        transition = exact_keys(leaf["transition"], transition_keys, f"{where}.transition")

        a = exact_int(reduced["residue"], f"{where}.reduced_class.residue")
        m = exact_int(reduced["modulus"], f"{where}.reduced_class.modulus")
        lifted_a = exact_int(lifted["residue"], f"{where}.lifted_class.residue")
        lifted_m = exact_int(lifted["modulus"], f"{where}.lifted_class.modulus")
        require(m > 0 and reduced_period % m == 0, f"{where}: reduced modulus must divide period")
        require(0 <= a < m, f"{where}: reduced residue is not normalized")
        require((lifted_a, lifted_m) == (2 * a + 1, 2 * m), f"{where}: incorrect odd lift")
        require(full_period % lifted_m == 0, f"{where}: lifted modulus must divide full period")
        require(0 <= lifted_a < lifted_m, f"{where}: lifted residue is not normalized")

        before = decode_mask(transition["before_mask"], reduced_period, f"{where}.before_mask")
        removed_claim = decode_mask(
            transition["removed_mask"], reduced_period, f"{where}.removed_mask"
        )
        after_claim = decode_mask(transition["after_mask"], reduced_period, f"{where}.after_mask")
        require(before == residual, f"{where}: before mask does not equal preceding residual")

        class_mask = progression_mask(a, m, reduced_period)
        removed = residual & class_mask
        after = residual & (universe ^ class_mask)
        require(removed != 0, f"{where}: leaf removes no residual point")
        require(removed_claim == removed, f"{where}: removed mask is incorrect")
        require(after_claim == after, f"{where}: after mask is incorrect")
        require((removed & after) == 0, f"{where}: removed and after masks overlap")
        require((removed | after) == before, f"{where}: transition does not partition before mask")

        counts = (
            exact_int(transition["before_count"], f"{where}.before_count"),
            exact_int(transition["removed_count"], f"{where}.removed_count"),
            exact_int(transition["after_count"], f"{where}.after_count"),
        )
        actual_counts = (before.bit_count(), removed.bit_count(), after.bit_count())
        require(counts == actual_counts, f"{where}: counts {counts} != {actual_counts}")

        # Check the containment of the entire reduced class, including points
        # already assigned by an earlier leaf, not merely the newly removed set.
        containment_count = 0
        for n in set_bits(class_mask):
            x = 2 * n + 1
            require((x - lifted_a) % lifted_m == 0, f"{where}: lift containment fails at n={n}")
            containment_count += 1
        require(
            containment_count == reduced_period // m,
            f"{where}: wrong number of points in reduced class",
        )

        transitions.append(
            {
                "id": leaf_id,
                "a": a,
                "m": m,
                "lifted_a": lifted_a,
                "lifted_m": lifted_m,
                "before": actual_counts[0],
                "removed": actual_counts[1],
                "after": actual_counts[2],
                "contained": containment_count,
            }
        )
        lifted_pairs.append((lifted_a, lifted_m))
        residual = after

    require(residual == 0, f"odd_fiber_chain: final residual has {residual.bit_count()} points")

    system = [(even_residue, even_modulus), *lifted_pairs]
    moduli = [modulus for _, modulus in system]
    check_distinct(moduli, "system moduli")
    require(all(modulus > 0 for modulus in moduli), "system: nonpositive modulus")
    require(all(full_period % modulus == 0 for modulus in moduli), "system: modulus misses full period")
    system_lcm = math.lcm(*moduli)
    require(system_lcm == full_period, f"system: LCM {system_lcm} != full period {full_period}")

    # Independently validate the parity-coordinate bijection on the period.
    even_points = {2 * t for t in range(reduced_period)}
    odd_points = {2 * n + 1 for n in range(reduced_period)}
    require(even_points.isdisjoint(odd_points), "parity partition: fibers overlap")
    require(even_points | odd_points == set(range(full_period)), "parity partition: not exhaustive")
    require(all(x % 2 == 0 for x in even_points), "even leaf containment failure")

    prime_items = root["prime_trial_certificates"]
    require(isinstance(prime_items, list), "prime_trial_certificates: expected array")
    expected_primes = [modulus + 1 for modulus in moduli]
    require(len(prime_items) == len(expected_primes), "prime_trial_certificates: wrong length")
    prime_rows: list[tuple[int, int, int, int]] = []
    for index, (item, modulus, expected_prime) in enumerate(
        zip(prime_items, moduli, expected_primes, strict=True)
    ):
        bound, checks = verify_prime_trial_certificate(
            item, expected_prime, f"prime_trial_certificates[{index}]"
        )
        require(expected_prime >= 3, f"modulus {modulus}: prime is below baseline threshold 3")
        prime_rows.append((modulus, expected_prime, bound, checks))

    canonical_system = "".join(f"{a},{m}\n" for a, m in system).encode("ascii")
    transition_payload = "".join(
        f"{leaf['id']}:{leaf['a']},{leaf['m']}:{leaf['before']},{leaf['removed']},{leaf['after']}\n"
        for leaf in transitions
    ).encode("ascii")

    lines = [
        f"VERIFIER_B schema={SCHEMA}",
        "METHOD reduced-residue transition masks modulo 180; no full-period class-union enumeration",
        f"PERIOD reduced={reduced_period} full={full_period} lcm={system_lcm}",
        "PARITY even=0(mod 2) odd=x=2*n+1 partition=exact",
    ]
    for row in transitions:
        lines.append(
            "STEP {id} n={a}(mod {m}) x={lifted_a}(mod {lifted_m}) "
            "before={before} removed={removed} after={after} class_containment={contained}/{contained}".format(
                **row
            )
        )
    for modulus, prime, bound, checks in prime_rows:
        lines.append(
            f"PRIME modulus={modulus} p={prime} floor_sqrt={bound} exact_division_checks={checks} status=prime"
        )
    lines.extend(
        [
            f"DISTINCT moduli={len(moduli)} status=pairwise-distinct",
            f"COVER reduced_assigned={sum(int(row['removed']) for row in transitions)}/{reduced_period} final_residual=0",
            f"SYSTEM_SHA256 {sha256_bytes(canonical_system)}",
            f"TRANSITIONS_SHA256 {sha256_bytes(transition_payload)}",
        ]
    )
    if certificate_path is not None:
        lines.append(f"CERTIFICATE_SHA256 {sha256_file(certificate_path)}")
    if verifier_path is not None:
        lines.append(f"VERIFIER_SHA256 {sha256_file(verifier_path)}")
    lines.append("RESULT PASS")
    return lines


def parse_args(argv: list[str]) -> argparse.Namespace:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "certificate",
        nargs="?",
        type=Path,
        default=base / "baseline_half_cover_certificate.json",
    )
    parser.add_argument("--log", type=Path, help="write the deterministic verifier transcript")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    certificate_path = args.certificate.resolve()
    verifier_path = Path(__file__).resolve()
    try:
        document = json.loads(certificate_path.read_text(encoding="utf-8"))
        lines = verify_certificate(
            document,
            certificate_path=certificate_path,
            verifier_path=verifier_path,
        )
    except (OSError, json.JSONDecodeError, CertificateError) as error:
        lines = [f"RESULT FAIL {type(error).__name__}: {error}"]
        result = 1
    else:
        result = 0
    transcript = "\n".join(lines) + "\n"
    sys.stdout.write(transcript)
    if args.log is not None:
        args.log.write_text(transcript, encoding="utf-8", newline="\n")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
