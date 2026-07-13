# Approach Registry

| ID | Mechanism | Status | Sharp frontier | Exact falsifier |
|---|---|---|---|---|
| A00 | Novelty sweep | ACTIVE | classify prior one-exception results | literature citations |
| A01 | Exceptional involution | OPEN | quantify paired/unpaired structure | exact census |
| A02 | Sidon stability | OPEN | sharp uniform stability at 2/sqrt(3) | reflected families |
| A03 | Interval counts | OPEN | continuous optimum 4/3 | ILP/census |
| A04 | Difference multiplicities | OPEN | characterize permitted repetitions | exhaustive sets |
| A05 | Energy/Fourier | OPEN | remove exceptional-energy spike | exact statistics |
| A06 | Graph/hypergraph | OPEN | exact equivalence and sharp packing | SAT/ILP |
| A07 | Construction/disproof | OPEN | beat 2/sqrt(3) | exact admissibility |
| A08 | Compression/exchange | OPEN | reflection without loss | local-search gate |
| A09 | Partial-symmetric Cayley graph | OPEN | sharpen K_{2,3}-free interval count to 4/3 | exact graph census |

## Wave-1 mechanism registry, 2026-07-12

- K2,3 / occupied Cayley slice: ALIVE. Exact inequality and small-exception theorem; frontier is support-duplicate product. File P02_k23_interval.md.
- Rank-window differences: PARTIAL. Proves target for reflected fraction <=1-1/sqrt(2); sharp barrier in high-reflection regime. File P03_windowed_differences.md.
- Energy/Fourier moments: CLOSED as a standalone route. Exact identities survive, but scalar moments lose positional information. File P04_energy_fourier.md.
- One-point compression: DEAD. Exact N=10 extremizer admits no closure-improving exchange even with exception relocation. File P06_compression.md.
- Signed-ruler coupled labels: ALIVE. Needs use of d_ij+c_ij=e_i; simple range separation is false. Assigned P07.
- Hybrid packing H<=N+o(N): ALIVE but unproved. Assigned P08.
- Unpaired residual reduction: ALIVE. Assigned P09.

## Wave-2 mechanism registry, 2026-07-12

- P02 centered support-defect product: OPEN. The P23 duplicate-only falsifier did not compute Z_H=D_H-Q_H; its prior DEAD classification is withdrawn.
- P22 gap-defect tradeoff: PARTIAL. Exact residual-safe inequality kH-M_H >= (4Z_H+2J_H)/m_H(C), averaged and colored-onset forms; sharp on Erdos-Freud but still needs incidence/phase control.
- P24 endpoint shadow: PARTIAL. Exact ordered shadow bound B(M-e_j)<=tau(d)<=R-d/2-F(M-d)-q+F(d)+1 for each represented distance d=e_j-e_i.
- P19 Bose-Chowla top-third localization: DEAD. Exact algebraic lifts violate localization while preserving the signed-ruler conditions.
- P26 Singer carry holes: CLOSED as an infinite counterconstruction. P29+P35 force every affine Singer hole to d=o(v) and coefficient 3. The analogous Bose-Chowla statement is not proved.
- P26 asymptotic SCG frontier: DEAD. Uniform STM excludes macroscopic affine Singer carry holes for all sufficiently large q.
- P27 Singer carry mixing: PROVED. P29+P35 give uniform STM; the Singer construction coefficient tends to 3.
- P20 centered N^(2/3) finite-correction profile: OPEN. Exact p=503 centered margin is -305894457730641; the earlier duplicate-only falsifier is invalid.
- P16 residue/quotient phase: DEAD as a marginal route. Exact subcritical countermodels survive residue histograms, aggregate wraps, moments through degree 3, and polynomially weighted modulus averages.
- P26 corrected mixing: RESOLVED by STM. Exact tetrahedral correlation plus P29+P35 gives O(q^(3/2) log^5 q) discrepancy and Singer drift to coefficient 3.
- CORRECTION P23/P20: P23 computed duplicate weight D_H, not centered Z_H=D_H-Q_H. Its unconditional centered-product falsifier claim is withdrawn; exact p=503 has Q_H>D_H and satisfies C20. P20 C20 is OPEN again.
- P33 centered tangent-gap factorization: PROVED REDUCTION. C20 is automatic for 3M_H<=2N; for 3M_H>=2N it follows from the explicit linear inequality LG33 (Psi_H<=0), which remains open.
- P50 LG33 sharp envelope: PROVED SUBCASE. The exact gap identity makes
  `8NZ_H<=Esharp_H` sufficient; at prescribed `H`, `4Z_H<=3N` suffices.
  The 78 census and 151 stored residual profiles remain outside this proof.
