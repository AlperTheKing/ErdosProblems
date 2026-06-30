# LRS coarea/CD attack — result: reduced to STAR (|M|-free pure-load quadratic); STAR itself open

Date 2026-06-29. All numbers EXACT (Fraction). Files: `_wf_lrsproof_*.py`.

## Outcome
The coarea/CD route to LRS, pushed to its sharpest non-lossy form, reduces LRS to a single
**|M|-free pure-load quadratic inequality STAR**, which is strictly stronger than LRS, validated
0-fail on the full standing gate, faithful (fails with triangles), and passes the N=23
iterated-Mycielskian finite-depth-killer gate. STAR closes #23 in one Cauchy-Schwarz step.
**STAR is not yet proved** — it sits in the same global odd-girth anti-concentration class as ROWSUM-O/SPEC.

## STAR
> **(STAR)**  `25 * Σ_v T(v)² ≤ Γ (N² + 25N − Γ)`,  where `Γ = Σ_v T(v) = Σ_f ℓ(f)²`.

Equivalently `Σ_v T(T−N) ≤ Γ(N²−Γ)/25`, or `25·(ΣT²/Γ) + Γ ≤ N(N+25)`.

### STAR ⟹ #23 (rigorous, non-circular; does NOT assume Γ≤N²)
- Cauchy–Schwarz + `ΣT=Γ` (handshake, proven): `ΣT² ≥ Γ²/N`.
- Plug into STAR: `25Γ²/N ≤ Γ(N²+25N−Γ)` ⟹ `25Γ ≤ N(N²+25N−Γ)` ⟹ `Γ(25+N) ≤ N²(25+N)` ⟹ **`Γ ≤ N²`**.
- `ℓ(f)≥5` (triangle-free) ⟹ `25|M| ≤ Γ` ⟹ `β=|M| ≤ Γ/25 ≤ N²/25`. ∎
- STAR ⟹ LRS, since `N²/25−|M| ≥ (N²−Γ)/25` (from `25|M|≤Γ`). So STAR is the stronger sufficient target.

### Validation (EXACT, 0 violation)
- census triangle-free connected gamma-min (loads cut) N=5..10 (5800 at N=10): STAR_viol=0.
- two-lane L=8,12,20,30 (the ρ(O)>N / ROWSUM-O / SM counterexample family): STAR holds, big margin.
- C5[t],C7[t],C9[t] blow-ups: STAR tight (margin 0) — the extremal family.
- Grötzsch (N=11), **Myc²(C5)=N=23** (CP-SAT-verified optimal max cut, Γ=400, margin +81277).
- **Faithfulness**: STAR FAILS on graphs WITH triangles (minℓ=3; census N=5,6,7), large negative margins —
  so STAR genuinely encodes ℓ≥5; it is not a free fact.

## Why the coarea/CD route collapses to STAR (the lossy relaxations are dead)
Coarea identity (verified exact everywhere): `Σ_v T(T−N) = ∫_0^∞ (2s−N)|H_s^>| ds`, `H_s^>={v:T(v)>s}`.
- The over-load tail equals exactly `U⁺ := Σ_{T>N} T(T−N) = ∫_N^∞ (2s−N)|H_s^>| ds`.
- **Overload-isoperimetry** `|H_s^>| ≤ δ_B(H_s^>)` for s>N: TRUE, 0-fail (census N≤9, two-lane, Grötzsch).
- **L-lemma** `Σ_{v∈A} T(v) ≤ N·δ_B(A)` for overload superlevels A: TRUE, 0-fail.
- BUT replacing `|H_s|` by `δ_B(H_s)` inside the weighted tail integral is **too lossy**:
  `J := ∫_N^∞ (2s−N)δ_B(H_s^>)ds ≤ Γ(N²/25−|M|)` is **FALSE** (Grötzsch J≈100.2 > slack 84; census N=8 G?`F`w J=120>28).
- Dropping the under-load entirely is also too lossy: **`U⁺ ≤ slack` is FALSE** (N=8 G?`F`w: U⁺=40 > slack=28).
  ⟹ LRS genuinely needs the negative under-load cancellation; no per-level or δ_B relaxation survives.
- The per-vertex sublemma **PV** `T(v) ≤ N+(N²−Γ)/25` (which would prove STAR by summing) is **FALSE**
  (Grötzsch T₁₀=815/63>11.84; N=8,10). ⟹ STAR's content is irreducibly global cancellation, not pointwise.

## Proven tools available toward STAR (none yet sufficient)
- handshake identity (exact): `2ΣT² − Σ_v T(v)D(v) = Σ_{e=xy∈B} μ(e)(T_x+T_y)`, `D(v)=Σ_{f∋v}ℓ(f)`, μ≥0.
- CD total variation (from max-cut): `Σ_{xy∈M}|T_x−T_y| ≤ Σ_{xy∈B}|T_x−T_y|`; Laplacian form `Σ_M(ΔT)² ≤ Σ_B(ΔT)²`.
- `Σ_v T = Γ`, `Σ_v(N−T)=N²−Γ` (P1,P2).

## Residual gap (precise)
Prove **STAR** `25ΣT² ≤ Γ(N²+25N−Γ)` for the geodesic load T of any triangle-free connected-B max cut.
Equivalent crux: `25·τ̄ + Γ ≤ N²+25N` with `τ̄ = ΣT²/ΣT` (T-weighted mean load) — a JOINT anti-concentration
(can't have both mean-load τ̄ and total Γ large). Tight exactly at T≡N (Γ=N², τ̄=N) = C_{2k+1}[t]. Needs the
global odd-girth-≥5 input; all local/per-level/per-vertex/δ_B reductions are refuted above.

## Files
`_wf_lrsproof_coarea.py` (coarea identity + CD/iso exact), `_wf_lrsproof_slackuse.py` (SM dead on two-lane),
`_wf_lrsproof_chain.py`/`_wf_lrsproof_budget.py` (δ_B tail lossy: BUDGET false), `_wf_lrsproof_uplus.py`
(U⁺≤slack false; L-lemma 0-fail), `_wf_lrsproof_star.py` (STAR 0-fail), `_wf_lrsproof_faith.py`
(faithfulness + N=23 gate), `_wf_lrsproof_pv.py` (per-vertex PV false), `_wf_lrsproof_chainproof.py`
(proven scaffolding 0-fail).
