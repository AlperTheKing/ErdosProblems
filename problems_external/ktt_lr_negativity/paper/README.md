# KTT positivity paper — reproducibility manifest

Paper: `ktt_positivity.tex` (amsart). Compile with any TeX distribution:
`latexmk -pdf ktt_positivity.tex` (no local pdflatex was available at draft time — compile before submission).

## Claims and their exact verifiers (all in `problems_external/ktt_lr_negativity/`)

| Paper item | What it asserts | Verifier / evidence |
|---|---|---|
| Thm 1 (r≤4) | KTT positivity for ≤4 parts | `r4_reeve/R4_STRUCTURAL_PROOF.md`; a₁≥0 via codim-2 atlas |
| Prop (codim-2) | all 99 BV weights > 0, min 1/9 | `UNIFORM_CODIM2_POSITIVITY.md`, checker **`uniform_codim2_gate_canonical.py`** (PASS) |
| Lemma (dilation) | qH lattice, e_k(qH)=q^k e_k(H) | verified exactly; independently re-checked on 33 rational r=5 hives |
| Thm 2 (top-4, all r) | e_D..e_{D-3} > 0, full-dim | `UNIFORM_CODIM2_POSITIVITY.md`, `UNIFORM_CODIM3_BV_REPORT.md` |
| Thm 3 (full-dim r=5) | all but linear coeff > 0 | `R5_CODIM4_LOCAL_POSITIVITY_REPORT.md` + `verify_r5_certificate.py` (PASS) |
| §Nonsimple | det-2 vertex cone is real | independently reproduced (hive4.py; c=50, rays (0,1,1),(1,0,1),(1,1,0)) |
| §Frontier | general KTT ⇐ (HTE); shortcuts obstructed | `GENERAL_KTT_PROOF_STATUS.md` + the six audit reports it cites |

## Engines
- `engine/lr_hive.exe` — hive lattice-point LR counter (COMMA-separated partitions on CLI).
- `engine/engineB_lrrule.py` — independent lattice-word LR-tableau counter.
- Cross-checked against each other for all |ν|≤8 and against published `lrcalc-rs` values.

## Independent-audit status (2026-07-22)
- r≤4: independently audited — a₁=Λ·μ on 11,415 non-witness hives (0 mismatches); dilation lemma and det-2 cone re-verified by hand.
- r=5: independently audited — referee 1 ACCEPT, referee 2 MAJOR_REVISION (editorial only, no math error); probe of 5,500 triples found 0 negative coefficients.

## Before submission — TODO (from referee 2)
1. **GAP A**: in the *technical reports* (`GENERALIZATION_REPORT.md`, `UNIFORM_CODIM2_POSITIVITY.md` §6) repoint the cited `uniform_codim2_gate.py` (crashes; superseded) to `uniform_codim2_gate_canonical.py`. No effect on the paper.
2. **GAP B**: scope wording "non-full-dimensional side-5 below top-four" in `GENERALIZATION_REPORT.md` §0 — the top-four theorem is for *full-dimensional* hives; already corrected in the paper's introduction.
3. Compile the .tex; set author/affiliation; final proofread of the frontier section against the six obstruction reports.
