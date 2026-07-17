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

## C78 image-boundary checkpoint (2026-07-13)

- The exact shell identity rewrites the C23 image inequality as: every
  image-realizable blocker cut has at least as many healed nonhard roots as
  unhealed hard roots.
- Four stronger local mechanisms are false: immediate matching at `54`,
  transitive local matching at `74`, direct banks at `186`, and rank-two
  dominance at `362`.
- The audit replays byte-identically under `python -O`.  A full image scan of
  all `66` hard cutoffs through `1000` has no violation.  This is finite
  evidence, not a uniform proof.
- Report: `fanout/wave5/C78_image_boundary_audit.md`.

## C88 tight-face backbone (2026-07-13)

- At each tight cutoff `54,74,186,362`, all zero-slack image optimizers have
  an identical full healed/unhealed shell pattern.
- The source is not rigid: `13,21,47,89` source variables remain free.
  Hence only the shell skeleton, not the source, is canonical in this finite
  gate.
- Exact Boolean fixing tests replay byte-identically.  Report:
  `fanout/wave5/C88_tight_backbone.md`.

## C89 grounded optimality obstruction (2026-07-13)

- The strengthening that `G` minimizes image slack is false first at `704`:
  the exact image optimum is `H-Q=-4`, while `G` has `-5`.
- Through `5000`, the optimizer-grounded gap reaches `4`; C23 itself still
  has no finite failure in this scan.
- Report: `fanout/wave5/C89_grounded_optimality.md`.

## C80-C82 global-reserve checkpoint (2026-07-13)

- C80: blocker-local least-counterexample induction is false already at
  `X=74`; hard roots `54,74` both reach only healed root `6`, while the
  second required reserve is the unrelated root `18`.  This obstruction
  also occurs in the canonical grounded prefix.  C23 itself remains tight.
- C81: an exact CP-SAT gate plus solver-free replay proves the C23 image
  inequality at every one of the `878` hard cutoffs through `10000`.
  Equality occurs only at `54,74,114,186,204,362`; this is finite only.
- C82: every C56/C79 dual has base-row load at least
  `K_X >= floor((X-24)/30)`.  Exact minimum base loads at
  `54,74,186,362,2000` are `1,3,13,35,310`.  Hence fixed-window,
  append-only, or eventually frozen local dual recurrences are impossible;
  a proof must update old coefficients globally with the cutoff.
- Independent `python -O` replays reproduced all C80-C82 JSON outputs
  byte-for-byte.  C79 acceptance assertions were replaced by explicit
  exceptions; the hardened exact replay output is unchanged.

## C83 arithmetic-feature obstruction (2026-07-13)

- At `X=186`, the grounded image has six unhealed hard roots
  `{54,74,114,144,174,186}` and six healed nonhard roots
  `{6,18,20,32,38,66}`, so the C23 shell inequality itself is tight.
- Under the full cut-independent local signature, roots `48` and `66` have
  the same feature class, but only `66` is healed.  Therefore that class is
  unusable by every sound static feature block.  The remaining five sound
  singleton target classes have capacity `5` against hard demand `6`.
- This is an exact real-valued Hall obstruction to the entire specified
  feature-symmetric static-potential family.  It does not falsify C23 and
  does not exclude root-specific or cut-adaptive global transport.
- The original solver-free replay is byte-identical under `python -O`.
  Independent standard-library verifier
  `compute/wave5/C83_feature_potential_independent.py` reconstructs the
  closure, image, ranks, classes, and deficit from definitions; canonical
  result SHA-256 is `5B4C3616BE7A47031A2491F04F5DAE3F08C0C6CE98B1DDE1F89BF64E194594DE`.

## C84 global flow-to-dual bridge (2026-07-13)

- Every full integral C65 arithmetic flow gives an exact zero-objective C79
  dual.  Descending grounding recursively revises all old closure-row
  multipliers, so this bridge is compatible with C82's unbounded base load.
