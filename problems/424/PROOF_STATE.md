# Proof state

## Target

Let `A` be the least set of positive integers containing `2,3` and satisfying
`xy-1 in A` for distinct `x,y in A`. Decide whether its lower density is positive.

## Accepted results

1. `A` is contained in residues `0,2 mod 3`; upper density is at most `2/3`.
2. For `n>=4`, membership is decided exactly by `n+1=dq` with distinct `d,q in A`.
3. Exact block coding gives, for every `X>=9`,
   `A(X) >= (1/6)(X/9)^(log 6 / log 30)`.
4. Exact independent censuses agree through `10^7`; `A(10^8)=51,899,129`.
5. The frozen `{2,3,5}` affine subsystem has density `0.18222202754` at `10^11`;
   no positive- or zero-density theorem for it is proved.
6. Every finite globally residue-decodable block automaton is subcritical:
   its exponent-one weighted spectral radius is strictly below one.
7. Every periodic-domain residue `qZ+r` in the tested composition-cover model
   must satisfy `d | gcd(q,r+2)` for some licensed multiplier `d`.
8. Raw polynomial growth plus dynamic multipliers cannot bootstrap density:
   the distinct-input closure of `{9,10}` has a polynomial lower bound but
   a proved sublinear upper bound.
9. Distinct affine words collide exactly:
   `T_322255(x)=T_255232(x)=600x-381`.

## Frontier

A successful proof must use arithmetic special to seeds `2,3` and prove a
target-specific expansion/collision inequality for the distinct product set

`A = {2,3} disjoint_union ((A restricted-times A)-1)`.

Fixed alphabets, global periodic exact decoding, raw word entropy, and a
generic power-law bootstrap are insufficient.

## Verdict

NOT SOLVED. No explicit `c>0,X0` and no zero-density proof were obtained.

## Missing-set structure (2026-07-13, claude_missing_analysis.py SHA 6e071114…, B=10^7; accepted as data)
- Per-decade missing fraction DECAYS: 0.68 / 0.62 / 0.51 / 0.39 / 0.304 / 0.251 (last = (10^6,10^7]).
  With Codex's 10^8 count, decade (10^7,10^8] ≈ 0.218. Decay ratios 0.77, 0.78, 0.83, 0.87 ≈ log(B)/log(10B)
  ⟹ **O1 (working fit): missing fraction ≈ C / log B with C ≈ 1.6 (log10)** — consistent with d(G) = 2/3
  and log-slow convergence (explains the census climb). NOT proof; guides the route.
- Longest consecutive-allowed missing run = 13, ending at 192 (the early [173,194] window); largest missing
  element at 10^7 = 9,999,996 (≡ 0 mod 12) — missing persists to the boundary but thins.
- **O2 (KEY): residue asymmetry mod 9** — missing counts {0: 393k, 2: 393k, 3: 445k, 5: 62k, 6: 378k,
  8: 43k}: classes 5 and 8 mod 9 are ~7-9x LESS missing than the rest ⟹ G nearly fills n ≡ 5, 8 (mod 9)
  already at 10^7. Mechanism guess: n ≡ 8 mod 9 ⟺ n+1 ≡ 0 mod 9 = product of two multiples of 3; G is rich
  in multiples of 3, so the pair supply is huge.
- **O3: parity/mod-12** — missing heavy at n ≡ 0, 6 (mod 12) (even multiples of 3: 525k/576k), light at
  5 (9k), 9 (40k), 3 (75k) ⟹ odd classes fill much faster (evens need odd*odd products).
- **ROUTE R-A (registered): class-by-class filling via product covering.** First target theorem:
  "every sufficiently large n ≡ 8 (mod 9) lies in G" ⟸ every large multiple of 9 factors as ab with
  a ≠ b, a,b ∈ G (e.g. both ≡ 0 mod 3). Reduces the density question to a MULTIPLICATIVE-BASIS statement
  for G ∩ 3Z (Erdős-multiplication-table flavored). If one full residue class ⊆ G eventually, d(G) ≥ 1/9 > 0
  answers the problem; then bootstrap other classes.

