# Erdős #23 Step-1 (a(30)≤36) — authoritative status, 2026-06-24 (Claude)

Single honest reference for the (multi-session) Step-1 effort. a(30)=36 is almost surely TRUE
(a(30)≥36 by C5[6]; ZERO β≥37 witness across all computation). a(30)≤36 is the UNPROVEN hard
direction. EVERYTHING below is conditional on BCL Thm 1.3 (cited; same dependency throughout).

## Architecture
Counterexample G (tri-free, 30 vtx, β≥37) ⇒ edge window 112≤e≤143 (blow-up+BCL, PROVEN). Root at a
MINIMUM nonedge-codegree pair ⇒ branches by δ₂=min nonedge-codegree ∈{1,2,3} (δ₂≥4 ⇒ hom-C5, done).
Within each branch, min-degree r: r≤3 closed; r=4..7 must give δ(G)≥8; r0∈{8,9} = the manifold enum.

## VERIFIED CLOSED (this session, sound modulo BCL)
- **q10** (t=2 manifold idx53-97): 2,767,528 tasks all INFEASIBLE, finalized, 0 FEASIBLE.
- **Min-degree (δ≥8 sub-cases):** δ₂=2/r4 (β≤25, search23/verify_min_degree_cuts.py); δ₂=3/r6 (β≤33,
  clean, 0 adversarial breaks); δ₂=3/r4,5 VACUOUS (K_{r,30-r}, β=0). [δ₂=2/r5 (β≤35) & δ₂=1/r5 (β≤25)
  CLOSED-with-caveat: need exact-ILP, not hill-climb, for Lean-grade.]
- **idx100** (q11, (0,2,2,7), a6b9): 36/36 INFEASIBLE (26 state-count + 10 by the sound second-shadow
  quotient on the band-top tail that timed out the 889-state CP-SAT). Certificate: k2_idx100_bandtop_quotient_certificate.md

## TOOLS BUILT (sound, verified)
- **Second-shadow quotient** (search23/second_shadow_quotient.py, ...full.py): GPT section-(c) engine,
  O(q²) vars. Cuts all PROVEN sound: col-imbalance (40) [re-derived: 70=2·37−4], WBCL max-degree
  Δ≤11@e=143 [blow-up+BCL, d≥13 margin], degree-histograms + v_rjk consistency, 2nd-moments, codegree,
  p+e_R≥37 & M+2e_R≥70 (trivial bipartition cuts β≤p+e_R, β≤p+U+e_R+4).
- SCOPE (honest): closes band-top cells for FAVORABLE A/B splits (idx100 a6b9: d(y)=11 hits the WBCL cap
  ⇒ tight) but NOT unfavorable (idx101 a7b8: no vertex at cap ⇒ relaxation feasible). ~73% of band-top.

## OPEN OBSTRUCTIONS (genuine, mostly research-grade — NOT just engineering)
1. **General high-p band-top** (idx101-type, e=143, p≈33-36, β≥37): this is the EXTREMAL case (β just
   above 36=30²/25). Quotient feasible; state-count timed out on idx100's (diagnostic running for
   idx101). Closing it ≈ proving the conjecture sharply at the extremal point — research-grade.
2. **Big grids** (idx270 ~5e8 tasks, idx232/233 ~2e8, idx254 ~3e8): brute-infeasible; need GPT
   section-(b) canonical-augmentation skeleton reduction (E+D core+attachment; E+S1+S2 compatible
   blocks; pure S1+S2 Gale-Ryser degree-partitions). NOT built.
3. **(C)/(D) uncovered branches**: the 387-manifold is δ₂=2 (t=2) ONLY. δ₂=1 (t=1) & δ₂=3 (t=3) main
   enumerations (r0≥8) have NO manifold built (q=15 work was t=3, conditional/retracted).
4. **δ₂=1/r=7** min-degree sub-case: empirical β-ceiling ~18 (value fine) but ≈ open BCL medium-density
   extremal — proof research-grade.
5. **Soundness items**: H14 anti-tightness over-cut is default-ON in state_count_6195_cpsat.py (all
   closure launchers pass --disable-anti-tightness, so recorded closures sound, but the default is a
   latent footgun); WYZ δ₂≥4⇒C5 applied at finite n=30 not independently re-audited; no single
   manifest-wide zero-UNKNOWN union certificate.

## Prioritized next steps (fastest sound path)
A. Band-top: await GPT's class-weight separator (a.6) / extremal cut for the unfavorable high-p case;
   verify sound (false-closure discipline); if it works, the band-top closes ⇒ engine+state-count sweep
   the t=2 frontier.
B. Big grids: implement section-(b) canonical reductions (collapses 5e8→tractable).
C. (C)/(D): generate t=1/t=3 manifolds (the engine generalizes); enumerate.
D. δ₂=1/r=7 + r=4,6: GPT cut or accept research-grade.
E. Distill to a re-runnable union certificate; fix anti-tightness default; audit WYZ-at-n=30.

BOTTOM LINE: sound reduction skeleton + verified partial closures; full Step-1 has ≥2 research-grade
cores (extremal band-top #1, δ₂=1/r=7 #4) plus large builds (#2,#3). Multi-session. No fabrication:
"a(30)≤36 not yet proven; a(30)=36 almost surely true."
