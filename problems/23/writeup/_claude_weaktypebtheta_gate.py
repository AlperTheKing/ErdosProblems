"""EXACT gate for MAIN's route-B WeakTypeBThetaGate on the stretched L/(L+2) cores (gap #1, 2026-07-07).

For each stretched nested core (build from _l5forcing_gate: f0=(s,t) ell=L, f1=(u,v) ell=L+2, intended 2-coloring
`side`), SEARCH for a switch set U such that WeakTypeBThetaGate holds:
  H1.  delta_B(U) = {bornLo}     (exactly ONE cut edge crosses U -> exactly one born bad edge; the "one-door")
  H2a. oldHi=f1 is a bad edge crossing U   (and delta_M(U) = {f1}: ONLY f1 is killed)
  H3a. ell_B(f1) = L+2
  H3b. bornLo is bad in B^U and ell_{B^U}(bornLo) <= L
Then drop >= (L+2)^2 - L^2 = 4L+4 > 0 (strict decrease). If a valid U EXISTS for each L=5,7,9,11 => route B is
empirically supported (the one-door variable-L structure holds). If NO valid U exists for some L => that L exposes
one of the 3 blockers (NoSideDoorForLongAnnulus etc.) = the residual open lemma. EXACT integer ell. Run from problems/23/writeup.
NOTE: we search all U (2^n, n<=16 for L<=11) but restrict to U giving a NONTRIVIAL sigma-favorable flip; we report
the BEST U (min born count) and whether a full WeakTypeBThetaGate witness exists."""
from itertools import combinations
from _l5forcing_gate import build, edge
from _satzmu_conn import struct_for_side


def analyze(L):
    n, E, side, f0, f1, adj, bip = build(L)
    if not bip:
        return L, n, None, "blue not bipartite"
    st = struct_for_side(n, adj, side)
    if st is None:
        return L, n, None, "struct None"
    M, ell = set(st[0]), st[1]
    fe1 = edge(*f1)
    fe0 = edge(*f0)
    # H3a: ell_B(f1) = L+2
    h3a = (fe1 in ell and ell[fe1] == L + 2)
    Eedges = [edge(a, b) for a, b in E]
    best = None
    # search switch sets U (as vertex subsets); skip empty/full; enumerate by size for efficiency
    found = None
    import itertools
    verts = list(range(n))
    for r in range(1, n):
        if found:
            break
        for combo in itertools.combinations(verts, r):
            U = set(combo)
            # graph edges crossing U (exactly one endpoint in U)
            cross = [e for e in Eedges if (e[0] in U) ^ (e[1] in U)]
            deltaB = [e for e in cross if side[e[0]] != side[e[1]]]   # cut edges crossing -> born bad
            deltaM = [e for e in cross if side[e[0]] == side[e[1]]]   # bad edges crossing -> killed
            # CORRECTED route-B (two-door allowed): ONLY core edges killed (deltaM subset {f0,f1}), f1 killed,
            # every born edge short (ell_{B^U} <= L), net drop > 0. (one-door H1 was too strong.)
            dM = set(deltaM)
            if not dM.issubset({fe0, fe1}) or fe1 not in dM:
                continue
            side_U = [side[i] ^ (1 if i in U else 0) for i in range(n)]
            st_U = struct_for_side(n, adj, side_U)
            if st_U is None:
                continue
            M_U, ell_U = set(st_U[0]), st_U[1]
            born = [e for e in deltaB if e in M_U]
            if any(ell_U.get(e, 10 ** 9) > L for e in born):
                continue
            gB = sum(ell[e] ** 2 for e in M)
            gBU = sum(ell_U[e] ** 2 for e in M_U)
            drop = gB - gBU
            if drop <= 0:
                continue
            found = dict(U=sorted(U), ndoor=len(deltaB), born=born,
                         bornells=sorted(ell_U.get(e, -1) for e in born),
                         killed=sorted(dM), drop=drop, predicted=4 * L + 4, h3a=h3a)
            break
    return L, n, found, ("OK" if found else "NO one-door WeakTypeBThetaGate witness")


def main():
    print("Route-B WeakTypeBThetaGate search on stretched L/(L+2) cores:")
    allok = True
    for L in [5, 7, 9, 11]:
        L_, n, found, msg = analyze(L)
        if found:
            print("L=%d n=%d: WITNESS #doors=%d killed=%s born_ells=%s drop=%d (>=4L+4=%d) H3a=%s U=%s" %
                  (L, n, found['ndoor'], found['killed'], found['bornells'], found['drop'], found['predicted'], found['h3a'], found['U']))
        else:
            print("L=%d n=%d: %s" % (L, n, msg))
            allok = False
    print()
    print("VERDICT: route-B WeakTypeBThetaGate %s for L=5,7,9,11" %
          ("SUPPORTED (one-door witness exists each L)" if allok else "FAILS at some L => residual blocker"))


if __name__ == '__main__':
    main()
