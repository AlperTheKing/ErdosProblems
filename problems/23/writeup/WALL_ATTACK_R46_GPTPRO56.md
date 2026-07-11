# WALL ATTACK — R46: NO ALL-t CYCLE-SPACE CLOSURE (k=2 gives only μ ≥ t−1; K_{2,t} shares cycles);
# t=5 RANGE [14,21]; COINCIDENCE BUDGET VACUOUS AT t=5; 18-VTX NEAR-CANDIDATE (fails only on 30 atom
# triangles); ROOTED-GENERATION SPEC COMPLETE; P ~6% — THEN SAME-HOUR ENGINE EVENTS SUPERSEDE (see overlay)
# (GPT-5.6 Pro, 2026-07-12, "worked 20m32s"; harvested ~14.2k ch)

**[CLAUDE GATE HEADER + ENGINE OVERLAY — TWO CODEX RESULTS LANDED THE SAME HOUR AND MOVE THE FRONTIER PAST
THIS REPLY: (1) the CP-SAT rooted harness found a PATH-REALIZABLE t=5 25/24 circuit with TRIANGLE-FREE
selected bad graph (18 support vtx, L10/R8, 29 available atoms/25 selected, multiplicity ≥3, all 25
deletion-SDRs, live swap present; graph6 Q???????F?Y?E{d?KOE??B?B???; my replay queue) — GPT's closing
question "can the 25 atoms be chosen triangle-free?" is answered YES at the support level, and the proposed
no_t5_triangleFree_twoOwnerCoveredCircuit is FALSIFIED AS STATED (pending my fully-covered-profile check on
the hit); (2) the SAME candidate dies at MAXCUT-vs-ROW-PRESERVATION: all 8 ambient shore-splits exactly
UNSAT (the decisive switch family crosses 24 bads but only 3 support edges ⟹ needs 21 new blue crossings,
each creating forbidden new shortest rows; CaDiCaL-verified, 468-1054 vars). One-candidate exclusion, not
general t5. THE NEW WALL = the maxcut/row-preservation tension. R47 targets it.]**

## 1-3. Cycle-space verdict
Per-owner: t−1 independent 4-cycles (vy_i-uniqueness) ⟹ μ(F*) ≥ t−1; H−v connected. Compile-ready
fullyCoveredOwner_cycleRank_ge. Multi-owner EXACT: μ(H) = μ(H−O) + kt − k + 1 − c (c = components of H−O,
each adjacent to ≥2 owners ⟹ 2c ≤ kt) ⟹ μ ≥ ⌈kt/2⌉ − k + 1. **k=2 gives only t−1** (K_{2,t} realizes it —
owners can share the ENTIRE cycle system); 2t−3 needs c ≤ 2, not derivable. Crossover vs demand (≥ 2t+2,
full sharing): t²−3t−1 < 0 ⟺ t=3 only. NO all-t closure by these tools; t=4 genuinely needed its catalogue.

## 4-7. t=5 exact range + vacuous budget
Cycle rank kills |V| ∈ [22,25] (k=2) and ≥20 (k=3). Mantel (25 bads, tri-free per shore): |V| ≥ 14, at 14
only shore split (9,5). **k=2: 14 ≤ |V| ≤ 21; k=3: 14 ≤ |V| ≤ 19.** Coincidence budget generalizes to
s+a+b+d ≥ 4t+5−t²: = 5 at t=4 (the closure), = 0 at t=5 — VACUOUS. Distance-4 supply: exact Q-matrix
formula (codegree-dependent; no degree-sequence-only bound).

## 8. The 18-vtx near-candidate (GPT's)
L = {v,m,a,b0..b4}, R = {x0..x4,y0..y4}; 24 edges: v,m → all x_i; a → x0..x3; a → y_j; b_j → y_j. 25
distance-4 atoms: vb_j, mb_j, b_ib_j, x4y_j. Minimal 25/24 circuit ✓; covered stars in BOTH orientations
via (x4, m|v, x_i, a, y_j) ✓. **FAILS: atom graph has K5 on {b_j} + 20 owner triangles = 30 triangles.**
Proves: cycle space + budget + supply + circuit + covered rows DO NOT suffice. (Superseded by Codex's
triangle-free hit — the tension moves to maxcut.)

## 9. Rooted t=5 generation spec (adopted by the engine, already live)
k=2 root: orders 14-21, owners deg 5, canonical |N(v)∩N(m)| = c ∈ [2,5], active nbr + coverage witnesses,
10 rooted bad endpoints + canonical support paths, complete to 24 edges; 9 pruning invariants (component
incidence, cycle rank, Mantel residual, incremental D4 bound, multiplicity, Hall/SDR feasibility,
covered-row feasibility, atom triangle-freeness, complete-row closure). k=3: ≤4 free edges ⟹ directly
feasible. Estimates: k=2 ~9.5e9 crude labelled (needs canonical augmentation), k=3 ~2.9e6.

## 10. Verdict + P
No uniform reduction; proposed size-specific lemma no_t5_triangleFree_twoOwnerCoveredCircuit — **FALSIFIED
AS STATED by the engine's hit within the hour** (must gain the maxcut/ambient hypothesis). GPT P ≈ 6%
(near-candidate proximity). ENGINE FIRST-VIOLATED-INVARIANT (candidate #1): maxcut domination vs
complete-row preservation (21-crossing switch demand vs forbidden new rows). R47 = formalize THAT tension.
