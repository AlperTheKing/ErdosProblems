"""verify_4 CHECK 2 — adversarial re-verification of corpus_miner2 RANK 4
(bi-stuck coverage): universal form claimed REFUTED on #264, holding on
#298 and the 18-vtx near-candidate.

Definitions (round-1 matroid report / R48, as operationalized by check_B):
  owners v,m       = the two same-shore degree-5 support vertices
  bi-stuck atom    = incident to NEITHER owner and EVERY row of its complete
                     family contains v or m
  coverage witness for (owner w, active x0, star pair {x0,y}) = a row Q of an
                     atom not incident to w with w not in Q, x0 in Q, y in Q,
                     where y in N_support(w) - {x0}
  coverage atom    = an atom carrying at least one coverage witness
Claimed: #298 owner0 4/4 bi-stuck, owner1 4/4; nearcand 5/5 + 5/5;
  #264 owner0 5/6 free (1 bi-stuck), owner1 5/5 free, with owner-avoiding
  coverage atoms (2,3),(9,11),(10,14),(12,14),(13,14).
"""

import sys
from collections import defaultdict

sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_hunt\verify_4")
from v4_fixtures import load_all  # noqa: E402


def nbrs(f, v):
    out = set()
    for (a, b) in f.support:
        if a == v:
            out.add(b)
        if b == v:
            out.add(a)
    return out


def degree(f, v):
    return len(nbrs(f, v))


def run(f, owners, actives):
    v, m = owners
    # verify the owner choice: same-shore degree-5 vertices
    degs = {u: degree(f, u) for u in range(f.n)}
    deg5 = sorted(u for u, d in degs.items() if d == 5)
    same_shore = ((v in f.left) == (m in f.left))
    print(f"=== {f.name}: owners {owners} (deg {degs[v]},{degs[m]}; "
          f"same shore {same_shore}; all deg-5 vertices {deg5}) "
          f"actives {actives} ===")
    assert degs[v] == 5 and degs[m] == 5 and same_shore

    bistuck = set()
    for i, (au, av, rows) in enumerate(f.atoms):
        if v in (au, av) or m in (au, av):
            continue
        if all((v in r) or (m in r) for r in rows):
            bistuck.add(i)
    print(f"  bi-stuck atoms ({len(bistuck)}): "
          f"{sorted((f.atoms[i][0], f.atoms[i][1]) for i in bistuck)}")

    verdicts = []
    owner_avoiding_cov = set()
    for w, x0 in zip(owners, actives):
        stars = sorted(nbrs(f, w) - {x0})
        cov = defaultdict(set)
        for i, (au, av, rows) in enumerate(f.atoms):
            if w in (au, av):
                continue
            for r in rows:
                if w in r or x0 not in r:
                    continue
                for y in stars:
                    if y in r:
                        cov[i].add((x0, y))
        nb = sum(1 for i in cov if i in bistuck)
        free = sorted((f.atoms[i][0], f.atoms[i][1])
                      for i in cov if i not in bistuck)
        for i in cov:
            if i not in bistuck:
                owner_avoiding_cov.add((f.atoms[i][0], f.atoms[i][1]))
        pairs_covered = {p for s in cov.values() for p in s}
        print(f"  owner {w} active {x0}: coverage atoms={len(cov)} "
              f"bi-stuck={nb} free={len(cov)-nb} "
              f"(star pairs covered {len(pairs_covered)}/{len(stars)})")
        if free:
            print(f"    free coverage atoms: {free}")
        verdicts.append((len(cov), nb))
    return verdicts, sorted(owner_avoiding_cov)


def main():
    fx = load_all()
    v298, _ = run(fx["hit298"], (0, 1), (17, 17))
    v264, free264 = run(fx["hit264"], (0, 1), (9, 9))
    vnc, _ = run(fx["nearcand"], (0, 1), (12, 12))

    print("\n--- verdict vs corpus_miner2 claims ---")
    print(f"#298 (claim 4/4 + 4/4 bi-stuck): {v298}")
    print(f"nearcand (claim 5/5 + 5/5 bi-stuck): {vnc}")
    print(f"#264 (claim owner0 6 cov/1 bi-stuck, owner1 5 cov/0 bi-stuck): "
          f"{v264}")
    print(f"#264 owner-avoiding coverage atoms (claim (2,3),(9,11),(10,14),"
          f"(12,14),(13,14)): {free264}")
    assert v298[0] == (v298[0][0], v298[0][0]) and \
        v298[1] == (v298[1][0], v298[1][0]), "#298 universal form FAILS?"
    assert vnc[0][0] == vnc[0][1] and vnc[1][0] == vnc[1][1]
    assert v264[0][1] < v264[0][0] or v264[1][1] < v264[1][0], \
        "#264 refutation NOT reproduced"
    print("V4 CHECK RANK4 COMPLETE")


if __name__ == "__main__":
    main()
