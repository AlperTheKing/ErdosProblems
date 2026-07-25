#!/usr/bin/env python3
"""Compare the audited r5 GHTE contract with the independent audit output.

This companion is intentionally separate from the zero-trust reconstruction:
the latter never imports the audited checker.  Here we compare exact face data,
BV vectors, volumes, and the row spaces of the differently represented balance
matrices after both computations have completed.
"""

import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import r5_lowerdim_complete_fan_ghte_contract as checked  # noqa: E402
import r5_lowerdim_complete_fan_ghte_zero_trust_audit as audit  # noqa: E402


def main():
    for name, boundary in (("horn_gap", checked.HORN_GAP),
                           ("hard", checked.HARD)):
        left = checked.build_contract(name, boundary)
        right = audit.build_contract(name, boundary)
        assert left["intrinsic_vertices"] == right["intrinsic_vertices"]
        assert left["lattices"]["M_basis_in_Z6"] == right["M_basis_in_Z6"]
        left_facets = tuple((item["normal"], item["rhs"], item["vertices"])
                            for item in left["facets"])
        right_facets = tuple((item["normal"], item["rhs"], item["vertices"])
                             for item in right["facets"])
        assert left_facets == right_facets
        left_edges = tuple((item["vertices"], item["facets"], item["length"])
                           for item in left["edges"])
        right_edges = tuple((item["vertices"], item["facets"], item["length"])
                            for item in right["edges"])
        assert left_edges == right_edges
        assert left["q2"]["BV_a"] == right["q2"]["BV_a"]
        assert left["q2"]["face_volume_v"] == right["q2"]["face_volume_v"]
        q2_joined_rank = audit.rank(
            tuple(left["q2"]["B"]) + tuple(right["q2"]["B_cross_embedding"])
        )
        assert q2_joined_rank == left["q2"]["rank_B"] == right["q2"]["rank_B"]
        assert left["q3"]["BV_a"] == right["q3"]["BV_a"]
        q3_joined_rank = audit.rank(
            tuple(left["q3"]["B"]) + tuple(right["q3"]["B_graph_incidence"])
        )
        assert q3_joined_rank == left["q3"]["rank_B"] == right["q3"]["rank_B"]
        print(f"{name}: FULL_MATCH q2_rowspace_rank={q2_joined_rank} "
              f"q3_rowspace_rank={q3_joined_rank}")
    print("PASS")


if __name__ == "__main__":
    main()
