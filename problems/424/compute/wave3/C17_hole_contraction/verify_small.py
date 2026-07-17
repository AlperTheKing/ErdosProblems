import json
import math
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


WEIGHT_SCALE = 1 << 30
ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[4]
C22_RESULT = Path(
    "problems/424/compute/wave3/C22_universal_contraction_sat/result_5000.json"
)


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    result = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


def naive_census(limit: int) -> dict:
    member = [False] * (limit + 1)
    rank = [None] * (limit + 1)
    member[2] = True
    member[3] = True
    rank[2] = 0
    rank[3] = 0
    pairs_by_n = [[] for _ in range(limit + 1)]
    missing_prefix = [0] * (limit + 1)
    splitless = 0
    reciprocal_charge = Fraction(0)
    fixed_charge_num = 0
    max_direct = (Fraction(0), 0)
    max_fixed = (Fraction(0), 0)
    first_direct_two = 0
    first_two_scale_failure = 0
    first_fixed_two = 0
    odd_reducible = 0
    seed3_even_reducible = 0
    hard_reducible = 0
    seed2_healed = 0
    rank_histogram = [2]
    healing_rank_histogram = [0]
    rank_cap_audits = {
        cap: {
            "cap": cap,
            "healed": 0,
            "first_failure_X": 0,
            "last_failure_X": 0,
            "maximum_excess": 0,
            "maximum_excess_X": 0,
        }
        for cap in (8, 9)
    }

    for n in range(2, limit + 1):
        pairs = admissible_pairs(n)
        pairs_by_n[n] = pairs
        witness_ranks = [
            1 + max(rank[left], rank[right])
            for left, right in pairs
            if member[left] and member[right]
        ]
        if witness_ranks:
            member[n] = True
            rank[n] = min(witness_ranks)
            while len(rank_histogram) <= rank[n]:
                rank_histogram.append(0)
            rank_histogram[rank[n]] += 1
            parent2 = (n + 1) // 2
            if n % 2 and allowed(parent2) and not member[parent2]:
                seed2_healed += 1
                while len(healing_rank_histogram) <= rank[n]:
                    healing_rank_histogram.append(0)
                healing_rank_histogram[rank[n]] += 1
                for cap, audit in rank_cap_audits.items():
                    if rank[n] <= cap:
                        audit["healed"] += 1

        missing_prefix[n] = missing_prefix[n - 1]
        if allowed(n) and not member[n]:
            missing_prefix[n] += 1
            if not pairs:
                splitless += 1
            else:
                if n % 2:
                    odd_reducible += 1
                else:
                    parent3 = (n + 1) // 3
                    if (n + 1) % 3 == 0 and allowed(parent3) and parent3 != 3:
                        seed3_even_reducible += 1
                    else:
                        hard_reducible += 1
                missing_incidences = sum(
                    (not member[left]) + (not member[right])
                    for left, right in pairs
                )
                pair_count = len(pairs)
                reciprocal_charge += Fraction(missing_incidences, pair_count)
                fixed_charge_num += missing_incidences * (
                    (WEIGHT_SCALE + pair_count - 1) // pair_count
                )

        for audit in rank_cap_audits.values():
            excess = hard_reducible - audit["healed"]
            if excess <= 0:
                continue
            if not audit["first_failure_X"]:
                audit["first_failure_X"] = n
            audit["last_failure_X"] = n
            if excess > audit["maximum_excess"]:
                audit["maximum_excess"] = excess
                audit["maximum_excess_X"] = n

        reducible = missing_prefix[n] - splitless
        half_missing = missing_prefix[(n + 1) // 2]
        if half_missing:
            direct = Fraction(reducible, half_missing)
            fixed = Fraction(fixed_charge_num, WEIGHT_SCALE * half_missing)
            if direct > max_direct[0]:
                max_direct = (direct, n)
            if fixed > max_fixed[0]:
                max_fixed = (fixed, n)
            if not first_direct_two and direct >= 2:
                first_direct_two = n
            if not first_fixed_two and fixed >= 2:
                first_fixed_two = n
        third_missing = missing_prefix[(n + 1) // 3]
        if not first_two_scale_failure and reducible > half_missing + third_missing:
            first_two_scale_failure = n

    return {
        "member": member,
        "pairs": pairs_by_n,
        "missing_prefix": missing_prefix,
        "splitless": splitless,
        "reciprocal_charge": reciprocal_charge,
        "fixed_charge_num": fixed_charge_num,
        "max_direct": max_direct,
        "max_fixed": max_fixed,
        "first_direct_two": first_direct_two,
        "first_two_scale_failure": first_two_scale_failure,
        "first_fixed_two": first_fixed_two,
        "odd_reducible": odd_reducible,
        "seed3_even_reducible": seed3_even_reducible,
        "hard_reducible": hard_reducible,
        "seed2_healed": seed2_healed,
        "rank_histogram": rank_histogram,
        "healing_rank_histogram": healing_rank_histogram,
        "rank_cap_audits": list(rank_cap_audits.values()),
    }


def hall_graph(census: dict, limit: int) -> tuple[list[int], list[list[int]]]:
    member = census["member"]
    pairs_by_n = census["pairs"]
    outputs = []
    graph = []
    for n in range(2, limit + 1):
        pairs = pairs_by_n[n]
        if not allowed(n) or member[n] or not pairs:
            continue
        if n % 2:
            outputs.append(n)
            graph.append([(n + 1) // 2])
            continue
        parent3 = (n + 1) // 3
        if (n + 1) % 3 == 0 and allowed(parent3) and parent3 != 3:
            continue
        neighbors = []
        for left, right in pairs:
            if not member[left]:
                neighbors.append(left)
            if not member[right]:
                neighbors.append(right)
        outputs.append(n)
        graph.append(neighbors)
    return outputs, graph


def kuhn_matching(graph: list[list[int]]) -> int:
    right_match = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in graph[left]:
            if right in seen:
                continue
            seen.add(right)
            if right not in right_match or augment(right_match[right], seen):
                right_match[right] = left
                return True
        return False

    return sum(augment(left, set()) for left in range(len(graph)))


class C17Verifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_exe = ROOT / "hole_contraction_redteam.exe"
        cls.hall_exe = ROOT / "hall_audit.exe"
        if not cls.main_exe.exists() or not cls.hall_exe.exists():
            raise RuntimeError("compile both C17 executables before running tests")
        cls.outputs = [
            ROOT / "_verify_weighted.json",
            ROOT / "_verify_hall54.json",
            ROOT / "_verify_hall2000.json",
            ROOT / "_verify_grounding5000.json",
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        for output in cls.outputs:
            output.unlink(missing_ok=True)

    def test_weighted_census_through_2000(self) -> None:
        limit = 2000
        expected = naive_census(limit)
        output = self.outputs[0]
        subprocess.run([str(self.main_exe), str(limit), str(output)], check=True)
        actual = json.loads(output.read_text(encoding="utf-8"))
        endpoint = actual["snapshots"][-1]

        self.assertEqual(endpoint["X"], limit)
        self.assertEqual(endpoint["generated"], sum(expected["member"]))
        self.assertEqual(
            endpoint["missing"], expected["missing_prefix"][limit]
        )
        self.assertEqual(endpoint["splitless_missing"], expected["splitless"])
        self.assertEqual(endpoint["odd_reducible"], expected["odd_reducible"])
        self.assertEqual(
            endpoint["seed3_even_reducible"], expected["seed3_even_reducible"]
        )
        self.assertEqual(endpoint["hard_reducible"], expected["hard_reducible"])
        self.assertEqual(endpoint["seed2_healed"], expected["seed2_healed"])
        self.assertEqual(
            endpoint["missing_at_third"],
            expected["missing_prefix"][(limit + 1) // 3],
        )
        self.assertEqual(
            endpoint["two_scale_excess"],
            endpoint["reducible_missing"]
            - endpoint["missing_at_half"]
            - endpoint["missing_at_third"],
        )
        self.assertEqual(endpoint["rank_histogram"], expected["rank_histogram"])
        self.assertEqual(
            endpoint["healing_rank_histogram"],
            expected["healing_rank_histogram"],
        )
        self.assertEqual(
            actual["rank_cap_healing_audit"], expected["rank_cap_audits"]
        )

        direct, direct_x = expected["max_direct"]
        self.assertEqual(
            actual["maximum_direct_coefficient"],
            {"X": direct_x, "numerator": direct.numerator, "denominator": direct.denominator},
        )
        fixed, fixed_x = expected["max_fixed"]
        self.assertEqual(actual["maximum_fixed_point_coefficient"]["X"], fixed_x)
        self.assertEqual(
            Fraction(
                actual["maximum_fixed_point_coefficient"]["numerator"],
                actual["maximum_fixed_point_coefficient"]["denominator"],
            ),
            fixed,
        )
        self.assertEqual(actual["first_lambda_two_failure_X"], 0)
        self.assertEqual(
            actual["first_two_scale_failure_X"],
            expected["first_two_scale_failure"],
        )
        self.assertEqual(actual["first_fixed_point_lambda_two_failure_X"], 0)

        reciprocal = endpoint["reciprocal_all_pair_charge"]
        self.assertEqual(
            Fraction(int(reciprocal["numerator"]), int(reciprocal["denominator"])),
            expected["reciprocal_charge"],
        )

    def test_hall_witness_at_54(self) -> None:
        limit = 54
        expected = naive_census(limit)
        outputs, graph = hall_graph(expected, limit)
        output = self.outputs[1]
        subprocess.run([str(self.hall_exe), str(limit), str(output)], check=True)
        actual = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(outputs, [11, 15, 21, 23, 29, 35, 39, 45, 47, 54])
        self.assertEqual(kuhn_matching(graph), 9)
        self.assertEqual(actual["matching_size"], 9)
        self.assertFalse(actual["perfect"])
        self.assertEqual(actual["hall_witness"]["left_sample"], [21, 54])
        self.assertEqual(actual["hall_witness"]["neighbor_sample"], [11])

        neighborhoods = {
            outputs[index]: set(graph[index]) for index in range(len(outputs))
        }
        self.assertEqual(neighborhoods[21] | neighborhoods[54], {11})

    def test_hall_matching_through_2000(self) -> None:
        limit = 2000
        expected = naive_census(limit)
        outputs, graph = hall_graph(expected, limit)
        output = self.outputs[2]
        subprocess.run([str(self.hall_exe), str(limit), str(output)], check=True)
        actual = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(actual["left_count"], len(outputs))
        self.assertEqual(actual["edge_count"], sum(map(len, graph)))
        self.assertEqual(actual["matching_size"], kuhn_matching(graph))

    def test_c22_grounding_replay(self) -> None:
        output = self.outputs[3]
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "grounding_audit.py"),
                str(C22_RESULT),
                str(output),
            ],
            cwd=REPO_ROOT,
            check=True,
        )
        actual = json.loads(output.read_text(encoding="ascii"))
        committed = json.loads(
            (ROOT / "grounding_5000.json").read_text(encoding="ascii")
        )
        self.assertEqual(actual, committed)
        self.assertFalse(actual["grounded"])
        self.assertEqual(actual["ungrounded_member_count"], 1384)
        self.assertEqual(actual["grounded_core_contraction"]["excess"], -515)


if __name__ == "__main__":
    unittest.main()