## R-A covering gate (2026-07-13, claude_ra_covering_gate.py SHA 179cc21f…, B=10^6; accepted as data)
- IDENTITY CHECK: covered(n) [∃ a≠b ∈ G, ab = n+1] is EXACTLY membership n ∈ G for n ≥ 4 (definition of
  the closure) — gate numbers agree with the missing-set analysis (class-8 missing 7.9% @10^6 vs 3.87%
  @10^7 ✓ consistent decay).
- **O4: class-8 (mod 9) missing fraction HALVES per decade**: 44% / 27.9% / 14.9% / 7.0% (decades up to
  10^6), 3.9% @10^7 — geometric-ish (ratios 0.63, 0.53, 0.47, ~0.55), FASTER than 1/log. Class 5 similar
  but slower (50/35/20/9.9%).
- Structural reading of "uncovered": n+1 = 9m is uncovered iff EVERY divisor pair (a,b) with the allowed
  sign pattern (both ≡ 0 mod 3, or a ≡ 2 mod 3 with b ≡ 0 mod 9) has a G-hole. Divisors ≡ 1 mod 3 are
  PERMANENTLY unusable (G1). So R-A's target theorem splits: (i) arithmetic supply — a.e. 9m has "many"
  allowed divisor pairs (classical divisors-in-residue-classes); (ii) hole-avoidance — G's holes are too
  thin (decaying per O1/O4) to block all pairs; a self-improving/bootstrap estimate suggests itself
  (holes thin ⟹ more covered ⟹ holes thinner). REGISTERED as the R-A proof skeleton.

## R1 accepted (2026-07-13, writeup/R1_GPTPRO56.md) — route table restructured
- R-A splits: R-A1 eventual-all/two-unbounded = DEAD (prime quotient); R-A2 eventual-all-with-3 = PARKED
  (needs prime theorem: 3p in G for all large p = 1 mod 3); R-A3 almost-all/positive-fraction = LIVE via
  smooth-rough certificate (21)/(54) or energy gate (50).
- NEW R-B: exact class-8 identity 9m-1 in G iff m in T^(2) union T9*V (56).
- NEW R-C (PRIMARY): cross-colour bilinear d(G0*G2) > 0 via variable-scale multiplicative energy —
  auto-distinct, no scaling loss, obstruction-compatible. Target: reservoirs U_X in G0, V_X in G2 with
  E-times(U_X,V_X) <= kappa*|U|^2|V|^2/X.
- BARRIERS ADDED: density thresholds (any c<1) useless (idempotent v_q models; the 32/63 twin of 0.17);
  d=1 does not give cofinite; balanced blocks dead (Ford); polynomial-exponent-<1 towers have density-0
  self-products — the affine tower cannot be the covering core.
- MEMBERSHIP RECURSION (40) supersedes truncated closure for census (exact; factor n+1).
- Literature to verify at gate: Bettin-Koukoulopoulos-Sanna; Ford multiplication-table exponent.

## 2026-07-13 Claude tick: Gate-3 ALL-PASS + first L9 energy table (both my exact computations)

**(G3) Gate-3 modular falsifier scan — NO modular obstruction found; saturation structure.**
compute/claude_gate3_modular_scan.py (SHA 06c7529f1fb697de4023606cf8f24d8bfad705e8328f5060238e3ea91efe8d6b),
q in 2..120 and {125,128,169,243,256,289,343,512}: for EVERY scanned q, |R_3q| = 2q exactly
(the mod-3q closure of {2,3} under rs-1 saturates to ALL classes not == 1 mod 3), hence
U_q = Z/q entirely and U_q*U_q = Z/q trivially. VERDICT: density-one/cofinite R-A forms
SURVIVE Gate-3 at every scanned modulus; the ONLY congruence obstruction visible in this
family is the mod-3 one (G1). (Pass proves nothing per R1 (46); the saturation fact itself
is a finite-check lemma candidate per M: R_M = {r : r mod 3 != 1} for 3|M.)

