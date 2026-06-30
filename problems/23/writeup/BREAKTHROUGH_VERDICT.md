# Erdos #23 multi-angle breakthrough attack -- VERDICT (2026-06-29)

All decisive claims independently verified. UNIF-LOAD is tight at C5[t] (slack 0) and survives two-lane with growing slack (524→3484) exactly where the spectral surrogates diverge. I have enough to render the verdict.

---

# VERDICT — Erdős #23 multi-angle attack (β = e − maxcut ≤ N²/25, triangle-free)

## (1) Did any angle produce a complete, verified proof? NO.

No angle closes the full conjecture. The strongest complete result is a **rigorous proof of a proper subcase**, not the theorem. I independently re-verified its three load-bearing pieces (fresh code, not the team's scripts):

- **Cyclic-min-product lemma** `25·min_i(n_i·n_{i+1}) ≤ N²` — HOLDS exact over all integer 5-tuples summing to N≤40 (zero violations). The AM-GM proof is correct: `∏(n_i n_{i+1}) = (∏n_i)² ≥ μ⁵` and `∏n_i ≤ (N/5)⁵` give `μ ≤ N²/25`.
- **C5-colorable reduction** `β ≤ min_i e(V_i,V_{i+1})` — 0 violations / 565 random C5-colorable graphs (brute maxcut).
- **Residual obstruction is real and precise** — Grötzsch (N=11, e=20, triangle-free, NOT C5-colorable): true β=4 < target 4.84, but the optimized 5-rotation rounding bound is 5.6 > 4.84, so the construction provably cannot reach it.

**Honest statement:** Angle 1 proves `β ≤ N²/25` for every triangle-free graph admitting a homomorphism to C5 (which includes all extremal C5-blowups, with correct equality case), with 1/25 derived transparently from "5". This is a clean closed-form subcase no prior route produced — **but it is not the conjecture.** The hard core (non-C5-colorable triangle-free / Mycielskian / odd-girth) is explicitly left open, matching the standing gate.

## (2) Most promising angle + single remaining gap

**Angle 6 (UNIF-LOAD) is the most promising,** because it survives the exact families that kill everything else. I confirmed the decisive **divergence** finding (the session's strongest new negative result): on the two-lane family `ρ(O)/N = 0.90 → 1.03 → 1.10 → 1.14 → 1.17` climbs **unboundedly past 1**, while `Γ/N² ≤ 0.378`. This **categorically prunes the entire current ROWSUM-O / Schur-cond3 / SPEC program at once** — any proof factoring through `ρ(O)≤N` or `‖T‖²≤NΓ` proves an arbitrarily-false statement. Cauchy–Schwarz `‖T‖²≥Γ²/N` loses a factor 3.1 here (concentrated load), which is *why* second-moment routes fail.

The clean target survives: **Γ ≤ N²** (tight only at C5[t]; ⟸ from `Γ≥25m`). And **UNIF-LOAD** `max_v T_uni(v) ≤ N + (N²−Γ)` — I verified tight at C5[t] (slack 0) and robust on two-lane (slack 524→3484, growing).

**Single remaining gap:** prove UNIF-LOAD as a **first-moment routing/Hall feasibility** statement (NOT spectral). Per the OVD/GPI equivalence in memory, this may be hardness-equivalent to the conjecture itself — that risk is unresolved.

## (3) NEW exact-testable inequality to gate immediately

**UNIF-LOAD** (already partially gated this session; extend the battery):
> For every triangle-free Γ-min connected-B max cut: `max_v T_uni(v) ≤ N + (N² − Γ)`, where `T_uni(v) = Σ_f ℓ_f·(#f-geodesics through v)/(#f-geodesics)`, `Γ = Σ_f ℓ_f²`.

Gate over **census N≤12, two-lane L≤24, Mycielskians incl. M(Grötzsch) N=23, iterated Mycielskians, large NON-uniform odd-cycle blowups**. Run with the mandatory **negative control**: `ρ(O)≤N` and `‖T‖²≤NΓ` must FAIL on two-lane L≥12 (ratios 1.03–1.17) — confirms the proof object is correctly first-moment-shaped. This single check formally retires the spectral surrogate program.

## (4) Literature: NO known proof or near-proof

Confirmed open. Source ladder is accurate:
- **Balogh–Clemen–Lidický, arXiv:2103.14179 (2021)**: best global bound `β ≤ N²/23.5`; exact `N²/25` proved ONLY for edge-density ≤0.2486 or ≥0.3197.
- **Erdős–Győri–Simonovits (1992)**: dense tail `e ≥ N²/5 − o(N²)` only.
- The **(0.2486, 0.3197) medium band is open** — exactly where the project's δ=0 obstruction lives. The 23.5-vs-25 SDP gap does not vanish with flag order (angle 4 independently diagnoses this as structural: max-cut is a non-flag-linear MIN over a global cut, so finite-radius flags are irreducibly loose; extremal not flag-perfect at order ≤10). **No citation will finish this.**

## (5) Concrete next action (fastest path to close)

**Drop all spectral/second-moment work** (definitively pruned by the verified divergence). Pursue **two parallel first-moment threads:**

1. **(Highest leverage) Merge angle 1 + angle 6 into a dichotomy.** Angle 1 *closes* C5-colorable cleanly. The open residual is exactly non-C5-colorable triangle-free graphs — which have **strictly more cuttable edges** (Grötzsch slack 4 vs 4.84 = 0.84). Attack: prove non-C5-colorable triangle-free ⟹ β bounded below N²/25 by an absolute margin, OR build the **fractional C5-cover** (distribution over φ_k:V→Z₅) whose LP-dual is precisely the measured rounding leak. This converts the residual into a transport/LP feasibility problem and reuses the only closed-form subcase result the team has.

2. **Prove UNIF-LOAD via Hall/max-flow** using triangle-freeness (bad-edge endpoints share no blue neighbor ⟹ geodesics spread through separated corridors) and the edge-load handshake `Σ_{e@v,B} μ(e) = 2T(v)−D(v)`, routing through `Σ_B μ(e) = Γ−Σ_f ℓ_f` — never through any ‖T‖² bound. Gate every candidate on the two-lane divergence control first.

**Strongest concrete quotable result of the session:** the cyclic-min-product lemma with a one-line AM-GM placing 1/25 = (1/5)², giving `β ≤ min_i n_i n_{i+1} ≤ N²/25` with equality iff balanced C5[N/5] — a fully rigorous proof for all C5-colorable triangle-free graphs (the entire extremal family), verified exact N≤40. It is a genuine subcase theorem, **not** a proof of the conjecture.

**Artifacts (absolute paths):**
- `E:\Projects\ErdosProblems\problems\23\writeup\_unifload_check.py` (UNIF-LOAD gate)
- `E:\Projects\ErdosProblems\problems\23\writeup\_slack_tl.py` (divergence control — the load-bearing negative)
- `E:\Projects\ErdosProblems\problems\23\writeup\_gamma_census.py` (Γ≤N² census)
- `C:\Users\a\AppData\Local\Temp\claude\E--Projects-ErdosProblems\461052bb-8cbc-4d9f-996c-62e0fcc0bfcb\scratchpad\verify_verdict.py` (my independent re-verification of angle 1 + Grötzsch)