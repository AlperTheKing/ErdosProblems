# WALL ATTACK — R43: t=3/N=15/|M|=9 WINDOW CLOSED (k=2 and k=3 both die by support-edge incidence);
# reservation-starvation FALSE (half 1 always pays — bounce self-feeds wherever geometry permits);
# next window t>=4 (|F*| = t^2-1 escapes the 8-edge obstruction); GPT P(falsifier) ~8%
# (GPT-5.6 Pro, 2026-07-12, "worked 13m3s"; harvested ~13.5k ch)

**[CLAUDE GATE HEADER — the two counting proofs are VERIFIED BY INSPECTION: (k=2) fully-covered live star at
profile owner forces deg_F*(v) ≥ 3 (detour rows put vx, vy0, vy1 into the complete support union F*); v,m
same side + common blue nbr ⟹ vm ∉ B (same side) and vm ∉ M (else triangle vxm) ⟹ incident support-edge sets
disjoint ⟹ 6 incident; the three distance-4 bad endpoints of v force 3 MORE edges avoiding both v,m (case 1:
some path avoids m ⟹ its last 3 edges external; case 2: every path v−p−m−q−b_i has distinct final edges qb_i
external, m only at position 2 [position 4 ⟹ vm bad ⟹ triangle]) ⟹ |E(F*)| ≥ 3+3+3 = 9 > 8 = the 9/8 circuit.
(k=3) three same-side owners, pairwise disjoint incident sets, deg ≥ 3 each ⟹ ≥ 9 > 8. Both SOUND. The
reservation verdict against my starvation idea is also sound: edge-exclusive reservation marks ONLY half 0 of
the re-activation orientation; (m,x,1) stays unreserved and sameFirst-eligible — exactly one payer, exactly
the (2,1,0,1) ledger. Compile lane: 4 lemmas + no_t3_balancedDeficiencyRotor (full skeleton given).]**

## 1-2. The k=2 exclusion (exact)
Profile owner v (dB=dM=3, deg_I=1, fully covered star {x,y0,y1}): coverage ⟹ detour rows containing vx, vy0,
vy1 ⟹ **deg_F*(v) ≥ 3** where F* = union of COMPLETE shortest-row supports of the nine atoms (|E(F*)| = 8 by
the 9/8 circuit). Same at m. Square x−m−y−v−x ⟹ v,m same side, common blue nbrs ⟹ vm ∉ B ∪ M (triangle) ⟹
disjoint incident sets ⟹ |E₀| = 8 − 3 − 3 ≤ 2 for edges avoiding both. But v's three bad neighbours b_i each
need a 4-path v→b_i inside F*: some path avoids m ⟹ 3 external edges; or all pass m at position 2 (v−p−m−q−b_i)
⟹ the three distinct final edges q·b_i are external ⟹ |E₀| ≥ 3. CONTRADICTION (9 ≤ 8). K3,3-hub placements:
opposite parts ⟹ vm bad ⟹ triangle with common nbr; same part ⟹ killed by the count above.

## 4. Reservation-starvation FALSE (my R43(2) idea dies)
Removed edge mx with p_ω(mx)=1 ⟹ n_ω(m,x)=1 → 0; if mx becomes m's unique active edge, keys (m,x,0),(m,x,1)
appear; edge-exclusive reservation marks ONLY (m,x,0) (the active orientation); **(m,x,1) is unreserved and
sameFirst-eligible for owner m — exactly ONE payer ⟹ the (2,1,0,1) neutral ledger is numerically realizable
wherever geometry permits.** No "payer always blocked" lemma exists. Compile shape:
reactivationEdge_frees_unreserved_halfOne.

## 5-6. k=3 exclusion + the t=3 closure theorem
Three rotating owners: same side by transitivity around the cycle (old/new middles share sides) ⟹ pairwise
disjoint incident support sets ⟹ Σ deg ≥ 9 > 8. **no_t3_balancedDeficiencyRotor** (full Lean skeleton:
k ∈ [2,3] by 3k ≤ |M| + nontrivial-cycle; interval_cases; the two lemmas + omega). Compile-ready:
fullyCoveredLiveStar_fullSupportDegree_ge_three, twoRotatingOwners_force_nine_supportEdges,
threeRotatingOwners_force_nine_supportEdges, no_t3_balancedDeficiencyRotor.

## 7. Scope + P
Closes ONLY the smallest window. At t ≥ 4 (N=20, |M|=16, |F*| = t²−1 = 15): 2t incident + t externals = 3t =
12 ≤ 15 — the direct obstruction fails; the self-feeding mechanism remains viable in principle. Evidence
stack: N≤12 zero; N=78 collapse; k=4 fully-active dead; t=3 k=2/k=3 dead. **P(falsifier) ≈ 8%.** Next: t=4
window search + generalize the incidence counting (complete-family union mass vs t²−1) to find the crossover.