- P28 affine probability: CLOSED as an ordinary-moment route. Exact mean is positive Theta(q^2); variance is eight-Gauss-sum and standard tail inequalities do not force zeros.
- P29/P35 shifted four-Gauss-sum and simplex completion: PROVED. Correct direct Katz type-(3,1) trace gives 12q^(3/2); explicit four-piece completion gives STM with K=5.
- q167 complete affine Singer scan: FINITE RECORD. 14,028 unit classes, 2,356,704 cuts, best M/p^2=9091/3528; literal admissibility and E_C(d)=0 independently checked.
- P34 modular construction obstruction: PROVED. Same-parity modular Sidon plus modular 3E-disjointness forces 2h>=3p^2-p+2; finite-field parabolas and Welch graphs are saturated; only literal carry constructions remain.

- P37b translate blocks: PROVED exact incidence lemma, but its rational
  coefficient-(2+g) profiles show P13 plus all continuum P24 shadow
  inequalities are insufficient. The next lemma must use integer carry phase
  or equal-three-sum partition structure.
- P44 raw carry counts: DEAD as a small-error statistic. On 37 exact large
  subcritical profiles, total overlap and the unweighted level-one minus
  level-two count are both (Theta(p^2)); positional or
  multiplicity-weighted data are required.
- P45 signed carry fibers: PROVED IDENTITY / DEAD bound. Exact identity
  `delta=M1+M2-u+a0+c0` holds, but `{2,4,5}` and `{2,3,5}` have the same
  unsigned data and opposite carry imbalance. Placement-sensitive phase is
  still required.
- P49 known-theorem bridge: DEAD. Strong cyclic 4-independence has only the
  proved coefficient-two consequence; coefficient three is conjectural, and
  reduction modulo `max(E)+1` fails on `{1,7,11}`.
- GPT delta correction: PROVED. The reflected target is
  `delta_+=o(p^2)` because `max(E)=3p^2-p+b-2delta`. A prime family with
  `delta/p^2 -> -3/2` falsifies the unnecessary two-sided formulation but
  satisfies the desired endpoint bound.
- P46 carry statistics: PROVED IDENTITIES / DEAD carry-only route.
  `delta=|I|+CS+CD-H0`; the exact set `{1,3,9,13}` at `h=14,b=1` has
  positive defect entirely in folds and zero overlap. Collision terms cannot
  be omitted.
- Folded sum count: DEAD EVEN WITH THE HOLE. P53 gives a positive-defect
  Sidon ruler with `p=25,CS=49>47`, killing the unconditioned statement, but
  it has both `-1,-2 in 3B-B`; P75 later gives a positive-defect literal-hole
  counterexample.
- Direct carry-graph KST: DEAD. A zero-fold Bose profile requires 34 and 17
  deletions to remove all `C_4`s, versus correction budget 7.
- Fold-repair correction: DEAD at both stated constants. A `p=17` Bose
  translation kills the linear repair. P58's `p=14` Singer lift has
  `delta=105`, `CS=CD=0`, and `105^2>4*14^3`, killing the constant-2
  `p^(3/2)` repair. An unspecified-constant `O(p^(3/2))` bound is OPEN.
- P62 Bose natural modulus: FINITE AUDIT / OPEN ASYMPTOTIC. Literal
  zero-fold holes occur for every tested prime power through `q=23`, but
  none among all 115,130 affine lifts for `25<=q<=64`.
- P48/P55 guarded recursion: PROVED OBSTRUCTION. Internal Sidonicity plus
  cross-disjoint differences forces component span sum `(1-o(1))p^2`; the
  strict range guards then force endpoint coefficient at least five.
- P51 barycentric partitions: PROVED PARTIAL. Balanced supports of equal
  triple sums have exact mean `x/3` and a mod-3 size constraint, yielding a
  much smaller integer subset-sum capacity. Coupling capacities across sums
  remains open.
