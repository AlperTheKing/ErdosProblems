# Erdős #23 (triangle-free β≤N²/25): the component-local crux — consolidated 2026-07-01

Consolidation of the LOAD-PSC multi-angle attack (Claude workflow, 4 attack angles + exact gates) and
the parallel Codex/GPT-Pro frontier. Everything below is EXACT-verified unless marked OPEN.

## The reduction (all links established/verified except the final crux)

    β ≤ N²/25   ⟸   LRS: Σ_v T(v)² ≤ L·Γ   ⟸   (CV) component-local, for every geodesic K-component C:
                                                    Σ_{v∈C} T(v)² ≤ L · Σ_{v∈C} T(v),
    where  T(v)=Σ_f ℓ(f)p_f(v) (load),  Γ=Σ_f ℓ(f)²=Σ_v T(v),  L = N + N²/25 − m,  m=|M|.

- Σ_C over the K-components partitions V, so (CV) summed over C gives LRS. LRS ⟹ β≤N²/25 is established.
- Equivalent (truncated) form = Codex's PRESSURE-SURPLUS componentwise:
  Pressure_C(k) ≤ max(0, Source_C(k) − Volume_C(k)) for every component C and every load-prefix k,
  where the banks are the coarea capacity/volume of the truncated load. (CV) is its τ=∞ untruncated twin.

## Proven / exact-verified pieces

1. **Coarea identity (exact):** LOAD-PSC-5 ⟺ Φ(τ)=25·Σ_v a_τ(L−a_τ) − 5N(TV_B(a_τ)−TV_M(a_τ)) ≥ 0 ∀τ,
   a_τ=min(T,τ), via ∫₀^τ|H_s|ds=Σa, ∫₀^τ s|H_s|ds=½Σa², (D+25N)/25=L. Capacity coeff (D+25N−50s) flips
   sign at s=L/2.
2. **σ_s ≥ 0 (PROVEN, unconditional):** for ANY vertex set S, flipping S changes cut size by δ_M(S)−δ_B(S)≤0
   (max-cut optimality), so δ_B(S)≥δ_M(S). The cut-pressure measure is nonnegative. Survives two-lane.
3. **LOAD-PSC-5 / (CV) / PRESSURE-SURPLUS all exact-gated:** 0 violations on census N≤10 (18k+ cuts/comps),
   two-lane L≤30 (spectral-killer control), k-lane, Mycielskian(Grötzsch) N=23, Grötzsch, M(C7), glued
   islands, C5/C7/C9 blowups. Tight only at balanced C5[t] (D=0, L=N, T≡N). [Claude _loadpsc_gate.py,
   _cv_component_gate.py; Codex _codex_loadpsc_capacity_gate.py, _codex_pressure_component_local_gate.py]
4. **LOW-HARD-P5 (exact):** on low bands (2b≤N), if Γ>N·h then σ≤5h; 0 violations, max σ/h=15/4<5 in 1277
   hard rows. The odd-girth "5" is NOT tight on the low side.
5. **(CV) is genuinely nontrivial:** T(v)>L OCCURS (54/19928 census verts, first G?`F`w N=8: T=10>L=8.56).
   So overloaded vertices must be compensated within their K-component — not a pointwise ceiling.

## Rigorously KILLED (exact counterexamples — do NOT retry)

- ALL spectral / second-moment routes (ρ(O)≤N, ρ(K)≤N, ρ(K2)≤N, ‖T‖²≤NΓ, K2·T≤N·T "descent"): refuted by
  two-lane L=12 (ρ=40.2>39 on a unique γ-min cut, R<0, no descent). K=PPᵀ,O=PᵀP ⟹ ρ(K)=ρ(O).
- ALL per-level / local sufficient conditions for LOAD-PSC: pointwise σ_s≤5|H_s| (fails, ratio 6), LOW-D
  D|H_s|≥Nσ_s (2466 fails, slack −68), θ-split I5≥0 for s<L/2 (6599 fails), per-vertex charge (4075 fails).
  ⟹ the proof is irreducibly a GLOBAL Abel/transport fact (bank capacity at low s<L/2, pay pressure at s>L/2).

## The OPEN crux and provability assessment

**OPEN:** prove (CV) / PRESSURE-SURPLUS componentwise. All four attack angles returned proof_complete=false.
The hardest regime is **near-extremal** (dense, m≈N²/25, D≈0, L≈N, T≈N): there the deficit budget vanishes and
(CV) becomes a **stability/rigidity** statement — each unit of high-level cut-pressure must be charged to
capacity deposited by its length-ℓ≥5 geodesic corridor at lower load-levels (the ℓ²−25 odd-cycle surplus
furnishes the constant 5; census slack ratio Φ5/D ≥ 135/28 shows the constant is available), but no rigorous
corridor-to-bank charging map / per-component transport certificate was found.

**Assessment (convergent across Claude workflow, Claude gates, Codex, Codex's GPT-Pro):** the crux is the
same odd-girth **global anti-concentration** hardness as the original ROWSUM problem, now correctly recast in
FIRST-MOMENT (transport) form (which is why it survives the two-lane control that kills all spectral surrogates).
This is plausibly **hardness-equivalent to the conjecture itself** (matches BREAKTHROUGH_VERDICT.md 2026-06-29).
The C5-colorable subcase is cleanly PROVEN (cyclic-min-product, 1/25=(1/5)², equality iff balanced C5[N/5]);
the non-C5-colorable residual is the open core. No known proof in the literature (best published: N²/23.5,
Balogh–Clemen–Lidický; the medium density band 0.2486–0.3197 is open).

**Next:** attack the near-extremal stability form of (CV)/PRESSURE-SURPLUS (the corridor-to-bank charging map),
jointly with Codex. This is where all the remaining difficulty concentrates.
