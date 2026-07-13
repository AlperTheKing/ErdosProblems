"""Exact search for submodularity of active-scoped score on trade cubes."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WRITEUP = ROOT / "problems" / "23" / "writeup"
sys.path.insert(0, str(WRITEUP))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import (
    active_scoped_obligation_parts,
)


def score(n, info, rows):
    c, h = active_scoped_obligation_parts(
        n, set(info["Bset"]), set(info["Mset"]), rows
    )
    return c + h, c, h


def main():
    tested = 0
    for n in range(5, 13):
        graph6, _ = graph6_for_orders(n, n)
        for g6 in graph6:
            nn, edges = dec(g6)
            info = loads(nn, edges)
            if info is None or any(x != 5 for x in info["ell"].values()):
                continue
            fam = shortest_row_families(info)
            coords = [i for i, f in enumerate(fam) if len(f) >= 2]
            if len(coords) < 2:
                continue
            base = tuple(f[0] for f in fam)
            for i, j in itertools.combinations(coords, 2):
                # Every alternative pair, not merely the first.
                for ai in range(1, len(fam[i])):
                    for aj in range(1, len(fam[j])):
                        r0 = base
                        ri = base[:i] + (fam[i][ai],) + base[i+1:]
                        rj = base[:j] + (fam[j][aj],) + base[j+1:]
                        rij = list(base)
                        rij[i], rij[j] = fam[i][ai], fam[j][aj]
                        rij = tuple(rij)
                        vals = [score(nn, info, r) for r in (r0, ri, rj, rij)]
                        tested += 1
                        # Submodularity: F(i)+F(j) >= F(empty)+F(ij).
                        if vals[1][0] + vals[2][0] < vals[0][0] + vals[3][0]:
                            out = {
                                "inequality": "F({i})+F({j}) >= F(empty)+F({i,j})",
                                "status": "false",
                                "testedBeforeWitness": tested,
                                "n": nn,
                                "g6": g6,
                                "edges": [list(e) for e in sorted(edges)],
                                "B": [list(e) for e in sorted(info["Bset"])],
                                "M": [list(e) for e in sorted(info["Mset"])],
                                "coordinateI": i,
                                "coordinateJ": j,
                                "baseRows": [list(r) for r in base],
                                "alternativeI": list(fam[i][ai]),
                                "alternativeJ": list(fam[j][aj]),
                                "scores_total_collision_hitneed": {
                                    "empty": vals[0], "i": vals[1],
                                    "j": vals[2], "ij": vals[3],
                                },
                                "lhs": vals[1][0] + vals[2][0],
                                "rhs": vals[0][0] + vals[3][0],
                            }
                            print(json.dumps(out, sort_keys=True, indent=2))
                            return 0
    print(json.dumps({"status": "no witness", "tested": tested}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