- At `X=1710`, an exact 81-path packing yields a coefficientwise integer
  dual with `alpha_5=269`.  Optimized replays verify the packing and dual;
  the dual JSON is byte-identical with SHA-256 `67EE097E...`.
- The canonical ambient-online shortest-path recursion is false at `1710`:
  it stops at `80/81`.  This does not falsify full-flow existence because
  the alternative 81-path packing is exact.
- The live frontier is therefore a uniform max-flow/Hall theorem for the
  arithmetic network, not a monotone greedy construction.

## C86 valuation-separated product obstruction (2026-07-13)

- The exact support maps `F_a(n)=a(n-1)` and `H_b(n)=b(2n-3)` give a valid
  collision-free recurrence when channels occupy distinct output
  2-adic valuations.
- A probability-weight dual proves uniformly that every profile-free scheme
  of this type has renewal capacity at most `23/45<1`.  The proof permits
  infinitely many channels and arbitrary source-valuation assignments.
- The finite `10^6` census has best exact inverse-slope load
  `6388439/17054400` and image coverage `79079/239195`.
- All acceptance `assert`s were replaced with explicit exceptions.  Normal
  and optimized hardened outputs are byte-identical.  Thus a product route
  must use richer profile information or controlled valuation overlap.

## C87 root-specific Horn obstruction (2026-07-13)

- A universal implication from hard root `h` to nonhard target `r` has an
  exact solver-free characterization: `top(r)` must be grounded, and every
  minimal pair-source `cl(G union {a,b})` generating `r` must support
  `top(h)`.  Necessity uses those minimal sources; sufficiency uses closure
  and image monotonicity.  Distinct inputs and cutoff locality are explicit.
- At `X=2000`, the resulting graph has `83` hard roots, `207` targets, and
  `6032` edges.  Its exact maximum matching is `82`; a Hall witness has
  `80` hard roots and exactly `79` neighbors.
- A second implementation enumerates rules by input pairs and computes
  closure by a trigger worklist.  It reproduces all adjacency data and the
  Hall witness.  Normal and optimized output SHA-256 is `7E1F5A6D...`;
  canonical summary SHA-256 is `A8A7F975...`.
- Therefore even cutoff-dependent, exact-root static universal transport is
  insufficient.  This does not falsify C23; viable transport must adapt to
  the source cut or use the global arithmetic flow of C84.

## C85: capacitated root pooling; unit capacity is false

For each fixed pair threshold `D`, every hard hole with at least `D+1`
admissible factor pairs satisfies Hall after root `r` is given capacity

`ceil(b_X(r)/(D+1))`, where
`b_X(r)=sum_{p in C_X(r)} floor((X+1)/p)` over missing odd nodes on the
seed-2 chain rooted at `r`.  The proof is an exact divisor-incidence count.
Consequently every fixed finite set of roots traps only `o(X)` hard holes.

Capacity one is false.  The first local collapse is `6140`, whose two
admissible pairs expose missing endpoints `23` and `89` on the same root-12
chain.  With at least six pairs per source, the first global Hall failure is
at `X=4361928`: an exact set of 48 hard holes has complete neighborhood of
47 roots.  Both integer augmenting-path computations replay byte-identically
under normal Python and `python -O`; JSON SHA-256 values begin `0854516C`
and `C612FF06`.  Thus C85 removes fixed-root traps but does not prove a
coefficient below `4/3`.

## C90: full arithmetic flow and C56/C79 are false

The exact max-flow/min-cut characterization is proved: full flow at cutoff
`X` is equivalent to `Q_X(U)>=|K_X cap U|` for every hole set `U` containing
all structural splitless holes and closed under all generated-factor unary
arcs.  In seed-chain coordinates this is `|T(U)|<=N(U)`.

The statement first fails at `X=2064`.  A verified source side has 97 selected
hard shapes and 96 seed exits; the corresponding network has demand 101 and
an exact minimum cut of capacity 100.  The same Boolean set satisfies every
C79 subadditivity row and has objective excess one, so the relaxed C56/C79
inequality itself is false.  Normal and `python -O` replays are byte-identical
(local log hashes `6202B289...` and `A45BB685...`).  This does not falsify the
more structured one-step-image inequality or C91's common-bank reduction.

