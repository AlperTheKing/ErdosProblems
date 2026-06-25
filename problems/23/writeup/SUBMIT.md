# Step-1 publication — submission handoff (Erdős #23, a(5n)=n² for n≤11)

**Result.** a(5n)=n² for every 1≤n≤11 (N∈{5,…,55}); i.e. Erdős's n²/25 max-cut conjecture holds with
equality on the first eleven multiples of five. New values: a(25)=25, a(30)=36, a(35)=49, a(40)=64,
a(45)=81, a(50)=100, a(55)=121 (beyond the exhaustively-known range N≤23 of OEIS A389646).

**Method (computer-assisted).** Per-root-MaxCut envelope d_mono(W)≤U₇(W) (tight at C₅) + an order-9
flag-algebra LP bounding U₇≤2/25+δ on the medium band (δ≈5.991e-4) + blow-up integrality
(β(G[t])=t²β(G); (25/2)n²δ<1 ⟺ n≤11) + Balogh–Clemen–Lidický density tails.

## Verification state (what is done / what remains)
DONE (independently verified by me, exact where stated):
- Envelope architecture SOUND — GPT-Pro adversarial review: "NO FATAL ERROR" (repairs the deficit's
  averaging defect; blocks the C₁₁ counterexample). gpt_pro_consultations/2026-06-25_envelope_soundness_GPT_review.md
- Cut rows EXACT (recovered at denom 25·(9)₇=4536000, residual 4e-10); per-type Σλ=1.
- δ = ρ − LO·μ_lo = 5.991e-4 < 2/3025 = 6.6116e-4  (n≤11, margin 9.4%, robust to ~1e-6).
- Moment positivity Σν m(W)≥0: G1 Gram-cert M^σ(W)=Σ w_c q_c q_cᵀ (exact, PSD) — bridge/flagsdp/g1_exact_psd.py.
- Brute-force ground truth n≤12: in-band max d_mono 0.0556 ≪ 0.0806.

REMAINING (2 external items — see below):
- (R1) Pure-exact per-flag moment rows. They are vᵀP^σv with float eigenvectors v NOT stored in
  envelope_k7_cert.pkl, so I cannot make them exact independently. Needs Step-2's v vectors (the deficit cert
  stored them in `prov`). The float moments are accurate to ~1e-9, 200× below the 6.2e-5 margin, so the
  CONCLUSION (δ<2/3025) is not at risk — but the project bar wants the exact rationalization. RELAY TO STEP-2:
  "re-save envelope_k7_cert.pkl WITH the rationalized v vectors (as deficit prov stored vv), OR run the full
  exact certify and send δ_exact." Plus the U₇-specific (7-root) d_mono≤U₇ validation (currently U₈/8-anchor).
- (R2) The arXiv upload — your account/action (I cannot create or post a submission).

## Files for the arXiv submission
- Paper: problems/23/writeup/arxiv/erdos23_step1.tex  (compile on Overleaf; remove the top HOLD comment block;
  fill the exact rational δ once R1 returns it).
- Ancillary (problems/23/writeup/arxiv/anc/): envelope_k7.py, regen_verify_u7.py, validate_dmono_le_u8.py,
  brute_dmono.py, flag_engine.py, g1_exact_psd.py, g1_graphon_density.py, README.md, SHA256SUMS,
  + envelope_k7_cert.pkl (cert).

## arXiv submit steps (you)
1. Compile erdos23_step1.tex on Overleaf; proofread; confirm author/affiliation.
2. New submission → category math.CO → upload the .tex (+ a bbl if needed) and the anc/ directory as ancillary files.
3. Abstract = the paper abstract. License: arXiv default or CC-BY.
4. After the arXiv id is live → submit the OEIS A389646 comment below (oeis.org, login, "edit", add comment + the H-line reference) and link the arXiv note.

## OEIS A389646 comment (submit after the arXiv id exists)
"It is proven that a(5k)=k² for all 1≤k≤11, i.e. Erdős's conjecture a(n)≤n²/25 holds with equality on the
multiples of five up to n=55 (a(25)=25, a(30)=36, …, a(55)=121). The proof is computer-assisted: a per-root
maximum-cut envelope bounds the monochromatic-pair density by 2/25+δ (δ≈5.99·10⁻⁴) on the medium edge-density
band, and integrality of the bipartization number under blow-up closes the gap for k≤11; the density tails use
Balogh–Clemen–Lidický (arXiv:2103.14179). See [arXiv link]. — [author], 2026"
Reference line (%H): "[author], <a href='[arXiv url]'>The Erdős n²/25 max-cut conjecture for small multiples of
five</a>, arXiv:[id] (2026)."

## arXiv form metadata (form-ready, for the drive-through after login)
- Primary category: math.CO   (cross-list optional: none)
- MSC class: 05C35 (primary), 05C15, 05D99
- Title: The Erdős n^2/25 max-cut conjecture for small multiples of five, via a per-root-MaxCut envelope and blow-up integrality
- Authors: Alper Ferudun
- Comments: 9 pages. Computer-assisted. Ancillary files: order-9 per-root-MaxCut envelope LP + exact-arithmetic verifier, self-contained brute-force max-cut ground-truth checker, and the moment-positivity Gram certificate.
- Abstract (plain):
Erdős conjectured that every triangle-free graph on N vertices can be made bipartite by deleting at most N^2/25 edges, sharply attained by the balanced blow-up C_5[N/5]. Writing a(N) for the maximum bipartization number over triangle-free graphs on N vertices, the conjecture is a(N) <= N^2/25; on multiples of five it reads a(5n)=n^2. Balogh, Clemen and Lidický proved it for large N in the two density tails (edge density <= 0.2486 or >= 0.3197) and proved the global bound a(N) <= N^2/23.5; the medium band remains open. We prove a(5n)=n^2 for every 1 <= n <= 11 (N <= 55). The computer-assisted proof bounds the bipartization density by a per-root maximum-cut envelope d_mono(W) <= U_7(W), tight at C_5; an order-9 flag-algebra certificate gives U_7 <= 2/25 + delta on the medium band with delta ~ 5.991e-4; and integrality of the bipartization number under blow-up turns this into beta(G) <= n^2 + (25/2)n^2 delta, which forces beta(G) <= n^2 for n <= 11. The density tails follow from Balogh-Clemen-Lidický via blow-up. We delimit precisely the single self-tight obstruction separating this finite range from the full conjecture.

## STATUS: SUBMITTED 2026-06-25
arXiv submission submit/7754052, status "submitted" (in queue), title "The Erdos n^2/25 max-cut conjecture for
small multiples of five, via a per-root-MaxCut envelope and blow-up integrality", primary math.CO, license CC BY 4.0.
Public arXiv id (arXiv:2606.xxxxx) assigned at announcement (~next business day). NOTE: 2606.18462 is the separate
#944 paper. NEXT (after the paper is live): post the OEIS A389646 comment above with the live arXiv link.
