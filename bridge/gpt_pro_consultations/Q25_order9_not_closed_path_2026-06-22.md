# Q25 — order-9 flag-SDP does NOT close t=2/25; which path to close the medium band?

## Honest state (all cut families proven sound, exact-cert machinery validated)

Erdős #23 Step 2 reduces to: certify d_mono* ≤ t=2/25=0.08 in the BCL-open MEDIUM band
d_edge/C(N,2) ∈ [0.2486, 0.3197] (BCL handles both tails; C5[n] is in the high tail).

Contradiction LP over triangle-free states of order N: max η s.t. Σx=1, band, and every valid
inequality f·x ≥ 0 for the counterexample x_W. η<0 ⟹ band closed at t.

Cut families implemented (all sound, validated):
1. **Deficit cuts** g_{σ,p}(H) = E_θ[mono-density of BCL profile-cut − t] ≥ 0 (BCL local cut).
2. **Moment-PSD** M^σ(x) ⪰ 0 (flag positivity) — as rank-one cuts (LP) OR conic.
3. **Cut-deficit LOCALIZER** L^{σ,p}(x) = ∫_θ δ_p(θ) ρ(θ)ρ(θ)ᵀ ⪰ 0, σ=C5, p-separated.
   (δ_p(θ) ≥ 0 pointwise because each profile-cut is a complete cut ⟹ mono ≥ d_mono > t.)

## Result (order N=9, states=1897, conic = full moment-PSD, status optimal)

| config | η at t=0.08 |
|---|---|
| deficit only (k≤4) | +9.0e-4 |
| deficit + moment-PSD | +2.0e-4 |
| deficit + moment + C5 localizer (p-sep) | **+4.3e-5** |

η = +4.3e-5 > 0 ⟹ **order-9 does NOT close**. (A localizer bug earlier gave a false −7.2e-4;
the exact rational certificate caught it; now fixed and the +4.3e-5 is the true order-9 value.)

The localizer is clearly the active lever (5× from moment-only) but order-9 falls ~4e-5 short.

## Question

Which single path do you choose to close the last +4.3e-5 (cheapest that works)?

A. **Order-10** (states=12172; deficit + moment + C5 localizer order-10). Order is the proven
   lever (~5× per order). Heavy precompute (~2-3 h) but the C5 localizer at order 10 sees C5 + 5
   spectators (closer to the C5[2] extremal). Likely closes but expensive.
B. **More localizer TYPES at order 9** (k=4 cut-deficit localizers: C4, K1,3, P4, 2K2 — cheap,
   reuse order-9 cache). Adds independent PSD blocks; may close the +4.3e-5 without going to order 10.
C. **Higher-order C5 localizer at order 9** is impossible (k+4=9 is the minimum); but a k=6 / two-
   hub localizer, or pairing the C5 localizer with an edge/non-edge localizer, at order 9.
D. Something else (e.g. a stronger localizer construction, the Lasserre-style order-2 moment of the
   deficit, or accept order-9's bound and tighten t only to the achievable +4.3e-5 value).

Pick ONE concrete next step. I will implement exactly what you choose and verify with the exact
rational certificate (max_H Φ(H) ≤ 0 in Fraction arithmetic).