## C91-C94 common-bank checkpoint (2026-07-13)

- C91 proves conditionally that `A_H(X) <= c D(X)+o(X)` for any fixed
  `c<4/3` implies the uniform cut contraction and hence generated-set density
  `2/3`.
- C93 independently scanned every event cutoff through `10^9`.  The exact
  minimum positive ratio is `D/A_H=5/6` at `X=186`; there is no failure of
  `6D>=5A_H`.  Two C++ runs are byte-identical, and an independent Python
  reconstruction agrees through `10^6`.  This is finite evidence only.
- C94 proves that because `0<=D(X)<=E(X)=o(X)`, every comparison
  `D(X)>=alpha A_H(X)-o(X)` with fixed `alpha>0` is equivalent to
  `A_H(X)=o(X)` and therefore to the full density theorem.  Thus the healed
  bank is not an already-positive reservoir.
- C92 found, with zero failures through `10^9`, the sharper exact candidates
  `A_H(X)<=D(X)+A_H(floor(X/4))+1` and
  `2D(X)>=7A_H(floor(X/4))`.  Together they imply
  `A_H(X)<=(9/7)D(X)+1`, enough for C91.  Neither quarter inequality is
  proved; they are the active arithmetic frontier.
- C96 proves that either quarter inequality with an arbitrary `o(X)` error is
  already equivalent to `A_H=o(X)`.  The canonical prime-square shadow cannot
  prove the fourfold statement: `54` maps to splitless root `24`, whose chain
  is unhealed through `216` and first heals only at `5889`.  Independent
  normal/optimized verification is byte-identical (SHA-256 `5BDB8911...E08B6`).
- C94's finalized analytic audit gives the exponent obstruction to the
  existing C55+C85 combination: the structural-bank reciprocal mass is
  `Omega(sqrt(log X))`, while C55's proved `omega_2` count only permits pair
  thresholds `(log X)^c` for `c<(log 2)/2<1/2`.  A possible escape is a new
  admissible-pair lower bound using all prime-power blocks, not only
  `2 mod 3` prime factors; this is under exact audit and is not yet a theorem.

## C92/C95/C97/C98 quarter-frontier audit (2026-07-13)

- C92's optimized exact scan now reaches every cutoff through `4*10^9` with
  no failure of `6D>=5A_H` or either quarter inequality.  The artifact SHA-256
  is `3391E75C...47CCC80E`; an independent direct-factor replay through
  `10^5` is byte-identical to the checked-in verifier output.  This remains
  finite evidence only.
- C95 proves the exact event identity
  `D(X)+A_H(floor(X/4))-A_H(X)=D(X)+|Lost_X|-|Fresh_X|`.
  The minimum through `10^9` is `-1`, first at `X=186`.  Factor-local Hall
  already has deficit four there, and the infinite `11p-1` star rules out
  unit charging to a source's own critical chain even with same-family
  quarter tokens.
- C97 broadens source ancestry to every missing-factor derivation leaf.  Its
  first exact Hall failure is `X=114`: sources `54,74,114` see only healed
  leaf `6`, while the scalar bank is `{6,18,20}`.  Thus the required payment
  is genuinely nonlocal even after all derivation leaves are exposed.
- C98 proves a nested-neighborhood Hall equivalence for the lower-quarter
  inequality, with seven source slots and two healed-root slots.  This is an
  exact reformulation, not a proof; support-local capacity fails at `54`,
  every downward-only family fails at `174`, and the `Y=2064` instance uses
  609 of 618 available slots.
- C85 coverage warning: the structural splitless bank does not contain every
  direct witness root.  The hard hole `534` has unique pair `535=5*107`; `5`
  is generated, while `107` lies on the hard root-`54` seed chain.  Therefore
  applying C85 Corollary 2 with only structural roots controls a proper
  subset of hard holes, not `A_H` or all hard holes.

