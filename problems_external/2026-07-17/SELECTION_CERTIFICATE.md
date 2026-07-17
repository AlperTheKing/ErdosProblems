# External Open-Problem Selection Certificate — 2026-07-17

Deadline: 2026-07-18T21:57:27+03:00. Scope: currently open, non-Erdős, exact problems with a direct one-day closure route.

## Decision

**Selected:** Written on the Wall II / Graffiti.pc Conjecture 143 (2005).

For a finite connected non-tree graph G, let t(G) be the largest order of an induced tree, g(G) its girth, and δ′(G) the second-smallest degree with multiplicity. Prove

t(G) ≥ (g(G)+1)/δ′(G).

The current Douglas West Graffiti.pc register still presents this exact statement as Conjecture 143, and the June 2026 Formal Conjectures snapshot marks it research-open. Two independent red-team passes found the same complete case split and no counterexample or indexed resolution. It dominates the runners-up because its frontier lemma has an elementary global proof rather than a low-probability finite search.

## Audited portfolio

| Candidate | Exact closing certificate | One-day assessment | Decision |
|---|---|---:|---|
| WOWII Conjecture 143 | Global proof via the two-leaf induced-tree lemma | >90% mathematical closure; novelty gate remains | SELECT |
| Queen domination γ(Q26) | SAT model for 13 queens or LRAT UNSAT plus known 14-witness | 10–20% | RUNNER-UP |
| Unknotting number u(10_100) | Two crossing changes plus published g4=2 lower bound | 10–15% | RUNNER-UP |
| Superpermutation L(6) | PB/LRAT exclusion through length 871 plus 872 witness | 3–5%; 2021 priority claim | QUARANTINE |
| Conway 99-graph | 84-vertex exact SAT witness or DRAT UNSAT | 4–8% | REJECT for one day |
| Hadamard order 668 | Four length-167 complementary sign sequences | 1–3% | REJECT for one day |
| Costas array order 32 | One 32-permutation difference certificate | 0.5–2% | REJECT for one day |
| Magic square of nine squares | One positive distinct-square 3×3 magic square | unresolved 2026 proof claim | QUARANTINE |
| Maximal determinant D(23), Tammes N=15, Golomb G(29), 3 MOLS(10) | Global optimality certificates | no bounded one-day certificate | REJECT |

## Selected direct certificate

Frontier lemma L: every finite connected cyclic graph of girth g with at least two degree-one vertices has an induced tree on at least g+1 vertices.

Bridge:

1. If δ′≥2, a shortest cycle is induced; deleting one cycle vertex gives t≥g−1, and (g−1)δ′≥2(g−1)≥g+1.
2. If δ′=1, at least two leaves exist and L gives t≥g+1.
3. These cases give tδ′≥g+1, equivalent to Conjecture 143.

First falsifiable action: exhaustively test every connected unlabeled graph on at most seven vertices, computing girth, δ′, and exact maximum induced-tree order. Then referee the maximal-induced-tree proof of L.

Exit: any counterexample kills the route; a prior full resolution kills novelty; failure to justify L kills the proof. No surrogate bound or restricted graph family may replace the theorem.

## Current sources

- Douglas B. West, Some Conjectures of Graffiti.pc: https://dwest.web.illinois.edu/regs/graffiti.html
- Formal Conjectures, GraphConjecture143 (June 2026 snapshot): https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/WrittenOnTheWallII/GraphConjecture143.lean
- Weakley, domination of queens graphs (2022): https://www.combinatorics.org/ojs/index.php/eljc/article/view/v29i2p50
- Applebaum et al., unknotting-number gaps (2025): https://doi.org/10.1080/10586458.2025.2542174
- Cesarz–Woldar, Conway's 99-graph restrictions (2025): https://doi.org/10.5802/alco.418
- Eliahou, 64-modular Hadamard matrix of order 668 (2025): https://hal.science/hal-05393934