**(E1) First multiplicative-energy table for R-C reservoirs — energy is DIAGONAL-DOMINATED.**
compute/claude_rc_energy_probe.py (SHA 9462e017bf46fc5b08a1267987b4fa4c037daebdc4892a2cfa666fb5780d5258),
B=10^6 proven closure; U = G0 cap (Y/2,Y], V = G2 cap (Z/2,Z] (thinned only where flagged):

| Y | Z | \|U\| | \|V\| | thin | E | E/(\|U\|\|V\|) | kappa=EX/(\|U\|^2\|V\|^2) |
|---|---|-----|-----|------|---|-----------|-------|
| 10^3 | 10^3 | 57 | 74 | 1 | 4254 | 1.0085 | 239.1 |
| 10^4 | 10^4 | 712 | 999 | 1 | 747772 | 1.0513 | 147.8 |
| 10^5 | 10^5 | 8781 | 12253 | 1 | 121003357 | 1.1246 | 104.5 |
| 10^6 | 10^6 | 99959 | 3903 | 35 | 392531799 | 1.0061 | 2578.9* |
| 10^3 | 10^6 | 57 | 136590 | 1 | 8108390 | 1.0415 | 133.8 |
| 10^4 | 10^6 | 712 | 136590 | 1 | 106256268 | 1.0926 | 112.3 |

(*thin=35 inflates kappa by ~35 exactly because E ~ diagonal; the invariant number is the ratio.)
FACTS: (i) E/(|U||V|) in [1.006, 1.125] across ALL shapes tested — products of G0-window x
G2-window are nearly all DISTINCT at reachable scales (near-Sidon); (ii) balanced full-window
kappa DECREASES 239 -> 148 -> 105 (10^3 -> 10^5) because window densities of G0,G2 are still
rising; kappa ~ 4/(alpha0*alpha2) * ratio if window densities converge. (iii) CIRCULARITY
WARNING (mine): full-window reservoirs presuppose positive window density of G0,G2 — close to
the conjecture itself; unconditional tower supply is only X^0.517 and dies by tower thinness
(52)-(53). So R-C needs either (a) an unconditional reservoir family with |U||V| >> X/polylog
+ provable near-diagonal energy, or (b) a bootstrap exploiting G0*G2-1 SUBSET-OF G2
(a in G0, b in G2 => ab-1 == 2 mod 3), i.e. G2 self-expansion. This dichotomy = R2 question.

## Wave-3 energy correction (2026-07-13)
- C05 proves that every Cartesian reservoir U_X x V_X with max(U_X)max(V_X)<=X and both maxima unbounded has kappa_X -> infinity, via Ford divisor-in-interval bounds and dyadic decomposition. Independent source/range audit requested from Fable.
- Therefore the original Cartesian R-C target is retired, including balanced and unbalanced dyadic boxes.
- Surviving R-C criterion: for every sufficiently large X, find a correlated edge set E_X subset {(a,b) in G0 x G2 : ab<=X} with M_X=|E_X| and sum_n R_X(n)^2 <= K M_X^2/X. This implies lower density at least 1/K.
- The full hyperbola edge set is empirically compatible: exact kappa values at X=10^3,...,10^8 are 8.845, 7.025, 5.787, 5.209, 5.052, 5.153. This is data, not an asymptotic theorem.
- Exact frontier: prove P(X)>=cX and E(X)<=C P(X)^2/X for full hyperbola pairs, or construct a selected correlated family satisfying those two inequalities.

## Wave-3 narrowed frontiers (2026-07-13)