## C99 all-prime sieve and residual-basin frontier (2026-07-13)

- For a hard hole with `h+1=3^epsilon R`, C99 proves the exact formula for
  residue-compatible factor pairs and the uniform lower bound
  `d(h)>=2^(omega(R)-2)`, including squarefull minus-prime factors.
- Hence, for every fixed `c<log 2`, the hard holes with
  `d(h)<=(log X)^c` are `O_c(X/log log X)=o(X)`.
- The structural splitless bank has reciprocal mass
  `Theta(sqrt(log X))`, so the exponents overlap for
  `1/2<c<log 2`.  This would close the sieve if high-pair hard holes were
  structurally trapped.
- That trapping is false.  The first direct failure is hard `534`, with
  `535=5*107` and non-splitless witness root `54`.  At `X=10^6`, `c=0.6`,
  151 high-pair hard holes have a non-splitless C85 witness root.
- Naive recursive shadow descent loses one logarithmic power; its exponent
  gap is `3/2-2 log 2=0.1137...`.  The remaining analytic target is an
  aggregate reciprocal-mass bound for non-splitless witness-root basins,
  not a pointwise structural-root capture lemma.
- Report SHA-256 `43AB890A...CC0DC0AD`; verifier SHA-256
  `B4BE979F...D2179BA6`.  Exact replay through `10^4` found zero formula or
  lower-bound failures and reproduced the first trap failure at `534`.

## C101 cross-type obstruction (2026-07-13)

- Partitioning persistent hard roots and healed splitless roots by
  `1_{3 divides r+1}` does not support a separate one-exception ballot.
- The first failure is exact at `X=186`: the nondivisible type has margin
  `-2`, the divisible type has margin `+1`, while the untyped quarter margin
  is `-1` and the candidate upper-quarter inequality is tight.
- Thus any proof of the untyped quarter gate must transfer capacity across
  these arithmetic types.  Source-independent matching within each type is
  already insufficient; this does not falsify the untyped inequality.
- Normal and optimized exact replays through `10^5` are byte-identical,
  SHA-256 `8B0E7363...A479A2C1`.

## C102 scale-varying light decoder (2026-07-13)

- C102 constructs explicit color-separated generated blocks `U_k,V_k` and
  central cross-scale edge families of size
  `N_K=sum_i |U_i||V_{K-i}|`, respecting distinct inputs.
- If `N_K>=c0 Q^K` and a fixed fraction `eta` of its edges lie on products
  of multiplicity at most a fixed `L`, then the retained products form an
  explicit subset of `G` with lower density at least
  `c0*eta/(972*L*Q)`.
- The two gates are not proved.  Exact experiments retain
  `60,512,829/60,512,841` edges at multiplicity at most two in the largest
  `(3,2,1)` row.  This is finite evidence only.
- This decoder is scale-varying and truncates the collision tail, so it is
  not killed by fixed automata, one Cartesian window, or bounded full-energy
  obstructions.  Its averaged support and truncated-collision gates are the
  live affine frontier.

## C103 zero-density obstruction audit (2026-07-13)

- Licensed affine-spine derivation-tree counts are superlinear at explicit
  cutoffs `X_m=9Q^m`: the ratio is at least
  `(31/30)^(31m)/(9(31m+1)^2)`.
- The direct root recurrence is supercritical for every exponent at most
  one because `1/2+1/3+1/5=31/30>1`; the residue-envelope product table
  already has size `2X/3+o(X)`.
- Hence unquotiented tree counts, bounded-multiplicity encodings, plain
  renewal, and residue-envelope multiplication cannot prove zero density.
  A negative proof would need a global collision quotient or an independent
  sparse-sequence sieve.
- The independent exact verifier reproduces `A(10^8)=51,899,129`; normal
  and optimized checks of the `10^5` probe and entropy certificate pass.

## GPT-Pro R8: quarter inequality is history-sensitive (2026-07-13)

