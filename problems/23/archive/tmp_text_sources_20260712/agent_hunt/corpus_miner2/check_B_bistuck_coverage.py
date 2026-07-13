"""CHECK B — are coverage-witness atoms bi-stuck?  (grounds the untried
combination: round-1 RANK-1 forced bounce  x  round-1 matroid bi-stuck kill).

Definitions (matroid report / R48):
  owners v,m = the two same-shore degree-5 support vertices (t=5).
  bi-stuck atom = incident to NEITHER owner, and EVERY row of its complete
    shortest-row family contains v or m.
  coverage witness for (owner w, active x0, star pair {x0,y}) = a row Q of an
    atom NOT incident to w, with w not in Q and x0,y both in Q
    (y in N_support(w) minus {x0}).
  coverage atom = an atom carrying at least one coverage witness.

Combination hypothesis to ground: coverage atoms are (mostly) bi-stuck, so a
single-row rotor handoff between the two owners' profile classes is blocked by
the coverage layer itself (Hamming >= #bi-stuck coverage atoms).

Exact integer arithmetic only; complete row families from the fixture DBs.
"""

import sys
from collections import defaultdict

sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_hunt\matroid")
import fixtures  # noqa: E402


def support_neighbours(circ, v):
    out = set()
    for (a, b) in circ.support:
        if a == v:
            out.add(b)
        elif b == v:
            out.add(a)
    return out


def analyse(circ, owners, actives):
    print(f"=== {circ.name} owners={owners} actives={actives} ===")
    v, m = owners
    # bi-stuck atoms
    bistuck = []
    for idx, a in enumerate(circ.atoms):
        if v in (a["u"], a["v"]) or m in (a["u"], a["v"]):
            continue
        if all((v in row) or (m in row) for row in a["rows"]):
            bistuck.append(idx)
    print(f"  bi-stuck atoms ({len(bistuck)}): "
          f"{[(circ.atoms[i]['u'], circ.atoms[i]['v']) for i in bistuck]}")

    # coverage atoms per owner
    for w, x0 in zip(owners, actives):
        nb = support_neighbours(circ, w)
        stars = sorted(nb - {x0})
        cov_atoms = defaultdict(list)   # atom idx -> list of covered pairs
        for idx, a in enumerate(circ.atoms):
            if w in (a["u"], a["v"]):
                continue
            for row in a["rows"]:
                if w in row:
                    continue
                if x0 not in row:
                    continue
                for y in stars:
                    if y in row:
                        cov_atoms[idx].append((x0, y, row))
        covered_pairs = sorted({(x0, y) for lst in cov_atoms.values()
                                for (_, y, _) in lst})
        n_cov_bistuck = sum(1 for idx in cov_atoms if idx in set(bistuck))
        print(f"  owner {w} (active {x0}, star {stars}): "
              f"{len(covered_pairs)}/{len(stars)} star pairs covered, "
              f"{len(cov_atoms)} coverage atoms, "
              f"{n_cov_bistuck} of them bi-stuck")
        for idx in sorted(cov_atoms):
            a = circ.atoms[idx]
            pairs = sorted({(x, y) for (x, y, _) in cov_atoms[idx]})
            tag = "BI-STUCK" if idx in set(bistuck) else "free"
            # which owner does each row visit if bi-stuck?
            print(f"    atom {(a['u'], a['v'])} covers {pairs} [{tag}] "
                  f"rows={len(a['rows'])}")
    print()


def main():
    fx = fixtures.load_all()
    # owners: two same-shore degree-5 support vertices; actives from archives.
    analyse(fx["hit298"], owners=(0, 1), actives=(17, 17))
    analyse(fx["hit264"], owners=(0, 1), actives=(9, 9))
    analyse(fx["nearcand"], owners=(0, 1), actives=(12, 12))
    print("CHECK B COMPLETE (no asserts; observational grounding)")


if __name__ == "__main__":
    main()
