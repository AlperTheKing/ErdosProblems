"""Search abstract interval models for NET/containment-flow obstructions.

This is not a graph verifier.  It tests which parts of the proposed
P-contained endpoint-tax route are purely interval-combinatorial.

Atoms are P-contained bad-row intervals J=[lo,hi] with unit weight.  Spans are
off-path component attachment intervals C=[lo,hi] with unit capacity for NET
endpoint tax.  We enforce:

* odd atom vertex-length at least 5;
* no bracket hub: no path position is simultaneously a right endpoint of one
  atom and a left endpoint of another;
* scalar NET: every interval I sees at least as many intersecting spans as
  atoms intersecting I;

and ask whether the stronger containment-flow statement must hold, i.e. every
atom can be matched to a span containing it.
"""

from __future__ import annotations

from itertools import combinations


def intervals(L: int):
    return [(a, b) for a in range(L) for b in range(a, L)]


def valid_atom(iv, L):
    a, b = iv
    length = b - a + 1
    return length >= 5 and length % 2 == 1 and (a, b) != (0, L - 1)


def no_bracket(atoms):
    starts = {a for a, _ in atoms}
    ends = {b for _, b in atoms}
    return not (starts & ends)


def scalar_net_holds(L, atoms, spans):
    for I in intervals(L):
        a, b = I
        demand = sum(1 for lo, hi in atoms if not (hi < a or b < lo))
        cap = sum(1 for lo, hi in spans if not (hi < a or b < lo))
        if demand > cap:
            return False, (I, demand, cap)
    return True, None


def containment_matching_holds(atoms, spans):
    """Unit-weight bipartite matching atom -> containing span."""
    n = len(atoms)
    adj = []
    for alo, ahi in atoms:
        adj.append([j for j, (slo, shi) in enumerate(spans) if slo <= alo and ahi <= shi])

    match_to = [-1] * len(spans)

    def dfs(i, seen):
        for j in adj[i]:
            if seen[j]:
                continue
            seen[j] = True
            if match_to[j] < 0 or dfs(match_to[j], seen):
                match_to[j] = i
                return True
        return False

    for i in range(n):
        if not dfs(i, [False] * len(spans)):
            return False
    return True


def find_first(max_L=12, max_atoms=4, max_spans=4):
    for L in range(5, max_L + 1):
        all_atoms = [iv for iv in intervals(L) if valid_atom(iv, L)]
        all_spans = intervals(L)
        for na in range(1, max_atoms + 1):
            for atoms in combinations(all_atoms, na):
                if not no_bracket(atoms):
                    continue
                for ns in range(1, max_spans + 1):
                    for spans in combinations(all_spans, ns):
                        ok, _bad = scalar_net_holds(L, atoms, spans)
                        if not ok:
                            continue
                        if not containment_matching_holds(atoms, spans):
                            return L, atoms, spans
    return None


def main():
    res = find_first()
    if res is None:
        print("NO abstract obstruction found")
        return
    L, atoms, spans = res
    print(f"L={L}")
    print(f"atoms={atoms}")
    print(f"spans={spans}")
    ok, bad = scalar_net_holds(L, atoms, spans)
    print(f"scalar_net={ok} bad={bad}")
    print(f"containment_matching={containment_matching_holds(atoms, spans)}")


if __name__ == "__main__":
    main()