- For the least closure seeded by `{2,3,66}`, the exact cutoff `X=186` has
  six persistent hard roots, four healed structural roots, and no persistent
  hard root through `floor(186/4)=46`; the quarter inequality fails by one.
- For the actual closure seeded by `{2,3}`, the only difference relevant to
  the count is that `66` is a structural hole whose chain enters at `131`.
  This supplies the fifth bank event and makes the actual inequality tight.
- Therefore closure, residues, the hard/splitless taxonomy, and the fact that
  hard cofactors lie below the quarter scale do not formally imply the gate.
  Any proof for the actual set must use global two-seed derivation history.
- A separate exact normal/optimized verifier reconstructs the complete
  three-seed prefix and all three counts; verifier SHA-256
  `6F7A1FEB...F29DA`.

## C104 reducible-root dyadic census (2026-07-13)

- For threshold `D`, let `R_{X,D}` be the non-splitless witness-root union of
  hard sources `h<=X` with `d(h)>=D+1`.  The exact eventwise scan found no
  failure through `10^8`, for every `1<=D<=15`, of
  `D*|{r in R_{X,D}:2^j<=r-1<2^(j+1)}|<=2^j`.
- If this dyadic-bin inequality holds universally, then
  `Sigma_D(X)<= (1+floor(log_2 X))/D`.  Taking
  `D=floor((log X)^c)` with `1/2<c<log 2` supplies the missing C99
  reciprocal-mass estimate and closes the positive-density proof.
- The stronger `D^2` bin bound and a constant global reciprocal budget are
  exactly false.  Thus C104-BIN, not either strengthening, is the current
  residual-basin frontier.
- An independent Python implementation through `300000` is byte-identical
  under normal and optimized execution, SHA-256
  `672157C5905B31FC79AA2E28CC014256EA03005F9B58D0AC1185CAE28C91C28C`;
  all 11 manifest entries pass a separate hash audit.
- A fixed-root diagnostic prevents treating C104-BIN as a routine packing
  fact.  For root `54`, the maximum witnessed source pair count rises through
  `1,2,3,6,8,9,12`, reaching `12` at source `7634274`; roots `62,68,534`
  show similar growth.  Universal C104-BIN therefore requires a genuine
  uniform bound on these staircases or a global packing mechanism.
- A one-implementation exact extension to `X=10^9`, with thresholds through
  `D=63`, still finds no C104-BIN failure and has maximum `d(h)=16`.
  However the stronger integrated load
  `sum_r(max_d(r)-1)<=2^j` reaches `119/128` in bin `j=7`, up from
  `101/128` at `10^8`.  That tempting sufficient strengthening is therefore
  near its finite capacity and is not accepted as a proof route.
- The final one-implementation falsification pass at `X=4*10^9`, again with
  thresholds through `D=63`, finds no C104-BIN failure.  The maximum source
  pair count is `18`; its only threshold-18 source activates four roots in
  bins `9,14,15`, not the saturated low bin.  The integrated-load maximum
  remains `127/128`.  Endpoint extension is stopped; these rows are finite
  evidence and have no theorem status.

### Weaker sufficient dyadic tail

- Full C104-BIN is stronger than the C99 sieve needs.  Suppose for some
  constants `C` and `alpha>0` one has uniformly
  `|R_{X,D} cap {2^j<=r-1<2^(j+1)}| <= C*2^j/D^alpha`.
  Then summing `1/(r-1)` over dyadic bins gives
  `Sigma_D(X) <= C(1+log_2 X)/D^alpha`.
- C85 divides this mass by another factor `D`.  With
  `D=floor((log X)^c)`, the residual term is
  `O(log X/(log X)^(c(alpha+1)))`, hence `o(1)` whenever
  `c(alpha+1)>1`.
- C99 permits every fixed `c<log 2`.  Therefore any
  `alpha>1/log(2)-1=0.442695...` closes the route.  In particular the
  square-root tail `alpha=1/2` suffices by choosing
  `2/3<c<log 2`.  This is the current weakened basin frontier.