- P59 block-count barycenter coupling: DEAD. Maximum capacity witnesses can
  overlap in five marks against block-count bound four; actual partition
  supports fail too. A different cross-column invariant is required.
- P52 spectral staircase: PROVED PARTIAL. Positive palindromic factor and
  tail domination hold exactly. Single-peak slope is DEAD on
  `Z={0,3,4},G=2`; curvature-reversal span remains open.
- P60 curvature span: CLOSED unconditionally. Exact tail and fixed-variation
  identities hold, but doubled Erdos--Turan rulers and finite certificates
  kill reversal, tail-floor, Hankel, and zero-count bounds. Only the
  width-compensated defect remains meaningful.
- P68 hole-neighborhood smoothing: DEAD. A valid `p=5` profile has a run of
  17 missing shifts, and 54,458 exact small hard holes lie in runs of at
  least three.
- P56 reflected completion: PROVED REDUCTION. At most one residual pair is
  deleted per virtual difference collision. The remaining frontier is an
  upper bound on completion defect beta and reflection shift tau.
- P61 two-scale completion: PROVED REDUCTION. Applying the reflected bound
  to both the core and repaired completion cancels `tau` exactly and handles
  positive-density residuals when the collision ratio `b/k` is small.
  The remaining completion frontier is quantitative control of `b/k`.
- P47 generic polynomial phase: DEAD. Equal modulus at every circle point,
  disjoint supports, full autocorrelation equality, nonnegative coefficients,
  and one exact profile admit coefficient-two families. Only the common
  Sidon Newman factor, both profiles, and one-sided arc orientation remain.
- P64 LG33 reflected residual: PROVED REFORMULATION. On separated dense
  reflected sets, LG33 implies the sharp coefficient-three center bound;
  it is not an easier local-gap bridge. The one-label strengthening is DEAD.
- P66 unrestricted completion charge: OPEN, with exact support. The bound
  `2beta<=h_S` has zero failures among all 35,776,005 normalized admissible
  sets of span at most 55, including 18,800,840 cases beyond P61.2.
- P63 natural Bose carry mixing: CANDIDATE THEOREM / REFEREE PENDING. Exact
  finite auditors pass and holes disappear from q=25 in the tested family;
  the asymptotic character-sheaf estimate still needs independent review.
- P63 referee disposition: PROVED after repair. Split-torus local monodromy
  and a uniform tame Betti bound validate the `(1/6+o(1))q^2` count. The
  natural-modulus affine Bose counterfamily lane is CLOSED.
- P65 hole-restricted fold bound: DEAD. It had zero failures in 10,118,486
  earlier valid translations, but P75 supplies a positive-defect literal-hole
  counterexample. The stronger p-1 bound and graph shortcuts are also dead.
- P67 pairwise barycenter coupling: DEAD. An infinite valid family has two
  q-block fibers intersecting in `3q-1` marks, so no pairwise bound with an
  `o(q)` correction can work.
- P69 fold-or-Fourier dichotomy: PROVED REDUCTION. Positive compensated
  defect forces quadratic fold loss or an almost-quadratic fourth-order
  Fourier coefficient. Neither term is universally bounded yet.
- P70 Ruzsa all-cut extension: FINITE RECORD. Five of seven primes from 263
  to 293 have a best natural cut below 14/5, with minimum 6707/2430 at p=271.
  Infinite persistence and uniform carry mixing remain open.
- P70 uniform Ruzsa carry mixing: PROVED after referee repair. The exact
  asymptotic is `(p^2/12)(1-t/n)^3+o(p^2)` uniformly in all natural cuts and
  shifts. The finite Ruzsa holes cannot yield a fixed sub-three family.
- P71 affine fold lift: UNRESTRICTED FORM DEAD. A p=25
  literal-hole lift has `C_S=49>47`, but its defect is `delta=-62`; generally
  `delta_q=926-494q<0` for q>=2. Thus it does not test the needed
  `delta>0 => C_S<=2p-3` statement; P75 later falsifies that hard form.
  The fixed-b=2 form is undecided but no longer sufficient by itself.