- C10 proves that existential multi-star selection is equivalent to positive density of G0*G2: choose one edge per represented product. It is not a weaker bridge.
- The minimal noncircular R-C target is the canonical full-annular incidence condition liminf 2^(-K) sum_(k<=K) M_k^2/E_k > 0.
- C14 exact census shows the 23-map affine collision excess worsens through 10^8; the zero/summable-excess bootstrap has no supporting finite trend.
- C13 proves the splitless allowed-hole count E(X)=o(X). It reduces density 2/3 to an eventual aggregate contraction M(X)-E(X)<=lambda M(floor((X+1)/2)) with lambda<2. Pointwise charging is false.
- C09 proves an exact fixed-subsystem recurrence criterion Delta(X)<=tau_(1/2)(X)F(X). The criterion passes all tested event cutoffs through 10^11 after X=64, but no asymptotic proof is known.


## C11/C12 corrections (2026-07-13)

- The full smooth/rough certificate requires rough cutoffs through X. The shorter X/L range is valid only for the windowed certificate with all ambient exceptions restored.
- Immediate 4t-1 contraction, seed-2 converse, and pointwise many-witness mechanisms are exactly false. The surviving R-A3 targets are the shifted smooth/sifted G2-factorization statements SR-S and SR-R in C11.
- Prime-frontier abundance is not forced by closure growth: a composite-only internal family attains the accepted exponent, and generic prime-seeded full closures can be O(X^epsilon). Fixed one-step cofactors face a growing modular avoidance problem.


## 2026-07-13 R2 ACCEPTED (archive: writeup/R2_GPTPRO56.md; gate header inside)

**ROUTE TABLE RESTRUCTURED BY R2 (verdict: case (c) for the old R-C framing):**
- (R-C EQUIVALENCE, verified exact): (1/18) d(G) <= d(G0*G2) <= d(G). R-C was not a weaker
  intermediate target; it IS the conjecture up to constants. Kept as the FRAME, no longer a route.
- SCALAR BOOTSTRAP KILLED (verified): B(CX) >= f(delta)X needs f(delta) > C*delta; constant-dilation
  top-window expansion uses finitely many multipliers (dead by obstruction); correct invariant =
  the full dyadic profile via the multiscale convolution bootstrap (40)-(43); critical profile
  delta_j ~ c/sqrt(j), i.e. X/sqrt(logX).
- NEW BARRIERS (verified unless noted): hyperbolic pair-mass N_X = o(X) kills ALL energy routes
  (15); tower pair count o(X) (18); bounded-depth product closures sublinear ((19)-(21), re-derive
  before use); reciprocal-summable x zero-density stays zero-density (22)-(24); T9*B circular (27).
  theta = log6/log30 = 0.5268025545 (corrected from 0.517; B07 recheck at gate).
- **R-D = NEW PRIMARY: growing-block common-slope affine-offset reservoir.** Exact objects:
  L2(t)=2t, L3(t)=3t+1, L5(t)=5t+3; offsets D_{a,b,c} with exact recursion (48)/(60);
  blocks H_k = 8Q^k + D_{15k,10k,6k} + 1 SUBSET G; color-split reservoirs (57)-(59).
  TWO FINITE GATES: (M) D_k >= c Q^k/sqrt(k); (E) global cross-k energy E_K <= C_E N_K.
  THEOREM (arithmetic verified): (M)+(E) => d(G0*G2) >= c^2/(3888 C_E Q) > 0 => d(G) > 0.
  Falsifiers: (64) liminf sqrt(k) D_k/Q^k = 0; (73) limsup E_K/N_K = infinity.
  Weaker asymmetric gate (75) survives symmetric (M) failure.
- FALLBACK: canonical smooth-rough cross-cover (77) (no energy input; refines R1 (21)).
- LITERATURE TO VERIFY (L11): Shamazov-Talambutsa orbit bound x/(logx)^((n-1)/2) under
  sum 1/a_i = 1 + freeness; Kolpakov-Talambutsa Thm 3 (sum 1/a_i > 1 => not free).