- The power tail need only hold for bins `j>=J(D)`, where `J(D)=o(D)`.
  The unrestricted reciprocal mass of the first `J(D)` bins is at most
  `O(J(D))`, so C85 makes their contribution `O(J(D)/D)=o(1)`.
  Consequently unbounded witness loads at any fixed finite set of roots do
  not obstruct the weakened route.

## C106 affine-decoder collision normal form (2026-07-13)

- C102's conditional decoder, distinct-input handling, scale bounds, and
  density constant are correct.  Gate T remains unproved and unfalsified.
- Every product collision has the unique coprime-swap form
  `(u,u',v,v')=(ga,gb,bc,ac)`.  An exact cross-scale collision preserves all
  `2,3,5`-adic factor valuations, so channel recovery by size or those
  valuations is false.
- At the first three-channel block `K=6`, exactly `307691821` of
  `307692465` labelled edges have multiplicity at most two; the maximum is
  four.  This is finite evidence.  Gate T is now the bounded-degree-mass
  problem in the scale-annular coprime-swap graph.

## C100 affine support obstructions (2026-07-13)

- Gate A is not implied by the known finite data, the capacity bound, the
  majority bound, and concatenation supermultiplicativity.  An exact scalar
  continuation satisfies all of them while
  `N_K/360^K <= 225(K+1)/(K+300)^2 -> 0`; a concrete rank-two
  concatenation language has the same `O(1/K)` behavior.
- The exact affine identity `T_322255=T_255232=600x-381` tensors into
  `8^k` distinct canonical-type words in one fibre.  Since
  `8*30^31>31^31`, this rigorously falsifies C29's uniform max-fibre
  local-limit estimate at the required scale.
- This does not falsify C102 Gate A after quotienting words by their affine
  value.  It proves that Gate A needs a quotient-level rank-one/support
  mechanism; word-level renewal and non-tensoring overlap assumptions are
  insufficient.

## C105 structural-pair fraction audit (2026-07-13)

- The exact census through `4*10^9` contains `106360959` hard holes and has
  maximum observed deficit `d(h)-s(h)=8` between allowed factor pairs and
  structural factor-pair mass.
- A rigorously parameterized `d=8,s=0` template recurs at finite points up
  to `h=918066571382`.  This kills direct per-pair positivity and requires
  any lower bound to retain an additive exceptional term.
- The finite data support the possible target `s(h)>=d(h)-8`, but neither
  that inequality nor a fixed positive fraction is proved.  C105 therefore
  does not close the C99 basin step.
- All 13 C105 manifest hashes pass an independent audit.  The independent
  Python checker agrees at `10^6` normally and under `python -O`.

## GPT-Pro R9 Gate-T dispersion lemma (2026-07-13)

- For every product value `z`, the full labelled fibre injects into the
  divisors of `z/(2^v2(z)3^v3(z))`.  Hence each fibre is subexponential
  uniformly in the total scale.
- The 60 distinct one-block offsets from permutations of `(2,2,2,3,3,5)`
  concatenate injectively in base 360.  Consequently
  `N_K >= (|I_K|/4)60^K`.
- For every fixed `delta in (0,1)`, any at most
  `60^((1-delta)K)` product values carry at most
  `(4A_delta/|I_K|)60^(-delta K/2)` of the labelled edge mass.
- This proves exponential dispersion of collisions and rules out bounded,
  polynomial, or sub-`60^K` concentration mechanisms.  It does not prove
  fixed-`L` Gate T: exponentially many medium fibres remain possible.
- The finite 60-block and labelled-divisor kernels pass an independent exact
  normal/optimized verifier, source SHA `C44A58C3...E773`, output SHA
  `6645D34A...6B2E`.  Full audit: `fanout/wave5/R9_gateT_dispersion_audit.md`.

## C107 seed-sensitive quarter correction (2026-07-13)

- The literal arbitrary-nonempty-seed inequality is false at the smallest
  possible cutoff: `S={2}, X=74` gives `A_H=2`, `D=0`, and
  `A_H(floor(X/4))=0`, so its right side is one.
