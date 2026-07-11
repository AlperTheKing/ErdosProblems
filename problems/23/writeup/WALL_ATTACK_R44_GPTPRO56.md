# WALL ATTACK — R44: |F*| = |A|−1 PROVED (transversal circuit); CROSSOVER TABLE — k ≥ t−1 impossible,
# k=2 needs 3t+2; SOLE SURVIVING WINDOW = (t=4, k=2) WITH SLACK EXACTLY 1 (14 ≤ 15); coverage-emptiness
# does NOT generalize (StarClosedAt shapes only); GPT P(falsifier) ~7%
# (GPT-5.6 Pro, 2026-07-12, "worked 19m0s"; harvested ~13.4k ch)

**[CLAUDE GATE HEADER — all three arithmetic pillars verified by inspection: (1) |F*| = |A|−1: proper Hall on
A∖{a} gives m−1 ≤ |∪_{b≠a}F_b| ≤ |F*| < m ⟹ equality + every deletion-union = F* ⟹ every support edge has
multiplicity ≥ 2 (an edge in only F_a would make the deletion-union m−2) + incidence connectivity (two
components would sum Hall to ≥ m); (2) the general bound kt + t ≤ |F*| (kt disjoint owner-incident by
same-side + t distinct final edges of ONE owner's bad paths; cross-owner final edges CAN fully overlap ⟹ no
stronger universal external term); (3) the k=2 improvement +2 (coverage row Q: v ∉ Q by row-intersection,
m ≤ 1 occurrence ⟹ ≥2 of Q's 4 edges non-owner-incident, distinct from terminal edges since a bad neighbour
adjacent to x or y in Q would triangle with v). Crossover: kt+t > t²−1 ⟺ k ≥ t−1; 3t+2 > t²−1 ⟺ t ≤ 3.
TABLE CONFIRMED: t=3 all dead; t=4: k=2 survives by EXACTLY 1 (14 ≤ 15), k=3 dead (16 > 15); first surviving
= (4,2). The T4 candidate structure goes to Codex as the enumeration target — the ambient restriction
(|V(F*)| ≤ 16, N=20, ≤4 outside vertices, maxcut certificate INTRINSIC) makes this decisively finite.]**

## 1. |F*| identity (exact, Lean-ready)
Inclusion-minimal support-deficient A with proper-Hall subsets ⟹ |∪F_a| = |A|−1; every deletion-union = F*;
every support edge in ≥2 atom supports; incidence graph connected; A = a transversal-matroid CIRCUIT
(deleting any atom leaves a perfect SDR onto all support edges). `minimalSupportDeficient_union_card`.
If the minimal family is proper ⊂ M: |F*| = |A|−1 (NOT |M|−1).

## 2. Classification at general t
No shape classification (17/16 bipartite K4-subdivision circuit kills series-parallel hopes). Double-star:
2t+2 = t²−1 ⟺ (t−3)(t+1) = 0 — **unique to t=3**. t=4: 16 atoms/15 edges, connected bipartite, |V| ≤ 16,
Σ|F_a| ≥ 64 ⟹ avg edge multiplicity ≥ 64/15. All-endpoints-one-shore numerically possible (Mantel: shore ≥ 8).

## 3-5. Shape-independent bounds + CROSSOVER TABLE
deg_F*(v) ≥ t per profile owner (coverage detours); same-side owners ⟹ disjoint incident sets ⟹ kt; + t
distinct final edges (one owner) ⟹ **|F*| ≥ kt + t** ⟹ k ≥ t−1 impossible (kt+t−(t²−1) = t(k+1−t)+1 > 0).
**k=2: |F*| ≥ 3t + 2** (coverage-row +2, universal). No stronger universal terms (coverage rows share outer
edges; only the final owner-incident edge my_i differs; k≥3 coverage rows can be fully owner-incident).
TABLE: t=3: k=2→11>8 dead, k=3→12>8 dead. t=4: k=2→14 ≤ 15 SURVIVES BY 1; k=3→16>15 dead. t=5: k=2 slack 7,
k=3 slack 4. t=6: slacks 15/11. Range 2 ≤ k ≤ t−2; **first surviving window = (t,k) = (4,2), slack 1.**

## 7. Coverage-emptiness does NOT generalize
K3,3 argument is shape-specific (every atom in the biclique star system). General circuits can have atoms
unrelated to hub + its bad neighbours carrying coverage rows freely; the 8-vtx rotor already realizes covered
pairs. Precise adapter condition: `StarClosedAt v : ∀ a ∈ supportFamily, a.incident v ∨ ∃ b ∈ badNeighbours v,
b ∈ a.endpoints` ⟹ emptiness. Minimal defect-one does NOT imply StarClosedAt.

## 8. THE EXACT SURVIVING WINDOW (gate target)
N=20, |M|=16, |F*|=15. Support: connected transversal circuit (deletion SDRs, multiplicity ≥2, distinct
tri-free endpoint pairs, blue distance exactly 4, support(a) = union of ALL shortest rows). Owners: v,m same
side, dB=dM=4 each, deg_I=1 in deficient states, both stars fully covered. Edge budget: 8 owner-incident +
4 terminal + 2 coverage = 14 of 15 forced; ONE free edge must complete EVERYTHING (circuit + 16 distinct
pairs + completeness + genuine maxcut on 20 vertices + coverage + the exact (2,1,0,1) ledger BOTH directions
+ equal positive globally-minimal defect). **Ambient restriction: |V(F*)| ≤ 16 ⟹ ≤ 4 vertices outside the
support graph ⟹ NO large independent locks — the maxcut certificate must be intrinsic to the 15-edge
geometry.** Lean: T4TwoOwnerRotorCandidate (fields in reply); no-hit promotes to no_t4_twoOwnerDefectOneRotor.
NOTE (mine): connected 15-edge graph on 16 vertices = a TREE (unique geodesics ⟹ F_a = unique 4-paths;
multiplicity ≥2 = every edge on ≥2 of the 16 paths; Σ = 64 slots / 15 edges); on |V| < 16, cyclomatic
16−|V| cycles. Highly enumerable.

## 9. Verdict
t=3 died because the budget was overdrawn; at (4,2) it is not — but one edge of slack must satisfy six
simultaneous global constraints. **P(falsifier) ≈ 7%.** If (4,2) is empty: next windows t=5 k∈{2,3} (more
slack — different argument needed). The exact surviving question: "Can the one remaining support edge at
(t,k)=(4,2) complete all of the circuit, coverage, and neutral-ledger constraints?"