**(M1) FIRST (M)-GATE DATA (mine, claude_rd_offset_mass_probe.py SHA 62ce87da...):**
Exact D_{a,b,c} + word-multiplicity second moment E^off on two supercritical rays:
ray (3,2,1) (M=360^k, n=6k): sqrt(n)D/M = 0.4082, 0.3493, 0.3222 (k=1..3); E^off/W = 1.0, 1.120, 1.305.
ray (2,1,1) (M=60^k, n=4k):  sqrt(n)D/M = 0.4000, 0.3213, 0.2761, 0.2458 (k=1..4).
All W validated against multinomials; CS floor W^2/E^off <= D everywhere (D within 1.13x of floor
=> near-uniform multiplicities on support). Normalized sequence DECAYING with local exponent
~0.32-0.40 in n and drifting — INCONCLUSIVE at n <= 18 letters; deep points k=4 (360^4=1.7e10)
and k=5,6 (60^k) running. NOTE: these small rays are NOT the canonical (15,10,6) ray; they probe
the same mechanism at reachable scale.

**(40)-AUDIT: membership-recursion DP vs truncated closure: EXACT bitmap match at 10^6 AND 10^7**
(claude_membership_recursion_census.py SHA 411948d8...; 10^7: both |G|=4952270, same SHA-256).

**(M1-deep) ray (3,2,1) k=4 (claude_rd_offset_mass_deep.py SHA ba85e7a0..., bool DP, M=16796160000):**
D_4 = 1054111467, sqrt(n)D/M = 0.3075. Sequence 0.4082, 0.3493, 0.3222, 0.3075 with decrements
-0.0589, -0.0271, -0.0147 (ratios 0.46, 0.54) => geometric-looking convergence to ~0.29-0.30 > 0.
FIRST EMPIRICAL SUPPORT FOR GATE (M) on a supercritical ray. Ray (2,1,1) k=5,6 still running.

## C16/C22 contraction frontier (2026-07-13)

- Let M(X) count allowed holes, E(X) splitless holes, and R(X)=M(X)-E(X) reducible holes. Exact every-cutoff computation gives R(X)<=M(floor((X+1)/2))+M(floor((X+1)/3)) for every X<=10^9, with zero failures. At 10^9: M=131390048, E=88550127, R=42839921.
- The stronger partition inequality `odd_seed2 + hard <= Mhalf` also has zero failures through 10^9. Together with the proved E(X)=o(X), either contraction would force M(X)=o(X) by a limsup argument.
- C22 proves that the two-scale inequality does not follow from forward closure alone. Exact CP-SAT finds the first closed-superset countermodel at X=362, with excess 1. It contains unsupported members such as 8. Therefore a proof for the actual set must use least/grounded generation from seeds 2 and 3. See `fanout/wave3/C22_universal_contraction_sat.md`.

## C18 affine pair-state verdict (2026-07-13)

- The exact inverse-parent recurrence has 11 live pair transitions, while the triple P235 has one transition. Literal primitive pair states do not close finitely: repeated `(5,3)` transitions yield infinitely many states.
- At t=547, two first-parent branches overlap exactly, so summing pair branches already requires a triple correction. The nine independent tests pass. Hence a finite pair-state recurrence is not a route without a new quotient or summable infinite-state weights.

## 2026-07-13 (M2) two-ray deep data + Codex WAVE3 reconciliation

**(M2) DEEP (M)-GATE DATA (mine, claude_rd_offset_mass_deep.py SHA ba85e7a0...):**
ray (3,2,1), n=6k: sqrt(n)D/M = 0.4082, 0.3493, 0.3222, 0.3075 (k=1..4; D_4 = 1054111467 at
  M=1.68e10). Local log-log exponent SHRINKING: -0.225, -0.200, -0.162 => consistent with a
  POSITIVE limit ~0.28-0.30. Surplus (word entropy - slope rate) = 0.0304 per letter.
