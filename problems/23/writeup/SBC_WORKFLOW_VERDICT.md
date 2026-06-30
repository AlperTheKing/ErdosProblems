# verify-sbc-architecture workflow verdict (2026-06-29)

All four gates reproduce exactly. I have independently confirmed every load-bearing number. Here is the verdict.

---

VERDICT — Exact verification of GPT-Pro's SBC proof architecture (Erdos #23)

All four gates were re-run; every load-bearing number below was independently reproduced (exact `Fraction` + rational LDL, no floats in any verdict).

(1) Does BLOCK-SBC hold exactly on the full battery? — NO. REFUTED.
The single claim the whole GPT-Pro proof reduces to — for every gamma-min connected-B max cut and every positive K-component C, rho(O_C) + m_C <= n_C + n_C^2/25 — is FALSE.
- Canonical gate `_wf_blocksbc.py`: tested 18764 components, 131 violations.
- The structural pillar of the reduction DOES hold: block-diagonality of O over K-components held universally (0 cross-block nonzero entries across all 18764 components / all cuts). So "O is block-diagonal" is sound; what fails is the per-component spectral inequality itself.
- Cleanest exact witness (census N=9, g6 = `H?AFBo]`), independently reconfirmed in `_wf_audit_n9.py`: positive K-component C={1,2,3,4,6,7,8}, n_C=7, m_C=2, bad edges {(1,7),(2,7)}, O_C = [[9/2,7/2],[7/2,9/2]] with exact eigenvalues {1,8} so rho(O_C)=8 exactly. Then rho+m_C = 10 > n_C + n_C^2/25 = 224/25 = 8.96, exact gap 26/25 = 1.04, and (c·I − O_C) with c=174/25 is NOT PSD by rational LDL. (The N=9 max-cut is verified global three ways: brute size 10 == CP-SAT optimum 10 == CP-SAT bound 10.)
- First violation by family order (structured, large margin), reconfirmed in `_wf_audit_L8.py`: two-lane L=8, N=27, single positive K-component n_C=9, m_C=4, O_C=[[7,7,5,5],[7,9,5,7],[5,5,5,5],[5,7,5,7]], rho(O_C) >= 24, so rho+m_C >= 28 vs RHS 306/25 = 12.24 — margin ~ −16. The two-lane family (L=8,12,16,20) all four fail; this is the known rho(O)<=N killer family.

(2) Does the adversarial hunt find a counterexample? — YES. The architecture (as a per-component reduction) is REFUTED.
Adversarial harness `_wf_adversarial.py`: tested 172841 components, 1468 violations, holds=FALSE. Quoting the smallest self-contained witness: "triangle-free N=9, g6=H?AFBo] ... n_C=7, m_C=2 ... O_C=[[9/2,7/2],[7/2,9/2]] ... rho(O_C)=8 (exact) ... 8+2=10 <= 7+49/25 = 224/25 = 8.96 — FALSE (10 > 8.96, margin 1.04)." Census N=11 alone (exhaustive gamma-min connected-B max cuts over 90842 graphs) gives 1455 genuine violations; first census-11 violator g6=`J???CB_]?~?`. Random triangle-free N=14,15,16 gave 0 violations — violations concentrate in path/cycle-rich structured graphs (long high-aspect-ratio K-components), not dense random ones.

(3) Does BUNDLE-SBC (the 1D terminal inequality) hold? — NO. REFUTED.
`_wf_bundle1d.py`: tested 290,501,791 (tuple,m) pairs exhaustively (cleared denominators, zero floats), 4 violations. First/cleanest, independently reconfirmed: ell=5, ns=(2,1,2,1,2), m=2: LHS = 2 + 2 + 2·(1+5/2) = 11 > RHS = 8 + 64/25 = 264/25 = 10.56. The other three: (3,1,3,1,3,m=3) 16 > 396/25; (3,2,3,2,3,m=6) 20 > 494/25; (4,3,4,3,4,m=12) 31 > 774/25. Critically, two of these have NO singleton layer (min n_i = 2 and 3), so the failure is not a trivial 1/n_i singleton blow-up — it is the genuine alternating/unbalanced C5 blow-up (ABABA) where the boundary term n_0+n_{ell-1} plus the reciprocal load m·c beats the N^2/25 budget. All 4 violations are at ell=5; none at ell=7,9,11,13. Equality holds at exactly the 7 ell=5 balanced cases ns=(k,…,k), m=k^2, k=1..7 (verified).