- P75 hard positive-defect folds: DEAD. Adjoining 639 to the P71 ruler gives
  `(p,h,b,delta,C_S)=(26,988,1,14,51)` with a literal hole and
  `51>49=2p-3`. Exact verifier: `compute/p75/verify_hard_fold_counterexample.py`.
- P66 mixed completion slack: OPEN SHARP FRONTIER. On all 30,899,206
  residual cases through span 55, `w<=h_D` and
  `2v+w+u<=|D_R|+h_D` have zero failures and imply `2beta<=h_S`.
  The simpler `2v<=|D_R|` is DEAD with 136 exact failures.
- P74 asymptotic completion charge: PROVED. A genuine Sidon subset of size
  `p+u+delta` yields enough difference holes to prove `2beta<=h_S`
  for every endpoint-normalized admissible set of size at least 1726.
  P76 proves this is insufficient for the full P61 assembly.
  GPT-Pro's exact `k`-window refinement of the same Sidon subsystem was
  independently checked: together with the P61.2 easy range it leaves 259
  parameter pairs, all with `p<=7,u<=48`. This is a valid finite reduction
  but is superseded by P74 and does not repair the P76 assembly obstruction.
- P73 completion overlap: PROVED FINITE REDUCTION after referee repair. The exact
  identity `2beta=|J intersect S|+|K intersect(S union J)|` reduces the
  unrestricted charge to 35 parameter boxes, with at most 29 points and
  span at most 567. The repaired parameter checker finishes in 1.3 seconds.
- P72 centered completion slack: PROVED `w<=h_D`. The stronger mixed
  inequality remains unproved, and centered inclusion-exclusion cannot see
  its `v` term; P73/P74 supersede it for the standalone completion charge.
- P76 P61/P74 assembly: DEAD. The complete normalized relaxation has
  minimum `L/k^2=3/8` at `u/k=b/k=1-1/sqrt(2)`. An exact integer parameter
  ray satisfies both P61 branches, difference packing, and P74 charge.
- P77 one-fold Fourier inequality: PROVED REDUCTION. Unconditionally,
  `L_h^5 Lambda >= (E-p+b-10C_S)_+/128`. Its proposed fold-free corollary
  depended on P65 and is dead by P75; a joint fold/phase estimate is needed.
- P79 fold bicliques: K2,4 AND K4,4 ROUTES DEAD. Exact positive-defect
  literal-hole rows contain K5,5; maximum pair codegree is 12. No K6,6 was
  found in 165,225 rows, leaving K6,6-freeness as an unproved KST target.
- P80 universal sumset-translate bound: DEAD. An endpoint-normalized
  29-point Sidon ruler at h=640 has `C_S=58>57=2p-1`. It has 89 and 97
  literal-hole collisions for b=1,2, so the hole remains essential.
- P82 fold-hypergraph removal: PROVED REDUCTION. Endpoint folds form a
  linear 3-partite 3-graph. If `C_S>=epsilon*p^2`, triangle removal forces
  `Omega_epsilon(p^3)` loose fold triangles. The P75 row has exactly 25,
  so the remaining target is a phase-sensitive `T_F=o(p^3)` theorem.
- P83 loose-triangle phase normal form: PROVED PARTIAL. Every loose triangle
  injects into `(a,c,u)` with `a<=c<u`, giving `T_F<=binom(p+1,3)`, and into
  three ordered literal-hole labels. The P75 row has only 3/25 natural
  in-range endpoint targets; a 7-point row falsifies the fourth label `d-R`.
- P84 phase Fourier tensor: PROVED IDENTITIES / CANDIDATE. It gives exact
  polynomial formulas for the hole, weighted folds, and loose-triangle
  trace. The closing candidate `T_F<=C_S` has zero failures on 465,115
  exact positive-defect hole rows but has no proof or injection yet.
  P94 independently extends the gate to 313,863 archived translation holes
  and 242 parity-lift insertions with zero failures; max ratio is `116/142`.
  The stronger componentwise form also has zero failures on all three exact
  domains: each loose-triangle component has at most as many edges as folds.
  P100 removes the defect and hole hypotheses entirely on every width-30
  endpoint translation: total, componentwise, color-prefix, and color-suffix
  forms all have zero failures in 791,869 exact systems.
  P88 falsifies every pure-order form at p=60: `C_S=182<T_F=200`, with
  component excess 35 and negative prefix/suffix slacks. That row fails both
  literal holes; the phase-conditioned C84 remains unfalsified.
  P101 exposes the corrected global target `T_F<=C_S+V_b`, where `V_b`
  counts folds whose low sum plus b is a represented difference. It has zero
  failures on 1,587,908 unrestricted exact rows. Its componentwise form is
  false, but the literal hole sets `V_b=0` and recovers C84.