ray (2,1,1), n=4k: sqrt(n)D/M = 0.4000, 0.3213, 0.2761, 0.2458, 0.2235, 0.2059 (k=1..6;
  D_6 = 1961050980 at M=4.67e10). Local exponent GROWING: -0.32, -0.38, -0.40, -0.43, -0.45 =>
  consistent with decay to 0 (exponent drifting toward -1/2). Surplus = 0.0161 per letter.
VERDICT: (M) is RAY-DEPENDENT in the data; the canonical ray (15,10,6)/31 has surplus 0.0327,
closest to ray (3,2,1) (favorable). Open: what ray invariant separates limit>0 from limit=0.

**CODEX WAVE3 RECEIVED (C00-C22 + gpt_pro/) — registered as CLAIMS, initial audit notes:**
- C01 (L9-EXT DONE): full unthinned energy grid to B=10^7; largest case 1.26e10 products:
  E/(|U||V|) = 1.1709, kappa = 92.62. Ratio RISING with scale (1.006 -> 1.125 -> 1.171).
- C05 (RED-TEAM, MAJOR): claims single-Cartesian-window bounded-kappa target is IMPOSSIBLE:
  min(Y,Z) -> infinity forces X*E/(|U|^2|V|^2) -> infinity, via Ford divisor-in-interval
  (rectangular multiplication-table thinness). KILLS R1 (48)-(51)/(58)-(61) AS STATED (single
  window). Does NOT touch R-D aggregated reservoirs (non-Cartesian union over k) — R2's move to
  aggregation was already forced by its (16). PENDING my re-derivation of the Ford step.
- C04 (L11 partial DONE): BKS citation VERIFIED to primary source: Bettin-Koukoulopoulos-Sanna,
  Bull. LMS 53 (2021) 1407-1413, DOI 10.1112/blms.12506, arXiv:2006.13356. Ford part in file.
- C14: 23-map affine support collision census to 10^8; both C07 zero-excess gates still fail;
  excesses ~0.458 and ~0.157 with no decay (context: Codex-internal C07 framework).
- C19: exact collision language for the {2,3,5} orbit: smallest collision morphisms 15t-2,
  600t-98, 400t-51; the 25-channel block monoid NOT finitely generated (depth-d indecomposables
  >= d-6). Directly relevant to R-D E^off collision control.
- CX-GPT (gpt_pro/, Codex-owned INDEPENDENT GPT-Pro rounds; NAMESPACE: their R<n> = CX-R<n> here):
  CX-R2 "finite-state strict-gap theorem": ANY fixed finite congruence partition + finite affine
  word family + fixed fractional packing has density-transfer spectral radius < 1 => no fixed
  finite monotone renewal architecture can prove positive density; unbounded scale-dependent
  complexity NECESSARY. Codex audit: accepted after notation repair. Consistent with R-D growing
  blocks. PENDING my audit. CX-R3 prompt (hole contraction) drafted by Codex.

## 2026-07-13 mailbox delta reconciliation (12.8KB, 10 Codex posts) + my C00 re-gate

**(C00 ACCEPTED at <=10^6 by exact independent replay, claude_hyperbola_regate.py SHA 18eb9e48...):**
Full-hyperbola census r_X(p) = #{(a,b) in G0 x G2 : ab = p}: my (P,Q,E) match Codex EXACTLY at
10^3/10^4/10^5/10^6: (124,118,136), (1856,1591,2420), (27214,20391,42858), (370812,239195,716226).
kappa_hyp = EX/P^2 = 8.845, 7.025, 5.787, 5.209. Codex 10^7/10^8 (claim, sampled-verified only):
P/X = .4788, .5967; Q/X = .2618, .2754; kappa = 5.052, 5.153. EMPIRICAL PICTURE: the aggregated
hyperbola has LINEAR pair supply (P/X rising to 0.6) and BOUNDED-LOOKING aggregate kappa ~5.1
(slight rise at 10^8 forbids monotonicity claims). Q/X = 0.2754 at 10^8 is direct finite evidence
d(G0*G2) reachable ~ 0.27+ so far. Cauchy: Q >= P^2/E = X/kappa exactly.

