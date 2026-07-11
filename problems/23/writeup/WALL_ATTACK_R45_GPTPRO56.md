# WALL ATTACK — R45: (t,k)=(4,2) WINDOW CLOSED (|V|=16 tree / |V|=15 unicyclic symbolic kills +
# |V|<=14 exact finite catalogue); tight 14-vtx regression circuit exhibited; GPT P(falsifier) ~4%;
# next scalar windows (5,2)/(5,3)
# (GPT-5.6 Pro, 2026-07-12, "worked 28m34s"; harvested ~10.4k ch)

**[CLAUDE GATE HEADER — READ WITH TWO OVERLAYS: (1) AMBIENT CORRECTION (Codex, accepted): R44/R45's
"ambient <= 4 / intrinsic maxcut" was REVERSED (N=20 minus |V(F*)| <= 16 gives >= 4 outside, >= 5 after the
tree-kill) — R45's closure does NOT rely on it (the catalogue argument is support-internal: F* contains ALL
rows by definition), verified. (2) CONVERGENCE: Codex independently closed t=4 the same hour by a THIRD
route — the r-INDEPENDENT raw-middle-swap exclusion (zero row pairs (a,x,m,y,b)/(a,x,v,y,b) in any complete
family of any of the 576 census circuits; my replay PASS, SHA b464682b; my Scope-A objection [their first
run filtered by r=4] was confirmed and the retraction/rerun preserved rigor) + the production adapter
LiveMiddleSwapCrossOuter (3DFF7897, [propext,Quot.sound]) + graph-only cross-outer exhaustion (79db75b9,
total 0; my replay PASS). GPT's |V|=15/16 symbolic kills verified by inspection (tree cannot contain the
forced square; unicyclic: each covered star pair {x0,y_i} forces a SECOND 2-path x0−q−y_i giving a distinct
4-cycle through v, deg(v)=4 forces >= 2 new cycles vs the single available). GPT's |V|<=14 catalogue is its
OWN enumeration — cross-covered by Codex's independent census finding circuits ONLY at n=15 (0 at n<=14),
consistent at every |V|. THREE independent closures of t=4 total. t=5 UNROOTED CENSUS INFEASIBLE (Codex
measured geng 24-edge counts: n16 already 194.6M @ 62s) — R46 must use rooted generation or a structural
lemma.]**

## 1-2. Identity + coincidence stack
|F*| = |A|−1 re-derived (general; transversal circuit). Coincidence budget: |E_v ∪ E_m ∪ T_v ∪ T_m ∪ C_v ∪
C_m| = 20 − s − a − b − d ≤ 15 ⟹ s+a+b+d ≥ 5 (s = shared tails ≥ 1 recovers the compiled K_{2,3} core;
sharp table per s). Count alone CANNOT close (coverage rows reuse externals) ⟹ classification necessary.

## 3. Exact distance-4 counter
For u,v ∈ L: d_H(u,v) = 4 ⟺ (Q_L)_{uv} = 0 < (Q_L²)_{uv}, Q_L = A_H A_Hᵀ. Exact checker formula (8); the
degree-weighted bound (9) is looser and unused.

## 4. Symbolic kills
|V|=16: tree ⟹ no forced square v−x−m−y. |V|=15: unicyclic ⟹ unique cycle = the square; full coverage at v
(deg 4, active x0) forces per covered pair {x0,y_i} a second path x0−q−y_i ⟹ a 4-cycle; ≥2 new cycles ⟹
contradiction. (Verified by inspection.)

## 5-6. Finite catalogue (10 ≤ |V| ≤ 14) + the tight regression circuit
|V|=10,11: no owner distance-4 profile. |V|=12: max total same-shore distance-4 pairs = 10 < 16. |V|=13:
280 normalized graphs with ≥16 pairs; ZERO admit a 16/15 circuit with four owner-star atoms each. |V|=14:
455 graphs; ZERO admit fully covered stars at both owners even with the full row DB available. **Tight
14-vtx regression circuit** (survives all EXCEPT coverage): bipartition {0..6}⊔{7..13}, 15 edges (13),
16 atoms (14), 864 tuples, 0 covered-star tuples; owners 0,1 share blue nbrs {7,8} + bad nbrs {3,5,6};
shared terminals 3-13,5-13,6-13; budget exhausted by 2-11, 4-9; coverage fails locally ({7,8} in no
shortest row; other rows contain the owner ⟹ absorb the active edge). Checker SHA 4644e5ab.

## 7-8. Compile shells + the t=4 theorem
`t4_supportCircuit_no_twoFullyCoveredStars` (split: 16 tree / 15 unicyclic / ≤14 catalogue) consumed by
`no_t4_twoOwnerDefectOneRotor` (minimal ⟹ |F*|=15; covered-star detours ⟹ owner stars ⊆ F*; square ⟹
common nbrs; bad stars ⟹ distance-4 atoms; apply). Formalization debt: kernel-replay of the ≤14 catalogue.
Coverage-emptiness stays size-specific (8-vtx rotor has covered pairs).

## Verdict
(t,k)=(4,2) CLOSED (three independent routes with Codex's). Next scalar windows: (5,2) slack 24−17=7,
(5,3) slack 24−20=4. **P(falsifier) ≈ 4%.**