- P90 phase literature: CLOSED WITH NO BRIDGE. C84 is the defect of a proper
  coloring from being strong, and loose triangles are triforces. Existing
  induced-matching, removal, triforce, and dense-Sidon theorems lose phase
  or assume the desired inducedness. Prendiville yields only phase-free
  `Omega(p^4)` equal-three-sum sextuples.
- P89 ordered stencil count: CLOSED AS INSUFFICIENT. Five P87 holes are
  fold-local and the sixth is absent for every shared triple. An infinite
  translated Singer family has positive defect and the literal hole while
  every stencil value lies below `min B`; occupancy cannot save a power.
- P95 support-fold Hall injection: DEAD. On the P94 ratio-maximizing row,
  116 triangles have maximum support-fold matching 105; a Hall witness has
  72 triangles and 61 neighboring folds. C84 needs a global charge.
- P93 leaf/prefix charges: DEAD. The tight component peels to a 75-triangle
  core on 64 folds, and seven archived literal holes violate the shared-high
  prefix bound. Collision-corrected prefix/suffix forms also fail on P88
  translations. Only a nonlocal total charge remains.
- P92 one-step hexagon charge: DEAD. A valid `p=138`, `delta=88` row has
  eight triangles but only seven fold labels reachable using all three P83
  labels plus every signed represented-hexagon step. C84 still survives.
- P85 generic stability tools: CLOSED AS INSUFFICIENT. Removal gives P82,
  while BSG, DRC, and rank-grid corners lose the endpoint phase or miss the
  required density scale. P75 falsifies all pointwise completion bridges.
- P86 dense loose-triangle search: FINITE RECORD. An exact 16-worker scan of
  1,613,120 translations and 312,094 insertion candidates found no cubic
  family. Reflection changes P75 from `T_F=25` to 37 with scalar data fixed.
- P87 punctured-center incidence: PROVED PARTIAL. Every loose triangle is a
  three-arm Sidon grid around `K notin B` with six phase-locked holes. The
  exact center-degree bound and eight sign chambers still permit cubic mass.
- P91 four-part K4 removal: DEAD. The P75 fold shadow has 106 K4s but only
  51 canonical folds; 55 noncanonical K4s survive the literal hole.

- P97 residual-interval matching: DEAD WITHOUT THE JOINT LITERAL-HOLE GATE.
  Every canonical or loose shadow triple `(a,c,u)` receives the interval
  between `u-a-c-b` and `h-b-u`; each fold supplies slots at `h-b-v` and
  `h-b-u`, plus a lower slot when `a+c+b` is a represented difference.
  Matching all intervals implies `T_F<=C_S+V_b`. Exact rechecks have zero
  failures on 1,583,738 width-30 rows and the archived literal-hole domains.
  P105 kills the negative-defect statement. P106 kills positive defect alone
  at `(p,h,b,delta,C_S,T_F,V_b)=(67,6572,1,129,199,221,20)`, with a minimal
  Hall window containing 411 intervals and 410 slots. P106 is not a literal
  hole, so only the joint positive-defect/literal-hole specialization remains
  logically open; it is no longer the preferred frontier.
- P98 componentwise C84: DEAD UNDER ALL GATES. Deleting `4740` from P94's
  tight row gives `p=103,delta=1379,V_1=0` and a component with 110 loose
  triangles on 109 folds. Exact mutation and CP-SAT audits add 3,014,932
  unrestricted and 27,074 full-gate evaluations with no positive-defect
  global corrected-C84 failure.
- P103 triangle-relation matroid charge: DEAD. The GF(2) nullity bound
  `T_F-rank<=V_b` fails on 19 P88 translations; the worst exact deficit is
  nine at `gamma=41,b=2`.
- P104 per-color strong-edge charge: DEAD. The proposed per-color induced
  and pseudoforest bounds fail on 2,196 and 2,302 exact rows respectively;
  the worst residual is 17.