**REGISTERED FROM DELTA (Codex claims + my initial rulings):**
- NORMALIZATION AUDIT (Codex, RE:TICK-130) ACCEPTED BY INSPECTION: for a full dyadic rectangle,
  E >= |U||V| always, so bounded single-rectangle kappa FORCES delta_U delta_V >= 4/kappa —
  the hypothesis already contains the target-scale mass (circular). Together with C05
  (Cartesian max(U),max(V) -> inf => kappa -> inf, Ford; pending my Ford-summation gate):
  **CARTESIAN R-C IS DEAD IN ALL FORMS (balanced, unbalanced, full-box).** Supersedes my E1
  single-window framing; my E1/E-tables remain valid DATA about ratios, not a route.
- C07 (claim): exact self-improvement P(4X) >= 2Q(X) >= 2P(X)^2/E(X); S = G0G2 closed under
  F_a(n) = a(n-1), a in G0, and H_b(n) = b(2n-3), b in G2 — TO GATE (high value: a recurrence
  on the hyperbola). 23-map family inverse-slope weight W = 1.094618 > 1; summable-collision-
  excess bootstrap gate: EMPIRICALLY DEAD (C14: excess 0.458/0.157 at 10^8, not decaying).
- C09 (claim): Boolean recurrence criterion R: Delta(X) <= tau_{1/2}(X) F(X); if eventual =>
  B(X) >= cX/sqrt(logX) (the critical profile) => linear hyperbola supply. Exhaustive through
  10^8 (32 failures all <= 64); all collision-tax events through 10^11 pass; margin -0.0146
  narrowing. Shamazov-Talambutsa Thms 5/7 CANNOT prove R (exponent 1/2 unreachable for this
  alphabet). Status: theorem-strength collision estimate, unproven asymptotics.
- C13/C16 (claims, INDEPENDENT ROUTE R-E "hole contraction"): splitless allowed holes E(X)=o(X);
  candidate contraction R(X) <= M((X+1)/2) + M((X+1)/3) has ZERO failures through 10^9
  (C16 exact C++, result_1e9.json); if proved with E(X)=o(X) => M(X)=o(X) => d(G)=2/3 EXACTLY.
  C22: closure-only version FALSE (CP-SAT countermodel X=362, excess 1, 34 unsupported values
  starting at 8) => any proof MUST use least-fixed-point groundedness. Codex lanes C23 (grounded
  Horn dual) + C24 (derivation-rank Hall) attacking.
- C11 (claim): R-A3 certificate quantifier corrections; immediate 4t-1 contractions, seed-2
  converse, pointwise many-witness claims FALSE; surviving = SR-S/SR-R shifted-factorization
  membership theorems. C12: prime-frontier abundance dead as generic route. C20: arithmetic
  multiplicity does not transfer G2 membership (blocked-pair witnesses).
- C03 (L10 DONE, claim): gates (31)/(32) exact finite values through 3.3e7; (31) ~1.00 (no o(logz)
  evidence); (32) decreasing 0.182 -> 0.086. Data only.
- CX-R2 (Codex GPT round, audited by Codex): fixed finite-state renewal has spectral radius < 1
  (no fixed architecture proves density); escape = scale-dependent packings with
  sum(1-theta_k) < infinity. PENDING my audit; consistent with R-D/R2 growing-scale requirement.

**FRONTIER AFTER THIS DELTA (three live mechanisms):**
(1) HYPERBOLA PAIR (new primary candidate): prove P(X) >= c1 X AND E(X) <= C P(X)^2/X.
(2) R-D growing blocks (M)+(E) — R3 in flight at GPT on exactly this.
(3) R-E hole contraction (C13/C16 + groundedness) — Codex-led, would give d(G)=2/3 exactly.
