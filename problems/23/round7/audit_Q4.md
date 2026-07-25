# AUDIT of round7/Q4.md — adversarial, independent re-verification

Auditor scripts (all in `E:\Projects\ErdosProblems\problems\23\round7\`, none importing the Q4
pipeline except where explicitly stated):
`audit_Q4_primal.py`, `audit_Q4_dual.py`, `audit_Q4_facts.py`, `audit_Q4_struct.py`,
`audit_Q4_hom.py`, `audit_Q4_blowup.cpp` / `.exe`.
Logs: `audit_Q4_petersen.log`, `audit_Q4_dual.log`, `audit_Q4_blowup_g8.log`,
`audit_Q4_blowup_petersen.log`, `audit_Q4_blowup_g8_Z.log`, `audit_Q4_blowup_petersen_Z.log`,
`audit_Q4_repro_run.log`, `audit_Q4_sosy_g11.log`.

Independence: my verifier builds Gamma_m from the circular-distance definition **in exact
Fractions**, builds Petersen as the Kneser graph K(5,2), re-derives every cut by searching **all**
2^(n-1) bipartitions (so the pickle's mask convention is never trusted), does its own polynomial
arithmetic, and tests PSD by producing an explicit LDL^T factorisation with symmetric pivoting
(pivot rule deliberately different from the gate's) and then **re-multiplying L D L^T and comparing
to the permuted matrix entry by entry** — so the PSD verdict does not depend on my elimination code
being correct. Every acceptance path is Fraction/int only.

---

## 1. CONFIRMED — `max_x psi(And(3) = Gamma_8 = Wagner) = 1/25`

Upper bound. `Q4_cert_g8_d1.pkl` passes all of my checks (`audit_Q4_primal.py`):

* pattern rebuilt independently: 8 vertices, 12 edges, 3-regular, triangle-free, = Wagner/Moebius
  ladder;
* all 29 listed monochromatic sets are realised by genuine bipartitions (searched all 128), listed
  cuts pairwise distinct, and they are **exactly** the 29 inclusion-minimal monochromatic sets;
* all 284 multiplier coefficients are exact `Fraction`s and `>= 0`; every multiplier monomial has
  degree 2;
* `sum_S nu_S == 25 L^2` exactly;
* `L^4 - sum_S nu_S q_S == sum_b v_b^T Q_b v_b` after `x = y^2`: 330 monomials, 0 mismatched;
* all 99 Gram blocks are stored symmetric and their symmetrisations are PSD, each with a
  re-multiplied factorisation. No float anywhere in the pickle (3090 Fractions + 68 exact integers).

The deduction is sound: nu_S >= 0 on the orthant, sum_S nu_S = 25 L^2 > 0, T >= 0 on the orthant
(via y^2), hence min over the listed cuts of q_S <= L^2/25, and psi is a minimum over **all** cuts,
so the subfamily is conservative — the direction is right.

Lower bound, independent of the PLATEAU lemma: `audit_Q4_blowup.exe g8 34` enumerates **every**
composition of N into 8 nonnegative parts (zero weights included) and gets
`max_a (25 bip(Gamma_8[a]) - N^2) = 0` exactly at N = 5,10,15,20,25,30 and `< 0` at every other
N <= 34 — never positive. So the ceiling is attained and the value is exactly 1/25.
Exact tightness on C5[n] holds by construction: at a C5-concentration `25 bip - N^2 = 0`
(verified separately for C5[k^5], k = 1..8, and the blow-up identity was cross-checked against a
direct brute-force max cut of the explicit blow-up graph).

Novelty precondition verified independently (`audit_Q4_hom.py`): Gamma_8 has **no** homomorphism to
C5, so the ceiling does not follow from the C5 certificate (a hom H -> K gives
psi(H,x) <= psi(K, phi_* x), hence max psi(H) <= max psi(K)).

Latent hole in *their* gate (not in the certificate): `Q4_gate.py`'s `ldl_psd` assumes the stored
Gram blocks are symmetric and never checks it; a non-symmetric block could pass while its symmetric
part — the only thing the quadratic form sees — is indefinite. Here 0 of 99 blocks are
non-symmetric, so nothing is wrong, but the gate would not have caught it.

## 2. CONFIRMED — `max_x psi(Petersen) = 1/25`

`Q4_cert_gpetersen_d1.pkl` passes the same 15 checks: 10 vertices, 15 edges, triangle-free,
135 listed cuts = exactly the 135 inclusion-minimal monochromatic sets (of 512 realisable),
2685 nonnegative Fraction coefficients, `sum_S nu_S == 25 L^2`, the 715-monomial identity matches,
all 256 symmetrised blocks PSD with re-multiplied factorisations.
Blow-up check: `max(25 bip - N^2) = 0` exactly at N = 5,10,15,20 and negative elsewhere for
N <= 22; the N = 15 maximisers are exactly the 12 C5-concentrations, no others — confirming the
report's "Z(Petersen) = 12 C5-concentrations, no segments".

The two PROVED items are genuinely independent: my exhaustive homomorphism table gives
Petersen -> Gamma_8 NO, Gamma_8 -> Petersen NO, Petersen -> C5 NO, and
Gamma_8 -> Gamma_11 YES, Gamma_11 -> Gamma_14 YES.

CONTEXT the report does not state: because And(3) -> And(4) -> And(5), max psi is monotone
**increasing** along the Andrasfai chain. And(3) is therefore the *weakest* open member — a ceiling
for And(4) would have implied And(3) for free, not conversely. The certified case is the easiest one.

## 3. CONFIRMED arithmetically, but the stated SCOPE IS TOO WIDE — the And(4) dual ray

`audit_Q4_dual.py` rebuilds Gamma_11 (22 edges, 4-regular, triangle-free), re-enumerates the 1001
degree-4 exponents, re-verifies all 386 moment blocks PSD (sizes 66/11/1) with re-multiplied
factorisations, all moments exact Fractions >= 0, and recomputes with the minimum over **all** 2^10
cuts:

    num = 8481669033/5000000 , den = 510871843/7500000 > 0 ,
    num/den = 25445007099/1021743686 = 24.903512933... < 25       (all three match the pickle)

The weak-duality derivation is correct as written. **But its pairing step
`sum_{S,m} nu_{S,m} zhat_S(m) >= sum_m (sum_S nu_{S,m}) min_S zhat_S(m)` needs
`nu_{S,m} >= 0` COEFFICIENTWISE**, i.e. mode `coef`. The report's own section 0 defines the scheme
by "(P1) nu_S >= 0 on the orthant" and states that mode `sosy` (nu_S(y^2) SOS) is "strictly more
general". So what is proved is

    c*_coef(Gamma_11, multiplier degree 2) <= 25445007099/1021743686,

not `c*(Gamma_11, degree 2) <= ...` as written in the HEADLINE, the EXACT VALUES table and section 6.
The gap is not cosmetic: I measured `min over m of min_S zhat_S(m) = 3806113/15000000 = +0.2537`,
i.e. **every** zhat_S(m) is strictly positive, so one negative multiplier coefficient (legal in
`sosy`, e.g. nu_S = (x_i - x_j)^2, which is orthant-nonnegative) destroys the inequality entirely.
Consequently the BLOCKED-section inference **"so degree 4 is genuinely required there" is
UNSUPPORTED** — degree 2 in the orthant (`sosy`) mode is untested. `Q4_dualrun.py`/`Q4_dual.py`
build the dual against `mode='coef'` (the default of `Q4_sos.build`), confirming the scope.

Measured (steering-grade, floating point, therefore NOT an acceptance-path claim): running the
report's own untouched machinery in the mode its section 0 actually defines,
`python Q4_run.py 11 1 sosy nd CLARABEL` -> status optimal, **c* = 24.978050256** on the 319
inclusion-minimal cuts (`audit_Q4_sosy_g11.log`, solve 58 s). That is strictly **above** the
claimed exact cap 24.903512933, i.e. the scheme as defined in section 0 already exceeds the number
the report presents as its ceiling. The domination reduction is lossless in this mode too
(nu_S(q_S - q_S') >= 0 on the orthant for any orthant-nonnegative nu_S), so the cut family is not
the explanation. An exact rational `sosy` certificate with c > 24.9035129 would upgrade this to a
formal REFUTED; producing one is easy in principle (the point is interior, unlike the c = 25 case)
but was not done here.

## 4. CONFIRMED — THEOREM Q4-1 (collapse of globally-nonnegative multipliers)

Every step checks out: lambda_S >= 0 on R^n with sum_S lambda_S = L^{2d} forces each lambda_S to
vanish on {L=0}; L irreducible gives L | lambda_S; a transversal sign change forces L^2 | lambda_S;
the induction lands on PSD quadratics with sum = L^2 = j j^T of rank 1, and PSD summands of a rank-1
sum annihilate j-perp, so lambda_S = c_S L^{2d}. Correct.

Minor defect: the corollary's citation of Motzkin-Straus does not match its use — MS concerns the
*unweighted* form and says nothing about where a *weighted* nonnegative quadratic attains its
simplex maximum. The conclusion is unaffected because the needed direction is trivial:
`max_x sum w_uv x_u x_v >= (1/4) max_uv w_uv >= (1/4)(1/5) = 1/20` since the weights sum to
`sum_S mu_S |mono(S)| >= 1` over 5 edges. So "value exactly 20 on C5" (already on the DEAD list)
stands. Also, the trailing sentence "if T is required to be globally SOS then the degree-2d scheme
is literally L^{2d-2} times the degree-2 scheme" is proved only *under the theorem's hypothesis on
the multipliers*, not from a hypothesis on T alone; as written it is a non-sequitur, though harmless.

## 4b. REFUTED (exact witness) — "equality exactly at the C5-concentrations"

Section 1.1 and the summary state: "bip(Wagner[a]) <= (sum a)^2/25 for every blow-up, with equality
exactly at the C5-concentrations". Exact falsifier, verified twice:

    a = (0,2,1,1,2,0,2,2)  on Gamma_8,  N = 10,  bip(Gamma_8[a]) = 4 = N^2/25 ,

support {1,2,3,4,6,7} of size **6**, so `a` is not a C5-concentration (the induced C5s of Gamma_8
are the eight 5-sets listed by `audit_Q4_facts.py`). Verification 1: minimum over all 128 cuts of
the monochromatic mass = 4. Verification 2: build the 10-vertex blow-up explicitly and brute-force
its maximum cut — 24 edges, maxcut 20, bip = 4. Further witnesses at N = 15:
(0,3,1,2,3,0,3,3) and (0,3,2,1,3,0,3,3), both with `25 bip = N^2 = 225`.
The report's own section 2 table and section 4 say the right thing (Z contains the 8 joining
segments as well), so this is an internal contradiction, not a computational error — but as written
the sentence is false.

## 5. The REFUTED item stands, but its DIAGNOSIS is incomplete; one sub-claim is REFUTED

* "Degree-2 multipliers are INFEASIBLE for And(3)" — correctly refuted by the gated certificate
  (item 1). Sub-facts confirmed by me: exactly **12 of the 29** inclusion-minimal cuts are arcs;
  the cut S = {1,3,5,7} has monochromatic edges exactly {(0,4),(1,5),(2,6),(3,7)};
  `round5/claude_wagner_cert3.py` does default to `arc_cuts([2,3,4])` = 20 cuts.
* **Diagnosis incomplete.** The recorded failure was with a *strict margin*, and a strict margin is
  impossible for **every** cut family at c = 25, not just for arcs. Proof: at a maximiser x*
  (L = 1, psi = 1/25) the family minimum is >= 1/25, so `sum_S nu_S q_S >= (1/25)*25L^2 = L^4` and
  `T(x*) = 0`; with `y* = sqrt(x*)`, `sum_b v_b(y*)^T Q_b v_b(y*) = 0` with every term >= 0 forces
  `Q_b v_b(y*) = 0`, and `v_b(y*) != 0` for the all-even block (it contains `y*_i^4 = (x*_i)^2 > 0`),
  so that block is singular for ANY valid certificate at c = 25. Measured on the
  verified certificate: total Gram dimension 330, **kernel dimension 252**, the 36x36 block has rank
  12. `round5/claude_wagner_cert3.py` maximises `tmar` subject to `G_b >= tmar*I`, which therefore
  cannot return a positive margin with any cut family. Attributing the record purely to the cut
  family is wrong; tightness is at least as responsible.
* **REFUTED sub-claim**: "The certificate's second-heaviest cut is the non-arc alternating cut
  S = {1,3,5,7}". By multiplier mass `nu_S(1,...,1) = sum_m nu_{S,m}` it ranks **fifth**:
  268.109420, 268.055647, 268.032482, 268.014875 (four 4-arcs, mono pairs {05,14}, {27,36},
  {16,25}, {03,47}) then 191.980284 for {1,3,5,7}. It is the heaviest *non-arc* cut and the only cut
  at the second distinct mass level; "second-heaviest" as written is false.

## 6. CONFIRMED — the exact-value table (graph facts and enumerations)

| claim | my independent value |
|---|---|
| bip(Gamma_8) = 2, 12 edges, maxcut 10 | 12 edges, maxcut 10, bip 2 |
| bip(Petersen) = 3 | 15 edges, maxcut 12, bip 3 |
| Gamma_8 has 8 induced C5s / Petersen 12 | 8 / 12 (Gamma_11: 33) |
| no hom to C5 for Gamma_8, Petersen | none (exhaustive) |
| inclusion-minimal cut counts 5, 29, 319, 4397 for k = 2,3,4,5 | 5, 29, 319, 4397 |
| \|Aut\| 16 (Gamma_8), 120 (Petersen), 22 (Gamma_11) | 16, 120, 22 |
| Z(Gamma_8) = 8 C5-concentrations + 8 joining segments | N=10: 8 + 8 midpoints; N=15: 8 + 16 interior points |
| exhaustive blow-up of Gamma_8, N <= 32: 0 iff 5\|N | confirmed to N <= 34 |
| the ten round5 witnesses | all satisfy psi <= 1/25; W2 (C5 uniform) exactly 1/25; W1 psi = 1/49 (arc-only bound 2/49 > 1/25 — the non-arc cut is what saves it); W8 far-regular Wagner psi = 1/32 |

## 7. UNSUPPORTED — three floating-point numbers presented inside "EXACT VALUES"

* "Gamma_8, degree 2, arc cuts only: c* = 24.98157" — a solver output; no dual certificate is
  produced for the arc-only family, so the strict inequality `< 25` is not established exactly.
  It is the *sole* quantitative support for the report's causal diagnosis in item 5.
* "Gamma_8, degree 4: c* = 24.999871" — solver output. The report's own embedding argument
  (a degree-2 certificate times L^2 is a degree-4 certificate: nonnegative coefficients survive,
  `sum = 25 L^4`, and `L^2 * SOS` is SOS) is valid and gives exactly 25; I checked it. The listed
  float is therefore noise, not a value.
* "Gamma_11, primal 24.903335" — solver output; only the dual side is certified.

## 8. CONFIRMED — reproducibility

`python Q4_exact.py 8 1` finished in **11 s** (claimed 12 s) and wrote a **byte-identical** pickle
(sha256 prefix `a753a93d82df092e`, identical to the shipped artifact), which passes my independent
audit unchanged (`audit_Q4_repro_g8.pkl`). The original artifact was restored.

## 9. Non-findings worth recording

* Section 1.5 ("the degree-independent first-order LP is feasible at all 48 maximisers of Gamma_8
  and at the C5 optimum") is **vacuous given item 1**: a verified certificate exists, and its own
  `mu_S = nu_S(x)/25` satisfies exactly those necessary conditions. Computing it adds nothing; the
  derivation itself is correct (I re-derived `sum_S mu_S d_j q_S = 2/25` on the support and `<= 2/25`
  off it).
* Section 1.4's domination lemma is sound and, in fact, not load-bearing: restricting to any
  subfamily of cuts is conservative for an **upper** bound on psi, so the reduction can only affect
  feasibility, never soundness.
* Protocol-specific checks, all clean: no float on any acceptance path (certificates are Fractions
  and exact integers); no psi value below 1/25 reported as a maximum for an odd-girth-5 graph (the
  sub-25 numbers are *scheme values* c*, i.e. weaker bounds 1/c > 1/25, not psi values); the integer
  enumerations do allow zero weights (mine do, and the maximisers found have zeros); the claimed
  exhaustive range N <= 32 is covered (mine covers N <= 34); no circularity — the certificate is
  constructed and verified without assuming any statement of conjecture strength; the only quoted
  theorem whose hypotheses do not match its use is Motzkin-Straus in item 4 (harmless).

## 10. Consequence, measured against WHAT COUNTS

The two PROVED items are correct and exactly verified, and they do prove Erdos #23 for every
blow-up of Wagner and of Petersen (and, by the homomorphism monotonicity above, for every graph
mapping into them). They are **not** an unconditional theorem on a minimum-degree range: converting
the And(3) ceiling into one needs a structure theorem of the form "delta >= c N implies hom to
And(3) or C5", which the report neither proves nor quotes. Combined with item 2's monotonicity
(And(3) -> And(4) -> ...), the band of accepted base 5 is unchanged by this report.
The one item that does kill a mechanism with an exact witness is the And(4) dual ray — with the
scope correction of item 3: it kills *coefficientwise-nonnegative* degree-2 multipliers on And(4),
not the degree-2 scheme as defined.
