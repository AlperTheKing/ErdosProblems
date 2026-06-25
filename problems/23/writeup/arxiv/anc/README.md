# Ancillary files — "The Erdős n²/25 max-cut conjecture for small multiples of five"

Computer-assisted proof that **a(5n) = n² for all 1 ≤ n ≤ 11** (N ≤ 55), where a(N) is the maximum,
over triangle-free graphs G on N vertices, of the minimum number of edges whose deletion makes G
bipartite (β(G) = e(G) − maxcut(G)).

## Method
1. **Per-root-MaxCut envelope** (Lemma 3.1): for the 107 triangle-free 7-root types,
   `d_mono(W) ≤ U₇(W) = 2/25 + Σ_σ min_c g_{σ,c}(W)`, tight at the C₅-blow-up.
2. **Order-9 flag-algebra LP** certifies `U₇ ≤ 2/25 + δ` on the band `[0.2486, 0.3197]`, with
   `δ ≈ 5.991×10⁻⁴` (exact rational in the certificate). η ≤ δ (the LP is a relaxation).
3. **Blow-up integrality**: `β(G[t]) = t²β(G)` ⟹ `β(G) ≤ n² + (25/2)n²δ`; `(25/2)n²δ < 1` for n ≤ 11
   (threshold `2/(25·121) = 6.6116×10⁻⁴`; margin 9.4%). Tails by Balogh–Clemen–Lidický (arXiv:2103.14179).

## Files (scripts; 144 KB)
- `brute_dmono.py` + `flag_engine.py` — **self-contained independent brute-force max-cut ground truth**
  (needs no certificate). `python brute_dmono.py 9 12` → in-band max d_mono ≤ 0.0556 ≪ 0.0806.
- `validate_dmono_le_u8.py`, `c11_check.py` — exact verification of the envelope soundness `d_mono ≤ U`
  (incl. the C₁₁ adversarial test; tight at C₅).
- `envelope_k7.py` (+ `run_k7b.py`, `flag_cutgen.py`, `flag_localizer.py`, `compute_U8.py`) — the order-9
  per-root-MaxCut envelope LP generator.
- `regen_verify_u7.py` — rebuilds the LP from the certificate, re-solves η, extracts the dual
  (per-type Σ_c λ_{σ,c}=1, band μ, moment ν), and runs the exact-rational cut+band feasibility check.
- `g1_exact_psd.py`, `g1_graphon_density.py`, `g1_soundness_check.py` — the moment-positivity Gram
  certificate `M^σ(W) = Σ_c w_c q_c q_cᵀ` (manifestly PSD; Razborov's theorem, exact rational form).

## Certificate and cache (not shipped here — size)
The converged envelope certificate (`envelope_k7_cert.pkl`, ~108 MB: 107 types, 4452 cuts, 1874 moment
rows) and the order-9 flag cache (`cache_n9.pkl`, ~278 MB) exceed arXiv ancillary limits. A **compact exact
certificate** (the dual + the ~617 active rows, as exact rationals) accompanies the final version; both the
cache and the full pool are regenerable from `envelope_k7.py` (which runs the flag engine). The
self-contained `brute_dmono.py` already gives independent confirmation without either.

## Verification status
The envelope architecture is sound (independent adversarial review: no fatal error). Verified exactly:
the cut rows (denom 25·(9)₇ = 4536000), per-type Σλ=1, `δ = ρ − LO·μ_lo < 2/3025` (margin 9.4%), the
moment positivity Gram certificate, and brute-force ground truth (n ≤ 12). The per-flag moment rows are
`vᵀP^σv`; their exact rationalization (the `v` vectors) is included in the compact certificate.