- Under the intended hypothesis `{2,3} subset S`, the natural correction is
  the number of occupied `U`-roots among the seeds.  The corrected statement
  has no finite failure in C107's enumerated systems, but remains unproved.
- The naive componentwise Euler induction is false: adding seed 668 lowers
  the uncorrected margin by two at `X=8012` by simultaneously suppressing
  roots 668 and 1002.
- All eight recorded principal hashes and the normal/optimized independent
  verification equality pass a local audit.  C107 changes the necessary
  formulation but does not prove the actual two-seed upper-quarter gate.

## C108/C110 moving-tail convergence (2026-07-13)

- The square-root pointwise tail
  `D*N_j(X,D)^2<=2^(2j)` for `j>=ceil(sqrt(D))` is sufficient for C99,
  using any fixed `2/3<c<log 2`.  It has no exact failure through
  `X=3*10^9`, with maximum tested ratio `275/4096`, but is unproved.
- The strictly weaker sufficient frontier is the integrated Carleson bound
  `sum_{j>=J(D)} N_j/2^j <= C(1+log_2 X)/sqrt(D)`, with
  `J(D)=ceil(sqrt(D))`.  Equivalently for `C=1`, its squared exact gate is
  `D*(sum N_j/2^j)^2 <= (1+floor(log_2 X))^2`.
- C108 isolates a stronger nested Hall gate with capped weights
  `min(ceil(sqrt(q_X(r))),j)`.  It has no deadline failure through `3*10^9`
  and maximum token mass `43/128`, but no token injection is proved.
- A direct source-local square-root argument is false at `h=1154`: it has
  `d=4` but only one reducible witness root.  Therefore the proof must pool
  structural and reducible roots or use global root-upgrade capacity.
- Both C110 manifests pass independent hash audits (`25/25` and `16/16`),
  and all nine C108 reported hashes pass.  Normal/optimized replays agree.

## C111 divisor-moment anticlustering audit (2026-07-13)

- For every `K>=2` and integers `q,T>=1`, the labelled edge tail obeys
  `T^q M_K(T) <= 972|I_K|360^K J_K^(2(2^q-1))`.
- After the exact `N_K >= |I_K|60^K/4` normalization, optimizing
  `q=floor(log_2(K/(log K)^3))` makes the edge mass above
  `exp((((log 2)(log 6))+epsilon)K/log K)` exponentially small.
- This is stronger than the pointwise R9 divisor bound, but it leaves the
  entire fixed-to-subexponential medium-fibre regime.  Fixed-`L` Gate T is
  still open.
- Independent normal/optimized Python outputs have SHA `867B732D...1FE7F`;
  an independently rebuilt 32-thread C++ census is byte-identical with SHA
  `D3A443E8...D0DC`.  Full audit: `fanout/wave5/C111_gateT_anticlustering_audit.md`.
- The proposed bounded-suffix decoder is exactly false: 30 collision pairs
  retain common six-letter suffixes on both factors.

## C112 weakened structural-incidence frontier (2026-07-13)

- If every high-pair hard source has at least `L` structural pairs, then
  `H_high(X) <= (X+1)W_E(X)/L`; the proof counts distinct factor endpoints
  and sums their seed-root geometric series.
- Consequently any uniform `s(h)>=A d(h)^alpha-B` with
  `alpha>1/(2 log 2)` closes C99.  In particular
  `s(h)>=d(h)^(3/4)-8` is sufficient and strictly weaker than `d(h)-8`.
- Neither power bound is proved.  Exact independent searches agree that all
  39,229 prime lifts of the recurrent `d=8,s=0` base through prime `10^6`
  are generated, so this direct multiplicative falsifier fails finitely.
- Normal/optimized replay output SHA is `7A864A14...E1F1`.  Full audit:
  `fanout/wave5/C112_structural_deficit_audit.md`.

## C114 selected-square layer-cake frontier (2026-07-13)

