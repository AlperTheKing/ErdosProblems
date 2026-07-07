r"""VERIFIED COUNTEREXAMPLE to NoLongSideDoorAnnulus / AnnularAtom_has_firstSplit from WEAK hypotheses (2026-07-08).

GPT-Pro's single-row long-annulus escape, exact-verified by Claude. Shows the door-only absorption lemma is FALSE
from {triangle-free, max-cut, Ferrers order, inclusion-minimal side-door interval, ell>=9} ALONE -- it needs an
ADDITIONAL CAP hypothesis (LongOwnedAtom_has_companionTheta) excluding the single-row escape.

Construction: C_18 (even cycle) as the cut graph B, parity bipartition, plus ONE bad edge h=(v0,v8).
  - triangle-free (C_18 + a chord between two even vertices at distance 8; no common neighbour).
  - parity cut is maximum (a cycle's unique all-edges-cut 2-colouring); the chord is the single bad edge.
  - ell(h) = dist_B(v0,v8)+1 = 8+1 = 9  (a level-2 atom).
  - D={v0} is a two-door (deltaB={v0v1,v0v17}), one-bad-door (deltaM={v0v8}), sigma=1, inclusion-minimal side-door
    subcage with B[D] and B[V\D] connected -- but it owns the ell=9 edge with NO companion bad row / theta, NO
    interior split door, NO triangle, NO shorter blue row. So S2's application geometry does NOT apply.
  - Demand(D) = ell(h)^2 - 25 = 81 - 25 = 56 > 25 = 25*sigma(D)  =>  DOOR-ONLY ABSORPTION FAILS.
  - beta = e - maxcut = 19 - 18 = 1 <= N^2/25 = 12.96  =>  the CONJECTURE still holds (this refutes the LEMMA, not
    the theorem; C_18 has a huge bank slack, it is NOT a tight/deficient/negative-reserve cage).

IMPLICATION: Claude's _claude_sidedoor_dooronly_gate.py "0 fail / no ell>=9 in 17757 cases" was a SEARCH-SPACE
ARTIFACT (census N<=9 + specific glue cannot host an ell>=9 single-row escape, which needs N>=18). The battery does
NOT support NoLongSideDoorAnnulus. The genuine residual is LongOwnedAtom_has_companionTheta: whether the actual
negative-reserve / deficient-cage extraction EXCLUDES single-row long annuli (needs a tight-bank / rowDB-ownership
argument, NOT battery). Run from problems/23/writeup.
"""
from _claude_sidedoor_dooronly_gate import deltas, internal_bad, conn_cut, ell_of
from _codex_k2t_switch_probe import adj_from_edges


def main():
    n = 18
    E = [(i, (i + 1) % 18) for i in range(18)] + [(0, 8)]
    adj = adj_from_edges(n, E)
    side = [i % 2 for i in range(18)]
    tri = any(b in adj[a] and c in adj[a] and c in adj[b]
              for a in range(n) for b in adj[a] for c in adj[b] if a < b < c)
    M = [(a, b) for a in range(n) for b in adj[a] if a < b and side[a] == side[b]]
    h = (0, 8)
    D = {0}
    dB, dM = deltas(n, adj, side, D)
    sigma = len(dB) - len(dM)
    owned = dM + internal_bad(adj, side, D)
    demand = sum(ell_of(adj, side, e) ** 2 - 25 for e in owned)
    cut = sum(1 for a, b in E if side[a] != side[b])
    print("C_18 + bad edge (0,8), parity cut:")
    print("  triangle-free:", not tri, "| bad edges M:", M, "| ell(0,8):", ell_of(adj, side, h))
    print("  D={0}: deltaB=%s deltaM=%s sigma=%d | B[D] conn=%s B[V\\D] conn=%s"
          % (sorted(dB), sorted(dM), sigma, conn_cut(adj, side, D), conn_cut(adj, side, set(range(n)) - D)))
    print("  ownedBad=%s Demand=%d  25*sigma=%d  DOOR-ONLY OK=%s" % (owned, demand, 25 * sigma, demand <= 25 * sigma))
    print("  cutval=%d edges=%d beta<=%d  N^2/25=%.2f  CONJECTURE holds=%s"
          % (cut, len(E), len(E) - cut, n * n / 25, (len(E) - cut) <= n * n / 25))
    ok = (not tri) and ell_of(adj, side, h) == 9 and sigma == 1 and demand == 56 and demand > 25 * sigma \
        and conn_cut(adj, side, D) and conn_cut(adj, side, set(range(n)) - D)
    print("VERDICT: %s -- NoLongSideDoorAnnulus is FALSE from weak hypotheses (single-row ell=9 escape, door-only fails);"
          " battery was a search-space artifact; residual = LongOwnedAtom_has_companionTheta (extraction must exclude this)."
          % ("CONFIRMED escape" if ok else "CHECK FAILED"))


if __name__ == '__main__':
    main()
