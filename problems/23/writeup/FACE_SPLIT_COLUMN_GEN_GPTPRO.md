# FACE-SPLIT COLUMN-GENERATION (GPT-Pro MAIN, 2026-07-07) — Claude-archived, exact-gated

The hard-tail unblock: exact Phase-I conic column generation in quotient coordinates with a
transpose-pricing oracle. Do NOT build the 80k x 64k quotient matrix. Only build columns the
current dual says are useful. Emits the ordinary expanded ConeCert `P = F + Ga*M` (F,M,Ga>=0),
OR an exact Farkas ray (decisive falsifier for that chart row).

## 0. The feasibility problem (cone membership)
    b = [ rem_a(P) ; quo_a(P) ]  in  cone( { [rem_a(F_j); quo_a(F_j)] }_j  ∪  { [0; M_k] }_k )
- Face columns F_j ∈ C_face; Lift columns M_k ∈ C_lift.
- Final artifact = ordinary expanded identity  P = F + Ga*M,  F>=0, M>=0, Ga>=0.
- Quotient machinery is ONLY a search accelerator; the final checker never trusts the quotient LP.

## 1. Restricted master problem (Phase-I artificial variables)
Selected quotient columns A_J. Solve:
    A_J x + u+ - u- = b,   x,u+,u- >= 0,   min 1'u+ + 1'u-.
- optimum = 0  => restricted cone feasible.
- optimum > 0  => dual gives a separator UNLESS pricing finds a missing column.
Dual:  max b'y  s.t.  A_j' y <= 0 (j∈J),  -1 <= y_i <= 1.  Pricing seeks a column with A_j' y > 0
(= negative reduced cost in Phase-I primal convention).

## 2. Transpose-pricing oracle (the core accelerator)
Quotient reduction by Ga is the linear map  R(F) = (rem_a(F), quo_a(F)).
For dual y = (y_rem, y_quo), the score of a face column F is
    <y_rem, rem_a(F)> + <y_quo, quo_a(F)> = <R^T y, F>.
So compute ONCE:  W_face := R^T (y_rem, y_quo).  Then for every unreduced face family column
F = P_fam * m:  score(m) = <W_face, P_fam m>.  For lift columns: score(M) = <y_quo, M>.
This avoids constructing quotient columns for all candidates.

### 2.1 Computing R^T y
Polynomial division by monic Ga# is TRIANGULAR in the chosen monomial order. Each full coefficient
row's reduction contributes to a remainder row OR a quotient row plus recursive subtractions. The
transpose map = replay that triangular elimination BACKWARDS.
Recipe: store the exact reduction trace once per chart/dominant: e_r -> (rem(e_r), quo(e_r)). Given
dual y, compute W_face = R^T y by sparse accumulation from the trace; price face families by sparse
convolution against W_face. Much smaller than materializing R(F_j) for all F_j.

### 2.2 Pricing face-pair families (PAIR CLOSURE — fixes capped-infeasible)
For each non-dominant generator G_b, pricing must be PAIR CLOSED: G_b*m AND (Ga - G_b)*m together.
    s1(m) = <W_face, G_b m>,   s2(m) = <W_face, (Ga - G_b) m>.
Add the pair if max(s1,s2) > 0 (in practice add BOTH columns whenever one violates). This avoids the
capped-infeasible behavior caused by missing the complementary dominance-delta partner.

### 2.3 Pricing lift families
score(m) = <y_quo, P_fam m>. The lift cone MUST include: base degree <=9; all G_i q_i INCLUDING
Ga q_a; all (Ga - G_b) r_b; band columns. Including Ga in the lift is ESSENTIAL — it creates Ga^2
in the expanded certificate.

## 3. Restricted-master + pricing loop
Init seed (small but robust):
- face: all base columns whose reduced remainder touches a nonzero row of rem(P); pair-closed
  G_b*m,(Ga-G_b)*m multiplier degree <=3; band degree <=4; columns used by lower-tier successful
  certs in neighboring charts.
- lift: base degree <=5; generator/delta degree <=3; band degree <=4; include Ga q lift from start.
- artificial columns for every quotient row.
Iterate: solve restricted Phase-I in FLOAT -> extract dual y -> price face (W_face=R^T y) + lift
(y_quo) -> add columns with exact positive score.
Add policy: per family top 256 (hard 512); global cap/iter 4096 (hard 8192); pair closure required;
lift quota >= 25% of additions. Repeat until Phase-I obj = 0 OR no positive priced column remains.
Dual stabilization (heuristic only): ỹ = 0.7 y_old + 0.3 y_new; price BOTH raw y_new and ỹ, add
union of positive columns. Every added column exact-verified by recomputing its score rationally.