- The exact square-layer identity implies that, for
  `m=floor((log X)^(c/2))` and `2/3<c<log 2`, the single condition
  `B_m(X)=o(m^3)` suffices to make the C99 residual-root term `o(1)`.
- This condition is strictly weaker than the integrated Carleson target but
  remains unproved.  It is a sufficient frontier, not a density theorem.
- Source-local charging is dead at the exact hard source `h=77317236`,
  where `d=4,A=2,M=1` and therefore `AM<d-1`.
- Independent normal/-O probes and layer-cake checks have SHAs
  `EB4B0608...A9EC` and `51E9F90B...9A1A`; a rebuilt C++ scan through `10^9`
  is byte-identical with SHA `D468AECD...F030`.  Full audit:
  `fanout/wave5/C114_integrated_carleson_audit.md`.

## C109 fixed-root growth audit (2026-07-13)

- Root `54` reaches witnessed `d=16` at `h=1559219514`; root `62` reaches
  `d=16` at `h=298274514`.  Thus fixed reducible roots carry substantially
  more load than earlier scans showed.
- A one-root C104-BIN violation in their bin requires `d>=34`; neither the
  complete `4e9` prefix nor targeted 64-bit families reach it.
- An independently rebuilt full bin scan through `4e9` is byte-identical,
  with `106360959` hard sources and no C104-BIN failure.  The independently
  rebuilt record scan agrees in every mathematical field (timings differ).
- The 21-entry manifest and normal/-O record verifier pass.  C104-BIN and
  fixed-root unboundedness both remain open.  Full audit:
  `fanout/wave5/C109_fixed_root_growth_audit.md`.

## C117 structural-power falsifier audit (2026-07-13)

- Six sparse-template lanes made 192,500 declared evaluations and 186,819
  exact recursive classifications.  They found eight hard survivors, no
  counterexample to `(s+8)^4>=d^3`, maximum tested `d=128`, and largest
  tested source `132131012341607575950114`.
- Every one of 86,319 classified divisor-raising sources is generated.  All
  hard survivors preserve the divisor shape under a prime-slot substitution;
  the best `d=16` survivor has `s=9` and seven nonstructural blocker roots.
- All six artifact hashes pass.  Independent normal/optimized replay and a
  rebuilt manifest are byte-identical, with SHAs `0DB3E133...9CC1` and
  `4FB5E1CF...1FCE`.  This is finite falsification evidence only; the C112
  power antecedent remains open.  Full audit:
  `fanout/wave5/C117_structural_power_falsifier_audit.md`.

## C119 atomic coprime-swap obstruction (2026-07-13)

- AO1 is false at `K=3`:
  `2131353*8825=2144475*8771=18809190225`, with reduced swap factors
  `8771=7^2*179` and `8825=5^2*353`.
- The fibre has exactly those two representations, so the non-atomic swap
  cannot be decomposed through a third atomic representation.  The complete
  `K<=4` census contains 61,074,225 labelled edges and reproduces C111's
  `K=4` multiplicity histogram.
- Two C++ runs are byte-identical; independent Python normal/-O replays are
  byte-identical.  Full audit:
  `fanout/wave5/C119_fixed_L_gate_audit.md`.
- This falsifies only atomic prime ownership.  Fixed-`L` Gate T remains open.

## C121 pure-divisor structural relaxation (2026-07-13)

- The closure-free relaxation `2*forced_both_structural>=d(h)-8` is false,
  even after excluding the easy factor-3 shape.  Its first exact failure below
  `10^6` is `h=237404`, with `d=12` and only one pair having structural roots
  at both endpoints.
- This value is generated (`237405=17*13965`) and therefore is not an actual
  hard hole.  An explicit derivation tree is recorded in
  `fanout/wave5/C121_pure_divisor_relaxation.md`.
- Hence C116 cannot be reduced to a theorem about complementary divisors and
  seed roots alone; a proof must use the absence of every generated factor
  pair, i.e. two-seed derivation history.
- The normal and optimized exact outputs are byte-identical, SHA-256
  `BA233A0A...2C26F4`.