(4) Did the coherent-bundle model identity verify? — YES. This is the one gate that holds.
`_wf_bundlemodel.py`: tested 8613 coherent/balanced tests, 0 violations. Claim (i) O_model = B_H^T B_H + c·J_m held EXACTLY for every bundle (ident_all=True; c = sum_{i=1}^{ell-2} 1/n_i, B_H the 0/1 endpoint incidence). Claim (ii) rho(O) <= rho(B^TB) + c·m certified via the rank-1 PSD J bound (ii_all=True). Claim (iii) the gate rho(O_model)+m <= n+n^2/25 held for all coherent bundles (0 fails), tight at ell=5 balanced full K_{t,t} (det=0, zero pivot). The only failures are 2 NON-coherent degenerate configs where an interior layer is smaller than an endpoint layer (interior slab < endpoint), which are not valid girth-5 blow-up bundles — outside the hypothesis.

(5) Overall: SOUND or BROKEN? — BROKEN as a complete exact-testable skeleton.
Three of the four gates FAIL on exact counterexamples: BLOCK-SBC (the claim the whole reduction targets), its adversarial restatement, and the BUNDLE-SBC 1D terminal inequality. Only the algebraic model identity O = B_H^T B_H + cJ (gate 4, claim (i)/(ii)) and the coherent-restriction gate (claim (iii)) survive — and they survive only because "coherent" excludes precisely the alternating/unbalanced configurations that break the other gates. So the localization architecture, as literally stated, does not close: the per-component budget n_C^2/25 is too small to absorb rho(O_C)+m_C on small/dense or long high-aspect-ratio K-components, while the global SBC (full N, rho(O)+|M| <= N+N^2/25) survives every case tested and is tight at C5[t] — it works only because the full N is ~3x the offending n_C, so N^2/25 absorbs the high rho. Calibration is correct (exact equality at C5[t]: t=1..4 give margin exactly 0); the additive/localized structure is what is wrong.

(6) The remaining UNVERIFIED-BY-GATE piece — the open analytic step.
None of the four gates touches the actual hard lemma, and it is precisely the one piece that is NOT exact-gateable: the hot-core compression lemma — "a Perron-hot noncoherent K-component admits a neutral, Gamma-decreasing switch." This is the analytic claim that whenever a K-component is noncoherent (interior slab smaller than an endpoint — exactly the configuration that breaks gates 1–3) and Perron-hot, one can apply a Gamma-non-increasing local switch that drives it toward the coherent/balanced extremal where gate 4 holds with equality. The gate battery confirms two bracketing facts that make this lemma necessary AND sufficient-shaped:
  - the coherent endpoint is exactly where the inequality becomes true and tight (gate 4, equality at C5[t]/balanced K_{t,t});
  - every refutation (gates 1–3) lives strictly in the noncoherent/unbalanced region (alternating ABABA C5 blow-ups, long two-lanes), i.e. exactly the domain the compression lemma must evacuate.
So the architecture is not refuted as a strategy — it is refuted as a finished proof: its terminal inequalities only hold post-compression, and the compression lemma itself remains the single open analytic step, unverified by any exact gate (it is a global optimization/monotonicity statement, not a finite per-instance PSD check). That lemma is where all remaining mathematical risk now sits.

Reproduced/verified scripts (all absolute):
- E:\Projects\ErdosProblems\problems\23\writeup\_wf_blocksbc.py (BLOCK-SBC canonical gate, 18764/131)
- E:\Projects\ErdosProblems\problems\23\writeup\_wf_adversarial.py (adversarial hunt, 172841/1468)
- E:\Projects\ErdosProblems\problems\23\writeup\_wf_audit_n9.py (self-contained N=9 witness, reproduced)
- E:\Projects\ErdosProblems\problems\23\writeup\_wf_audit_L8.py (self-contained two-lane L=8 witness, reproduced)
- E:\Projects\ErdosProblems\problems\23\writeup\_wf_bundle1d.py (BUNDLE-SBC 1D, 290.5M/4)
- E:\Projects\ErdosProblems\problems\23\writeup\_wf_bundlemodel.py (coherent model identity, 8613/0, ident_all=True)
- E:\Projects\ErdosProblems\problems\23\writeup\_wf_census_viol.py (census violation extractor)