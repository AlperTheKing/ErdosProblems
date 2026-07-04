# F6 exact active-face repair + thin-face/degenerate decision rule (GPT-Pro, MAIN thread, 2026-07-04)

Source: MAIN thread addendum reply (8637c; raw in-thread, msg idx 6 post-reload). Faithful
structured transcription; formulas reconstructed from the ZZ-transformed extraction.

## Classification (updated decision rule)
- **Thin-face row (F2-type)**: margin 1e-8 infeasible/unstable; margin 0 feasible; basis SMALL
  (#basic <= 128); exact replay passes or dust-repairs immediately. ACTION: margin-0 exact
  replay accepted. (k6/F2: basis 60, exact pass, min residual exactly 0 — archived as
  classification=thin_face_margin0.)
- **High-dim degenerate-face row (F6-type)**: margin-0 basis LARGE (#basic > 512 or #used > 500);
  exact replay yields source negatives or >20 residual negatives; min residual large rational
  height. ACTION: DISCARD float basis; exact active-face repair from best exact certificate.
- **Basis/form insufficiency**: active-face repair fails after 3 row-generation rounds.
  ACTION: face-split certificate around the dominant generator (F6#-face + lift).

## F6 primary recipe: exact active-face repair
Base: best exact F6 certificate p = A·lam0 + b0 with lam0 >= 0, b0_h < 0 exactly on
H0 = {21590, 21842, 22523, 22569}, all other b0_i >= 0, ZERO source negatives.
Solve exactly for a correction Delta with lam' = lam0 + Delta >= 0 and b' = b0 - A·Delta >= 0.

### Active row set R0 = H0 ∪ T0 ∪ D0
- T0 (tight guards): rows with 0 <= b0_i <= 2^-36 (1 + |p_i|); cap at 256 smallest normalized.
- D0 (damage guards): J_gain := {cols j : exists h in H0 with A_hj < 0}; include rows i with
  b0_i <= 2^-30 (1 + |p_i|) and exists j in J_gain with A_ij > 0; cap at 512 smallest.
- So |R0| <= 4 + 256 + 512 = 772.

### Column set J0 = J_old ∪ J_gain_top
- J_old := {j : lam0_j > 0}.
- Per hard row h, rank cols j with A_hj < 0 by score_h(j) = (-A_hj) / (1 + sum_{i in R0} max(0, A_ij));
  take top 512 per h (escalate 1024). J_gain_top = union.
- Expected |J0| ~ |J_old| + 1000..2000.

### Correction variables (source nonneg AUTOMATIC)
- Old cols j in J_old: Delta_j = u_j - v_j, u_j >= 0, v_j >= 0, v_j <= lam0_j.
- New gain cols: Delta_j = u_j >= 0 only.

### Two-stage exact LP (Markowitz_Q exact solver; all rationals)
- Hard-row target margin: b0_h - A_h·Delta >= 2^-30 (1 + |p_h|) for h in H0 (drop to 0 if infeasible).
- Stage 1: minimize sum z_h s.t. b0_h - A_h·Delta + z_h >= margin_h, z_h >= 0, and guards
  b0_r - A_r·Delta >= 0 for r in R0 \ H0. Require optimum 0 (else margin 0; else enlarge J0).
- Stage 2: fix hard deficit 0; minimize sum_j (1 + ||A_.j||_{1,R0}) (u_j + v_j).

### Exact apply + row generation
- Compute lam' and b' = p - A·lam' on the FULL official row set. If lam' >= 0 and b' >= 0: emit.
- Else R_{t+1} = R_t ∪ Worst64{i : b'_i < 0}; rerun from lam'. STOP after 3 rounds -> fallback.

### Invocation parameter block
mode = exact_active_face_repair; base_certificate = best_exact_F6_4neg;
hard_rows = [21590, 21842, 22523, 22569]; hard_margin = 2^-30 * (1 + abs(target_row));
tight_guard_threshold = 2^-36; damage_guard_threshold = 2^-30;
top_gain_cols_per_hard_row = 512 (escalate 1024); max_rowgen_rounds = 3;
exact_solver = Markowitz_Q; allow_signed_delta_on_old_support = true;
allow_additive_delta_on_new_gain_cols = true.

## F6 fallback: face-split certificate (NOT weak inequality)
- Face F6# = 0: prove P_k = P_face + F6#·H with H arbitrary signed; P_face gets a normal
  ConeCert from remaining nonneg constraints (simplex, near band 2s-1, dominance deltas
  F6#-Gb#, other generators). On the face the signed term vanishes; checker obligation
  P_face >= 0 on the face region. Exact and sound.
- Off-face lift: P_k = P_face + F6#·M with M >= 0 on the whole F6-dominant near region.
  If M >= 0 hard: split by a second generator; keep it a face-saturation family.

## FORBIDDEN for F6
- Replaying the 1414-col margin-0 basis (geometric failure, not prime budget).
- Float-seeded exact Bland pivoting (explores a huge degenerate face).
- eps-lexicographic perturbation AS the certificate (may generate candidates only; final
  certificate must be exact for the unperturbed target).
- Weak/tolerance certificates.
