# Q15 (STRATEGY) — GPT recommendation + Step-2 AUDIT (2026-06-20)

Chat "Erdos 23 Step 2" `c/6a36e5af-e228-83ed-b148-e30d7246891d`, Kapsamlı Pro. User-directed: τ_K route
exhausted ⟹ ask GPT how to proceed and follow it. **GPT gave a concrete, high-quality strategic pivot.**

## GPT's recommendation (verbatim-faithful)
**STOP treating CF/τ_K as the target** — the 16-state Clebsch surrogate is now a liability; direct β has
only 2 states and an exact cut-cone formulation. **Route = max-cut-colored flags + macroscopic switching,
with C5-defect stability as cleanup.** Ranking: `max-cut-colored flags + macroscopic switching > C5-defect
stability cleanup > peeling > fixed 2-opt`. Precedent: arXiv 2605.05346 (May 2026, K_4-free balanced
bipartite distance) — smallest counterexample + global vertex coloring + blow-up graphons + rooted
randomized partition inequalities in a 2-vertex-colored flag algebra (closest methodological analogue).

### Switching Lemma (the new exact tool)
Let A⊔B be a maximum cut; M=E(G[A])∪E(G[B]) (monochromatic, |M|=β), C=E(A,B). EQUIVALENT:
(1) A⊔B is a max cut; (2) ∀S⊆V: **|M∩δ(S)| ≤ |C∩δ(S)|** (SW0); (3) ∀p∈[0,1]^V:
**Σ_{uv∈M}(p_u+p_v−2p_up_v) ≤ Σ_{uv∈C}(p_u+p_v−2p_up_v)** (SW). Proof: flipping side of S toggles δ(S);
monochromatic count changes by |C∩δ(S)|−|M∩δ(S)|≥0 ⟺ global opt. (2)⟹(3): random S with P(v∈S)=p_v,
P(uv∈δ(S))=p_u+p_v−2p_up_v, take E. (3)⟹(2): p_v=1_{v∈S}. Corollary (L1): for every L1-metric d,
Σ_M d(u,v) ≤ Σ_C d(u,v) (L1-metrics = integrals of cut metrics).
**Flag-compatible:** p_v a prescribed function of (max-cut color of v, adjacency to k bounded roots) ⟹ SW is
a linear inequality in 2-colored flags of order k+2. Roots bounded but switched set Θ(N) ⟹ retains
quadratic-scale info (the key distinction from fixed k-opt).
**Explicit audit-check (SW1):** for v∈A, P=N(v)∩A, Q=N(v)∩B, R=A∖(P∪{v}), T=B∖Q, switching P∪T and using
e(P,Q)=0 (triangle-free): **|P| + e(P,R) + e(Q,T) ≤ e(R,T)** — must hold for every root of every max-cut-
colored triangle-free graph.

### C5-defect stability (cleanup)
d_5(G)=min over ψ:V→Z5 of #{uv∈E: ψ(u)−ψ(v)≢±1 mod 5}. Then **β(G) ≤ (e+4 d_5)/5** (delete the d_5 defective
edges ⟹ 5 consecutive block-pairs; delete the smallest of the 5 sets, ≤(e−d_5)/5 ⟹ bipartite block-support).
⟹ band theorem if **d_5(G) ≤ (N²/5−e)/4** (C5-target). Tolerance d_5/N²: 0.0100 at x=0.16, 0.0189 at
x=0.1243. So stability need only force a 1–2% edge-distance to C5-support (conditional on β>N²/25), NOT
literal proximity to a complete balanced blow-up.

### Program
Fix max cut → 2 colors; objective |E(A)|+|E(B)|. Run a 2-colored triangle-free flag SDP with: edge-density
band; PSD flag constraints; all 1- and 2-root SW instances; selected 3-root via a separation oracle. Ask
β/N²≤1/25 directly (extremal C5[n] is at x=0.2, OUTSIDE the band, so no equality case to reproduce here). If
it stalls, refine colors by max-cut margin h(v)=d_C(v)−d_M(v)≥0 or degree buckets; target C5-target as
stability. Audited blow-up transfer ⟹ an asymptotic colored-graphon certificate suffices.
**Main risk:** the colored switching hierarchy may have low-order pseudo-graphons satisfying every few-root
switch yet violating the bound; required root order/#colors could become large.

## Step-2 AUDIT (computational) — `verify_q15_audit.py` (2026-06-20T23:05) — ALL VERIFIED
- **(A) SW1** `|P|+e(P,R)+e(Q,T) ≤ e(R,T)` at every root of a MAX cut: **0 violations** on all tested
  (C5[n], M(M(C5)), K_8,32, K_16,64, random in-band). The switching tool is sound.
- **(B) β ≤ (e+4d_5)/5** (the C5-cleanup, UNCONDITIONAL): holds on all; **tight at C5[n]** (β=4=(20)/5 for
  C5[2], β=9 for C5[3]).
- **(C) d_5 ≤ (N²/5−e)/4 — held on the small sample but is FALSE in general (broader census).** `census_d5.py`
  (geng N=10..13, ~6k graphs at N=10): **max d_5/target = 2.0**, witness N=10 e=16 x=0.16 (band top), d_5=2 >
  target=1. That graph has EXACT β=3 ≤ 4=n² (conjecture HOLDS), but the C5-cleanup gives only β≤(e+4d_5)/5=4.8
  ≰ 4. **⟹ the C5-cleanup FALLBACK is INSUFFICIENT as a standalone route** — too lossy near the band top x=0.16
  (the same wall). It is only a *conditional* stability tool (GPT noted "conditional on β>N²/25"), and the needed
  unconditional d_5-bound is false.
- **NET:** GPT's MAIN route — the max-cut-colored switching flag-SDP for β directly — is INTACT (SW1 verified
  0 violations; materially stronger than the uncolored coverage SDP ruled out in Q12; K_4-free precedent
  arXiv:2605.05346). It needs a real 2-colored triangle-free flag-algebra SDP (flagmatic/CSDP) — research-grade
  tooling beyond this session. The C5-cleanup cannot shortcut it. Step 2 still UNPROVEN.

## Assessment + plan
SOUND and the most promising route offered: it (a) encodes the genuinely GLOBAL obstruction exactly (the
switching lemma is the standard local-max-cut optimality, fractionalized + flag-lifted), (b) drops from 16
to 2 states, (c) has a small falsifiable first implementation (SW1), and (d) the C5-cleanup reduces the
"hard core" to a cleaner C5-frustration target d_5≤(N²/5−e)/4. Executing: (1) machine-check SW1 + β≤(e+4d_5)/5
+ test d_5 vs target on band graphs/Mycielskians/C5[n]; (2) if d_5≤target holds in-band ⟹ the C5-cleanup may
be a SHORTER route than the full switching SDP — a fresh narrow GPT question on "prove d_5≤(N²/5−e)/4". CF/
Step 2 still UNPROVEN.