## 4. Exactness protocol
Feasibility: when restricted master reaches float Phase-I obj 0 -> solve restricted system EXACTLY
(CRT/Markowitz); verify A_J x = b, x>=0; expand F = Σ α_j F_j, M = Σ β_k M_k; emit ordinary
expanded ConeCert P = F + Ga*M. Final checker does NOT trust the quotient LP.
If exact replay gives small residual defects: keep columns; add exact residual rows to Phase-I row
basis; reprice with the exact residual dual; add exact-positive-score columns; repeat. Do NOT restart.

## 5. Exact infeasibility / Farkas certificate (DECISIVE FALSIFIER)
If restricted Phase-I optimum > 0 and pricing finds NO violated column, produce a Farkas cert:
    ∃ y: A_j' y <= 0 ∀j, b'y > 0   (j over ALL uncapped face + lift columns).
Emit a PRICING certificate (not a listing of all columns):
    dual vector y over quotient rows; rational proof b'y > 0;
    per face family: adjoint pricing polynomial W_face + proof all allowed multiplier scores <= 0;
    per lift family: pricing polynomial W_lift + proof all allowed multiplier scores <= 0.
Checker verifies: exact dual y; exact b'y > 0; for every finite multiplier domain every score <= 0
(enumerate the multiplier exponent list — small vs materializing quotient rows; enumerating ~80k
scalar scores for the final Farkas cert is acceptable). If it verifies => decisive obstruction for
that chart row (surface + STOP).

## 6. Pricing oracle I/O
Input per chart/dominant: Ga_sharp; target P; reduction trace R; family list {faceBase,
faceGenerators G_b, faceDeltas Ga-G_b, faceBand, liftBase, liftGenerators G_i, liftDeltas Ga-G_b,
liftBand}; allowed multiplier domains.
price(y):
  W_face = transposeReduce(y_rem, y_quo)
  for each face family Ffam: score(m)=<W_face, Ffam*m>; return top positive m
  for each lift family Lfam: score(m)=<y_quo, Lfam*m>; return top positive m
Efficient scoring (monomial NF, multiply by m shifts exponents):
  score(m) = Σ_{terms t in P_fam} coeff(t) * W[exp(m)+exp(t)]
(Bernstein basis: precompute the product stencil per family polynomial.)

## 7. Concrete Codex recipe
Phase 0 (quotient preprocessing per hard row): build Ga_sharp; reduction trace R; remP, quoP;
  family descriptors.
Phase 1 (seed RMP): face = base touching remP + pair-closed gen/delta deg<=3 + band deg<=4;
  lift = base deg<=5 + all gen/delta deg<=3 + band deg<=4 + include Ga generator lift.
Phase 2 (CG loop): max_iterations=60; add_per_family=256 (hard 512); add_global_cap=4096 (hard
  8192); pair_closure=required; dual_stabilization = 0.7 prev + 0.3 curr; exact_score_threshold=0;
  float_score_threshold=1e-9.
Phase 3 (exact solve): when float obj = 0 or < 1e-9 -> solve selected columns exactly; if exact
  feasible emit expanded ConeCert; else add exact negative residual rows + reprice.
Phase 4 (Farkas): if no priced columns and Phase-I positive -> exactify dual; verify family pricing
  <= 0; verify b_dot_y > 0; emit Farkas.

## 8. Row favorability
MOST favored: k4/G3 (exact target case — tier2 capped-infeasible + tier3 timeout = classic
  missing-column; pair-closed quotient pricing should help strongly); k6/G1 (dominant-generator
  face row — Ga-lift + pair closure is the intended tool); k3/G6 (face-dominance degeneracy).
MODERATE: k0/G7 (expect lift pricing to dominate — may need more lift columns / secondary split);
  k9/F6 (F6-type degeneracy — source-sanitize first, then CG); k4/F2 (thin margin-zero faces — try
  margin-zero exact replay / small-basis route FIRST, else CG).

## 9. Falsifier-first
If CG produces an exact Farkas cert (A_j'y<=0 ∀j, b'y>0) the FULL face-split cone for that chart
row is infeasible = decisive obstruction, not a timeout. If no Farkas appears and feasible columns
keep pricing positive, it is solver scaling and CG eventually finds enough columns.

## 10. Summary
Use quotient Phase-I column generation with transpose pricing, not brute-force uncapped LP.
Critical pieces: transpose quotient reduction R^T y; pair-closed face pricing; lift pricing
including Ga; exact restricted solve; exact family-pricing Farkas cert if infeasible. Final proof
artifact unchanged: P = F + Ga*M, expanded and checked exactly by the ordinary ConeCert checker.
