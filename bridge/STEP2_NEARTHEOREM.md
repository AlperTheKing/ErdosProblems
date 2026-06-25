# Erdős #23, Step 2 — unconditional near-theorem + isolated open lemma

**Status: INTERNAL consolidation (NOT for publication — all-or-nothing rule: only a full sorry-free Lean
proof of the conjecture counts). Packaged per GPT Pro Q41.** 2026-06-23.

## The conjecture (Step 2)
Every triangle-free graph `G` on `N` vertices has `β(G) = e(G) − MaxCut(G) ≤ N²/25`
(equivalently `d_mono(G) := 2β(G)/N² ≤ 2/25`). For `N = 5n`, extremal at the C5[n] blow-up.

## Unconditional NEAR-theorem (asymptotic, rigorous)
> For every triangle-free graph `G` on `N` vertices,
> **`β(G) ≤ (1/25 + δ/2)·N² + o(N²)`**, with the EXACT rational `δ = 6.0699891…×10⁻⁵`
> (`δ = 12045893274065266971721 / 198450000000000000000000000`).

Equivalently `d_mono(G) ≤ 2/25 + δ + o(1)`. The δ/2·N² overshoot is the only gap to the conjecture
(≈ 0.0758 % of N²/25).

### Two components
1. **Tails (d_edge ∉ band).** Balogh–Clemen–Lidický (arXiv:2103.14179) prove `β ≤ N²/25` (asymptotically)
   for edge-density outside the medium band, i.e. `d_edge ≤ 0.2486` or `d_edge ≥ 0.3197`.
2. **Medium band (d_edge ∈ [0.2486, 0.3197]).** EXACT order-9 flag-algebra dual-margin certificate:
   `d_mono(W) ≤ 2/25 + δ` for every triangle-free graphon `W` of band edge-density. Machine-verified in
   exact rational (Fraction) arithmetic.

## The exact medium-band certificate
Contradiction/deficit LP at order 9 (n=9 triangle-free states; A006785: 1897). For each rooted type σ and
profile-cut p, the BCL deficit `g_{σ,p}(H) = (same-side mono density) − 2/25` satisfies, for every graph H,
`d_mono(H) − 2/25 ≤ min_{σ,p} g_{σ,p}(H)` (profile-cuts ⊆ all cuts ⇒ leave ≥ mono than the true max-cut).

**Dual-margin certificate (GPT Q40, Pick a).** Nonneg multipliers `λ_r` (deficit, `Σλ_r = 1`), `γ_j`
(rank-one moment-PSD cuts `v^T M^σ v ≥ 0`), `μ, ν` (band slacks), such that **for ALL 1897 states H**:
```
Σ_r λ_r g_r(H) + Σ_j γ_j m_j(H) + μ(e_H − 0.2486) + ν(0.3197 − e_H)  ≤  δ   (verified EXACTLY).
```
On a band graphon the added terms are ≥ 0, so `Σλ_r g_r ≤ δ`, hence
`d_mono − 2/25 ≤ min_r g_r ≤ Σλ_r g_r ≤ δ`.  ⇒ `d_mono ≤ 2/25 + δ`.

- Kept: 8 deficit rules + 114 rank-one moment cuts (localizers excluded — exact regeneration over
  permutations(n,5) impractically slow; they would tighten δ to ≈ 4.5e-5 but are not needed).
- Checker: `bridge/flagsdp/certify_dual.py` (builds the LP + EXACT Fraction verification via
  `flag_exact.py` regenerators: `gr_exact` for deficits, `moment_cut_exact` for moment cuts).
- Artifact: `bridge/flagsdp/dual_cert_n9.pkl` (the rational multipliers + the exact `max_H Φ = δ`).

## The single OPEN lemma (removes δ/2 → the full conjecture)
GPT Pro verdict (Q38–Q39): the remaining gap is the **irreducible BCL medium-band gap** — the joint
radius-2 bound
```
Q − T + 2D  ≥  Ne − 2N³/25 + c(N²/5 − e) − o(N³)      (triangle-free, any small c>0),
```
with `Q = Σ_x d(x)²`, `T = Σ_v e2(v)` (edges inside L2(v)), `D = Σ_v Δ_v`,
`Δ_v = MaxCut(H_v) − S_v ≥ 0` (radius-2 ball surplus; exact local form
`Δ_v ≥ max_{U⊆L2(v)} [e(U, L2(v)∖U) − Σ_{z∈U} c(v,z)]`). The exact reduction
`Q − T + 2D ≥ Ne − 2N³/25  ⟺  β ≤ N²/25` is verified and C5[n]-tight.
**No known elementary per-vertex certificate proves the density-coupled `c(N²/5 − e)` improvement**
(low-codegree shortcut refuted: a balanced Clebsch blow-up has min nonedge codegree exactly N/8).
Proving any uniform `c > 0` would strengthen the unresolved BCL result.

## What was ruled out (so future work doesn't repeat it)
- order-9 flag-SDP moment hierarchy SATURATES (4K1/S4: +4.3e-5→+2.30e-5; 5K1/S5: +2.29e-5; cut-floor).
- the cut fix (non-profile / two-extension) needs order-11 (infeasible at n=9).
- low-codegree `δ₂ ≤ N/8 ⇒ d_mono ≤ 2/25 − γ` (uniform γ): FALSE (C5[m]+pendant, d_edge=2/5, d_mono→2/25).
- density-coupled `c(2/5 − d_edge)` holds numerically (empirical c ≈ 0.2 ≫ needed) but its general-N proof
  IS the open joint bound above.