- P105 unrestricted corrected C84: DEAD. The exact 57-mark parity-lifted
  Sidon row above satisfies the literal hole and `T_F=160>C_S=159`, but has
  negative defect. It does not falsify the hard-regime theorem required for
  Problem 864.
- P103/P110 weighted global relation matrix: DEAD GLOBALLY. A loose triangle is sent
  to its three-fold incidence vector together with the two formal six-mark
  relations `L1,L2` and their phase moments `dL1,dL2`. Full row rank would
  give `T_F<=C_S+4p=O(p^2)`, sufficient for P82 without a hole hypothesis.
  P110 gives 20 exact dimension falsifiers. The smallest has
  `(p,C_S,T_F)=(104,579,1104)` and `T_F>C_S+4p=995`; hence no matrix in only
  those `C_S+4p` columns can have independent rows. The surviving filtered
  candidate partitions triangles by their minimum phase label and asks for
  independence within each class; it remains unproved.
- P109 canonical residual-component closure: DEAD. In 304 exact positive-
  defect literal-hole rows through width 30, a loose interval bridges two
  disjoint components of the canonical residual intervals. The first is
  `B={8,10,15,23,24,27},h=28,b=2,delta=24`, with supporting intervals
  `[3,3],[-1,2],[2,2]`. RM97 cannot be reduced to canonical interval
  components.
- P107 positive-defect falsifier search: FINITE RECORD. Exact CP-SAT closes
  every hard-regime endpoint-preserving subset of P88 and every deletion of
  at most five P94 marks; nine mutation lanes examine 3,384,139 labelled
  candidates and 5,869 full-gate rows. There are zero P101 or RM97 failures.
- P111 abstract fold-only relation matrix: DEAD. A 20-vertex, 51-edge
  ordered linear rooted 3-graph has rank 50 for `(S,E,dE)`. Thus P103's
  formal mark relations are essential; order and linearity alone do not
  prove the `O(p^2)` triangle bound.
- P112 short arithmetic relation matrix: DEAD BY DIMENSION. The rows `(S,L1,dL1)` live
  in `C_S+2p` columns and have full rank over GF(1000003) on every one of
  1,583,738 width-30 rows, all 2,085 P88 translations, P75, P94, P98, and
  P105, but the P110 rows have `T_F>C_S+4p`, hence a fortiori
  `T_F>C_S+2p`. The finite full-rank census did not cover the dense dimension
  obstruction. The exact audit hash begins 4864EC9F.
- P113 support-plus-difference Hall: OPEN. Match a loose triangle to one of
  its three supporting folds or one of the three represented pairwise
  differences of their phase labels. This gives
  `T_F<=C_S+binom(p,2)=O(p^2)`. There are zero failures on 791,869 width-30
  fold systems, all P88 translations, and the named hard rows. Difference-
  only matching fails three P88 translations, so fold resources are needed.
- P114 endpoint-plus-span Hall: DEAD ABSTRACTLY. A 13-vertex linear proper-
  middle triple system has 20 demands but matching size 19 to outer
  endpoints plus span lengths. Any proof of P113 must retain all three
  supports/differences or use fold arithmetic.
- P115 global BC108 color budget: DEAD. The exact P110 endpoint ruler
  `(p,h,delta,C_S,T_F,V_1,E_+)=(104,9821,6352,579,1104,314,598)` has
  `E_+>p+V_1` by 180. It is not a literal hole; its parity lift is a literal
  hole but has negative defect. Thus only the joint live specialization is
  untouched.
- P122 live color-excess/difference Hall: OPEN. For each color `u`, demand
  `(t_u-n_u)_+` distinct arm-pair differences `|v_i-v_j|`. This weaker Hall
  statement would give `T_F<=C_S+binom(p,2)=O(p^2)`. It passes all mandatory
  live rows and all 1,037 positive-defect literal-hole triangle rows through
  width 30. It fails 19 of 20 dense P110 systems, all outside the joint gate.
- P81 outer `K6,6` exclusion: OPEN ONLY WITH POSITIVE DEFECT. Exact searches
  find no hard-regime `K6,6`, but an 85-mark parity-separated literal-hole
  ruler with negative defect realizes one. Local nesting and the hole alone
  cannot prove the exclusion.
