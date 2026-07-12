"""CHECK C — exhaustive max_S kappa(S) on hit298 (canonical tuple) via the
selected-multiplicity route; cross-validates round-1 farkas Finding 4
(UNVERIFIED there: max kappa 19-20, engine sigma=-20) with an independent
implementation, and verifies kappa(S) <= sum_{e in delta(S) cap Sel}(s(e)-1)
for EVERY S (2^18 exhaustive).

kappa(S) = badCross(S) - |delta(S) cap F*|   (all support edges are blue).
Exact integers only.
"""

import sys

sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_hunt\matroid")
import fixtures  # noqa: E402


def main():
    fx = fixtures.load_all()
    for name in ("hit298", "hit264"):
        circ = fx[name]
        n = circ.n
        tup = tuple(0 for _ in circ.atoms)  # canonical tuple
        # selected multiplicities
        s = {}
        for a, ridx in zip(circ.atoms, tup):
            row = a["rows"][ridx]
            for k in range(4):
                e = fixtures.norm(row[k], row[k + 1])
                s[e] = s.get(e, 0) + 1
        support = list(circ.support)
        atom_pairs = [(a["u"], a["v"]) for a in circ.atoms]
        max_kappa = -10**9
        argmax = None
        viol = 0
        for mask in range(1 << n):
            bad_cross = 0
            for (u, v) in atom_pairs:
                if ((mask >> u) & 1) != ((mask >> v) & 1):
                    bad_cross += 1
            cross_support = 0
            excess = 0
            for (u, v) in support:
                if ((mask >> u) & 1) != ((mask >> v) & 1):
                    cross_support += 1
                    excess += max(0, s.get((u, v), 0) - 1)
            kappa = bad_cross - cross_support
            if kappa > max_kappa:
                max_kappa = kappa
                argmax = (mask, bad_cross, cross_support)
            if kappa > excess:
                viol += 1
        m, bc, cs = argmax
        members = sorted(v for v in range(n) if (m >> v) & 1)
        print(f"[{name}] canonical tuple: max_S kappa = {max_kappa} at "
              f"S={members} (badCross={bc}, supportCross={cs}); "
              f"kappa<=selectedExcess violations over all 2^{n} S: {viol}")
        assert viol == 0
    print("CHECK C: ALL ASSERTS GREEN")


if __name__ == "__main__":
    main()
