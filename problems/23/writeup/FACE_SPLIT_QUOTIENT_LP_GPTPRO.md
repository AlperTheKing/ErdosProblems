# Face-split: quotient-coupled LP formulation + cap ladder (GPT-Pro, MAIN, 2026-07-05)

Source: MAIN reply (9647c raw, fully extracted). Supersedes the combined-cone-only reading of
the face-split form; the combined cone is SOUND but non-scalable. Lean/checker interface is
UNCHANGED (§10): the emitted certificate is the ordinary expanded ConeCert P = F + Ga·M;
the quotient machinery is a search/exactification accelerator only.

## Core identity (§1)
P = F + Ga·M with F ≥ 0 on the WHOLE chart region and M ≥ 0 on the whole region ⟹ P ≥ 0
(Ga ≥ 0 on the chart). A two-stage "pick any P_face ≡ P mod Ga" is UNSOUND unless P_face is
globally nonnegative — the raw normal form rem_a(P) is NOT a valid P_face (§6).

## Quotient-coupled LP (§2, the recommended form)
Exact polynomial division by g := Ga# (term order graded_reverse_lex, divisor normalized
monic over Q): R = rem_a(R) + g·quo_a(R). Apply to P and every face column F_j; lift
columns M_k stay unreduced. Certificate ⟺ the two reduced systems:
  (Q-rem):  Σ_j α_j rem_a(F_j) = rem_a(P)
  (Q-quo):  Σ_k β_k M_k + Σ_j α_j quo_a(F_j) = quo_a(P)
with α, β ≥ 0. Equivalent to the combined cone but on remainder rows + degree-9 quotient
rows instead of the full degree-11 (167,960-row) coefficient space.

## Column families (§3)
- FACE cone (globally nonneg columns only): base Bernstein deg ≤ 11; G_b·q (b ≠ a);
  (Ga−G_b)·r_b; band·h. EXCLUDE Ga·q in the first pass (zero remainder role).
- PAIR-CLOSURE RULE (essential; explains capped infeasibility): any cap including G_b·m
  must include (Ga−G_b)·m, and vice versa — because G_b·m ≡ −(Ga−G_b)·m mod Ga.
- LIFT cone: base deg ≤ 9; ALL G_i·q_i INCLUDING i = a (Ga² terms carry off-face
  curvature); (Ga−G_b)·r_b deg ≤ 9; band deg ≤ 9.

## Cap ladder (§4)
- Tier 0 diagnostic: compute rem_a(P), quo_a(P); read off their monomial supports.
- Tier 1: pair-closed reduced support touching rem_a(P) (face) / quo_a(P) (lift).
- Tier 2: face pairs deg(m) ≤ 7; lift total ≤ 9 (gen/delta multiplier ≤ 7, band ≤ 8).
- Tier 3: full pair-closed face deg(m) ≤ 9 + full degree-9 lift (replaces the 58k combined).
Run Tier 2 first; Tier 3 on infeasibility.

## Sound two-stage variant (§5-7)
Stage A (quotient anchor): find F = Σ α_j F_j, α ≥ 0, with rem_a(F) = rem_a(P) ⟹ Ga | P−F;
set H := (P−F)/Ga. Stage B: certify H ≥ 0 in the lift cone. If Stage B fails: do NOT
iterate representatives — run the quotient-COUPLED LP (chooses F and M simultaneously).
If coupled Tier 3 fails: add quotient max-cut facets to both cones; then secondary-generator
split (Ga = 0 / Ga > 0 + second generator); only then raise degree.

## Exactification (§9)
floor-buffer if the quotient LP has margin; if boundary-feasible, Markowitz+repair in the
QUOTIENT rows (not full expanded rows); final emitted certificate is EXPANDED and passed
through the official Fraction checker.

## Invocation block (§9)
mode=quotient_face_split; divisor=Gsharp[a]; term_order=graded_reverse_lex;
normalize_divisor=leading_coeff_to_1; compute remP/quoP + remF_j/quoF_j per face column;
solve (Q-rem)+(Q-quo) with alpha,beta >= 0; column policy per §3 (face: base ≤11, paired
G_b·m/(Ga−G_b)·m ≤11, band ≤11, exclude Ga·m first pass; lift: base ≤9, all G_i·q_i incl.
i=a ≤9, deltas ≤9, band ≤9); Tier 2 then Tier 3.
