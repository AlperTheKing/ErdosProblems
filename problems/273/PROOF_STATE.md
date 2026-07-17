# Proof State


## Current lemma tree

### Lemma P (parity split)

Let `D` be a finite set of distinct integers `d >= 2` such that `2d+1` is prime. Every allowed modulus is `m=2d`. A congruence modulo `2d` has fixed parity.

For an even residue `a=2b`,

`2x ≡ 2b (mod 2d)` iff `x ≡ b (mod d)`.

For an odd residue `a=2b+1`,

`2x+1 ≡ 2b+1 (mod 2d)` iff `x ≡ b (mod d)`.

Therefore a p >= 5 certificate is equivalent to two covering systems of `Z`, one for each parity, whose half-modulus sets are disjoint and whose every modulus `d` satisfies `2d+1` prime. Lifting uses residues `2b` and `2b+1` modulo `2d`. Distinct half-moduli give distinct original moduli.

### Lemma B360 (reconstructed p >= 3 baseline)

A normalized exact reconstruction is

`0(2), 1(4), 1(6), 3(10), 3(12), 11(18), 17(30), 23(36), 35(40), 11(60), 71(72), 179(180)`.

The modulus-2 class covers the even fiber. The other classes are odd and, after applying Lemma P, give the half-cover

`0(2), 0(3), 1(5), 1(6), 5(9), 8(15), 11(18), 17(20), 5(30), 35(36), 89(90)`.

Its half-modulus set is

`H0 = {2,3,5,6,9,15,18,20,30,36,90}`.

### Frontier F1

Find a finite covering system `H1` with pairwise distinct moduli `d`, each satisfying `2d+1` prime, and `d notin H0`. Then lift `H1` to the even fiber and the displayed `H0` cover to the odd fiber. This produces a p >= 5 solution immediately.

Failure of F1 in any bounded or fixed-period family is only a restricted impossibility result; the global problem also permits replacing `H0`.

### Downstream certificate obligations

1. Exact finite search or construction of `H1`.
2. Lift `H0` and `H1` through Lemma P.
3. Check all original moduli are distinct and `m+1` prime.
4. Verify a complete true LCM period with Verifier A.
5. Verify independent residue-tree/CRT containment with Verifier B.
6. Produce human covering tree, hashes, primality certificates, paper, adversarial audit, and Lean certificate.

## Highest-leverage open lemma

`F1`: existence of a distinct admissible half-modulus cover disjoint from `H0`.

## First exact search family

For a proposed half-period `L`, use

`M_half(L) = {d : d | L, 2d+1 prime, d >= 2, d notin H0}`.

Choose at most one residue modulo each `d` and require coverage of every residue modulo `L`. Begin with smooth multiples/extensions of `180`; record every family restriction exactly.

## Lemma T5 (infinite smooth-tail bound)

Let `P={2,3,5,7,11}` and let `E` be all `P`-smooth integers `d>=2` with `2d+1` prime and `d notin H0`. Let `B` be the exponent box `(8,5,3,2,1)`. Splitting `E` into elements inside and outside `B` gives

`sum_{d in E} 1/d <= S_B + (G_P - G_B)`,

where `S_B=462476029/598752000` is the exact eligible mass inside the box,

`G_P = product_{p in P} (1-1/p)^(-1)`

is the reciprocal mass of every `P`-smooth integer, and

`G_B = product_i sum_{j=0}^{e_i} p_i^(-j)`

is the reciprocal mass of every divisor in the scanned box. The inequality replaces the eligible outside-box tail by the full outside-box smooth tail. If its right side is below 1, no H1 cover supported on `P` exists for any exponents.

Exact evaluation for Lemma T5:

- `G_P = 77/16`.
- `G_B = 234403/49500`.
- `G_P-G_B = 15263/198000`.
- `S_B+(G_P-G_B) = 508631341/598752000`.
- The gap from 1 is `90120659/598752000 > 0`.

Hence no half-cover disjoint from `H0` can use only moduli whose prime factors lie in `{2,3,5,7,11}`, regardless of exponent bounds.

## Lemma D140 (density threshold for fixed-H0 refinement)

Among all admissible half-moduli `d` with `2d+1` prime and `d notin H0`, the exact reciprocal sum first exceeds 1 at `d=140` (prime successor 281). There are 47 candidates through 140:

`8,11,14,21,23,26,29,33,35,39,41,44,48,50,51,53,54,56,63,65,68,69,74,75,78,81,83,86,89,95,96,98,99,105,111,113,114,116,119,120,125,128,131,134,135,138,140`.

The sum through the first 46 is

`49277588894329808414813335962031 / 49555061802583614776595528432000 < 1`,

and after adding `1/140` it is

`49631553621491119948931875450831 / 49555061802583614776595528432000 > 1`.

The excess is smaller than the reciprocal of every listed modulus, so if an H1 cover has maximum half-modulus at most 140, it must use all 47 candidates. Canonical LF list SHA-256: `1af3c5b9a10674c3cae8256173f4e3c727e0cf6cf7b25cfd5120c1b4e8814473`.

## Lemma F8 (mod-8 forced-waste obstruction at d <= 140)

By Lemma D140, any fixed-H0 half-cover with maximum modulus at most 140 must use all 47 admissible candidates through 140. In particular it uses one class `A_8` modulo 8, which completely covers one fiber `F` modulo 8.

For every odd candidate modulus `d`, every class modulo `d` meets `F` in global density exactly `1/(8d)` by CRT. This density is forced redundancy inside the already-covered fiber. Even-modulus classes contribute a nonnegative additional redundancy, which may be discarded for an upper bound.

Let `S` be the exact reciprocal sum of all 47 candidates. A necessary condition to cover the complement of `F`, of density `7/8`, is

`(S - 1/8) - sum_{odd d} 1/(8d) >= 7/8`,

or equivalently

`sum_{odd d} 1/(8d) <= S-1`.

Exact values are:

- `S-1 = 76491818907505172336347018831 / 49555061802583614776595528432000`;
- forced odd waste `= 5164400519232437732730583 / 76788599262693408130540500`;
- waste minus slack `= 3256323069776033123854938336721 / 49555061802583614776595528432000 > 0`.

Therefore no H1 cover disjoint from H0 has maximum half-modulus at most 140.

## Lemma R1 (one-prime support exclusions)

For each `r in {17,19,23,29,31,37,41,43,47}`, every admissible fixed-H0 half-modulus supported on `{2,3,5,7,11,r}` has total reciprocal mass below 1, even with arbitrary exponents. This follows by exact enumeration in the inclusive box `(8,5,3,2,1,1)` plus the full smooth reciprocal tail outside the box. The support with `r=13` is not resolved by this bound.

## Target J27720 (joint two-cover search)

Without fixing `H0`, the least scanned smooth period passing the joint density screen is `L=27720=2^3*3^2*5*7*11`. It has 43 admissible divisors `d` with `2d+1` prime and total reciprocal mass `6429/3080 > 2`. The 43 moduli admit a complete disjoint reciprocal-mass partition with sums `263/252` and `4133/3960`, both above 1. These are necessary conditions only; residues covering both copies of `Z/LZ` remain to be found or ruled out exactly.

For Lemma T5 and Lemma R1, every listed exponent cap is inclusive.

## Lemma T13 (six-prime fixed-H0 tail bound)

Let the allowed prime support be `{2,3,5,7,11,13}`. In the inclusive exponent box `(8,5,3,2,2,6)`, excluding `H0`, the exact eligible mass is `206435194374323669/222534738762336000`. The reciprocal mass of every smooth integer outside this box is `33326826113/746470296000`. Their sum is

`216370454467826777/222534738762336000 = 1 - 6164284294509223/222534738762336000 < 1`.

Hence no fixed-H0 half-cover exists on this full six-prime support at any exponents.

## Lemma B185 (bounded fixed-H0 obstruction)

Let `A_B={d:2<=d<=B, d notin H0, 2d+1 prime}` and `S_B=sum_(d in A_B)1/d`. At `B=185`, density forces modulus 11 because `S_185-1/11<1`. Every class with modulus coprime to 11 has forced intersection density `1/(11d)` with the selected 11-class. The forced overlap exceeds total slack by

`138457791684833691407794193043540808659347 / 78655028798323317249846838879985572894929600 > 0`.

Thus no fixed-H0 refinement with maximum half-modulus at most 185 exists. At the next candidate `d=186`, no individually density-forced single anchor gives this obstruction; monotonicity makes 185 maximal for this method.

## Lemma J27720 (restricted joint obstruction)

For `D={d:d|27720,d>=2,2d+1 prime}`, the exact total mass is `T=6429/3080=2+269/3080`. Since `T-1/5<2`, modulus 5 is mandatory in one of the two disjoint half-covers, say `C`. The other cover has mass at least one, so the slack of `C` is at most `269/3080`.

The total available mass from moduli divisible by 5 is `3049/6930`. The coprime-overlap inequality at the chosen 5-class bounds the remaining mass in `C` by `5*(269/3080)`. Consequently

`mass(C) <= 3049/6930 + 5*(269/3080) = 24301/27720 < 1`,

a contradiction with exact deficit `3419/27720`. Therefore no two disjoint half-covers using only divisors of 27720 exist. An independent exhaustive tree has 5,095 nodes, 3,384 exact prunes, and zero leaves.

## Current joint frontier

Exact overlap-capacity screening rejects the first targets `L=27720`, `L=55440`, and `L=110880`. The first screened capacity-feasible target is `L=138600`, with 64 admissible half-moduli and total mass `296663/138600`. The first exported allocation's 12-modulus side is residue-infeasible; other allocations are under exact search.

## Lemma Mq (single mandatory-anchor obstruction)

For a finite joint candidate pool `D`, put `T=sum_(d in D)1/d=2+delta` and `N_q=sum_(gcd(d,q)>1)1/d`. If `q` is mandatory (`T-1/q<2`) and `N_q+q*delta<1`, then two disjoint covers cannot exist. Indeed, in the cover containing `q`, the other cover's mass bounds its slack by `delta`; CRT overlap bounds its selected coprime mass by `q*delta`, while its noncoprime mass is at most `N_q`. Thus its total mass is below one. An exact scan certifies this obstruction for 136 of the 296 density-passing smooth periods.

## Lemma J55440 (restricted joint obstruction)

For `D={d:d|55440,d>=2,2d+1 prime}`, there are 52 candidates, total mass `117517/55440`, and mandatory set `{2,3,5,6,8}`. Moduli 2 and 3 must lie in opposite covers. For all eight placements of 5, 6, and 8, an exact rational Farkas ray proves even the continuous relaxation of the remaining allocation inequalities infeasible, each reducing valid inequalities to `0<=-1`. A standard-library verifier checks all rays, and an independent local-union certificate kills all 420 viable mandatory residue configurations with maximum combined coverage `104063/55440<2`.

## Fixed-allocation cut at J138600

The first capacity allocation has side `A={2,6,8,14,18,30,44,50,308,504,5775,6300}` and total incidence only 38 points above `L=138600`. Any intersection among the selected classes modulo 2, 6, and 8 would contain respectively 23100, 17325, or 5775 points, exceeding all available excess. The three classes would therefore need three pairwise distinct parities, impossible modulo 2. This rejects that allocation exactly; it does not reject the full period.

## Lemma J110880 (restricted joint obstruction)

For `D={d:d|110880,d>=2,2d+1 prime}`, there are 58 candidates with total mass `11861/5544`. The forced moduli 2 and 3 must be on opposite sides. If forced modulus 5 joins the 2-side, exact candidate-wise capacity is at most `5039/2520=2-1/2520`. If it joins the other side, weighting the anchor-2 inequality by `4/5` gives capacity at most `22173/12320=9/5-3/12320`. Both branches contradict the required capacity, exhausting the placement of 5. The independent verifier rejects 13 mutations.

## Lemma Hmin (baseline half-cover minimality)

For `H={2,3,5,6,9,15,18,20,30,36,90}`, a cover of `Z/180Z` using at most one class per modulus must use every member of H. CP-SAT checks all 2048 subsets; independently, exhaustive bit-mask trees for the 11 maximal proper subsets visit 396679 nodes with no feasible leaf. Hence changing the baseline residues cannot free any half-modulus for the complementary cover.

## Lemma J83160 (restricted joint obstruction)

For the 58 admissible divisors of 83160, total mass is `11827/5544` and `2,3,5,6` are mandatory. Moduli 2 and 3 lie on opposite sides. The four placements of 5 and 6 have exact weighted anchor-capacity deficits `181/27720`, `181/27720`, `227/83160`, and `598/17325`. Thus no two disjoint half-covers supported on divisors of 83160 exist.

## Lemma J138600 (restricted joint obstruction)

Let D={d:d|138600, d>=2, 2d+1 prime}. Then |D|=64 and sum_(d in D) L/d=296663 for L=138600. Projecting two putative disjoint covers to the twelve labeled cells modulo 6 leaves total scaled excess E=6(296663-2L)=116778. Mandatory moduli 2 and 3 lie in opposite covers. The class modulo 6 either joins the 2-cover at an odd cell, forcing saturated-cell incidence 2(44352+45513)=179730, or joins the 3-cover away from residue 0 mod 3, forcing incidence 3*44352=133056. Both exceed E. Hence no two disjoint half-covers supported on divisors of 138600 exist. Two independent exact verifiers reconstruct D and check every placement; the 27-file hash manifest passes.

## Current joint frontier update

The exact restricted obstructions now eliminate the density-passing half-periods 27720, 55440, 83160, 110880, and 138600. The least period surviving the exact q=6 screen is L=166320; quotient projections are under independent exact audit.

## Lemma J32760 (restricted joint obstruction)

For D={d:d|32760,d>=2,2d+1 prime}, there are 45 candidates and T=66233/32760=2+713/32760. Modulus 5 is mandatory. The full mass from moduli noncoprime to 5 is 2453/5460, while the selected coprime mass in the cover containing 5 is at most 5(T-2). Thus that cover has mass at most 18283/32760<1, with gap 14477/32760. An independent verifier reconstructs all candidates and rejects six mutations.

## Lemma Q6Q30 (finite five-prime quotient screen)

In the inclusive box (8,5,3,2,1) on support {2,3,5,7,11}, exactly 296 periods have total admissible mass above two. Exact saturated-cell projection modulo 6 eliminates 166. Branching on modulus 6 and projecting all mandatory anchor configurations modulo 30 eliminates 19 more. An independent integer-weight implementation checks every quotient state and minimizing mask. Exactly 111 periods survive; the least is 831600. This is a restricted finite screen.

## Lemma J166320 (restricted joint obstruction)

For L=166320 there are 71 candidates. The q=6 projection has total excess 165474. Normalized anchors force modulus 6 into the 3-cover away from residue 0 mod 3, and the coprime moduli 5,11,35 leave only 6066 excess; modulus 8 is therefore forced into the 2-cover at an odd residue. At q=24 the forced saturated-cell incidence is 708912, exceeding the available 661896 by 47016. Two independent verifiers check all 16 surviving q=24 anchor cases.

## Lemma J221760 (restricted joint obstruction)

For L=221760 there are 68 candidates, total integer weight 476218, and q=6 excess 196188. After normalizing moduli 2 and 3 into opposite covers, modulus 6 forces saturated incidence 281412 if placed with modulus 2 and 212544 if placed with modulus 3. Both exceed the available excess, with gaps 85224 and 16356. The independent verifier exhausts all 24 normalized anchor placements.

## Lemma R105525 (admissible fiber refinement)

The quotient classes 0(2),0(3),1(4),5(6),7(12) cover every residue modulo 12. With d=105525, composition gives the exact identity 0(d)=0(2d) union 0(3d) union d(4d) union 5d(6d) union 7d(12d). The five child half-moduli 211050,316575,422100,633150,1266300 are distinct and have prime successors 422101,633151,844201,1266301,2532601; the parent successor 211051 is prime. Two independent exact checkers verify equality over period 1266300, primality, Pocklington witnesses, and six mutations. This is a collision-removal gadget, not a global cover.

## Current joint frontier update

Within the verified five-prime box the least q=6/q=30 survivor is L=831600. In the independently audited six-prime box including 13, the smaller period L=360360 has an exact feasible overlap allocation and is under quotient/residue attack. Neither allocation is a covering certificate.

## Lemma J360360 (restricted joint obstruction)

For L=360360, the 79 admissible half-moduli have total integer weight 796909. An exact q=24 anchor enumeration has 384 normalized cases. Saturated-cell bounds eliminate 368, with minimum gap 134976. Each of the remaining 16 cases has a ten-cell demand 3603600 but capacity at most 3395880, a gap of 207720. Two independent integer verifiers pass and seven mutations are rejected.

## Lemma J831600 (restricted joint obstruction)

For L=831600, exact q=120 enumeration over 4862 normalized states branches on mandatory moduli 2,3 and optional anchors 5,6,8. The minimum forced charge is 20737/92400, while available slack is 30383/138600. Their difference is 289/55440>0. Two independent verifiers reproduce the minimum and its multiplicity 80.

## Lemma J997920 (restricted joint obstruction)

For L=997920, the analogous 4862-state q=120 enumeration has minimum forced charge 737/3360 and available slack 68903/332640. The exact gap is 29/2376>0. Independent bitset and set/Fraction verifiers agree.

## Lemma J1108800 (restricted joint obstruction)

For L=1108800, there are 101 candidates. The q=120 anchor enumeration over 4862 states has minimum charge 5957/26400 and slack 74933/369600, with exact gap 1693/73920>0. Two independent exact implementations pass.

## Lemma R3Q420 (bounded refinement obstruction)

For parent half-modulus d=3 and quotient moduli restricted to divisors of 420, exact primality leaves 13 candidates. A solver-independent least-uncovered-residue tree visits 37688965 memoized states and finds no quotient cover, even before excluding collisions with H0. Independent CP-SAT returns INFEASIBLE after 17968 branches. This is restricted to q|420.

## Lemma R15Q13860 (bounded refinement obstruction)

For parent d=15 and quotient period 13860, the 31 admissible quotient moduli have total mass 1157/1155. Moduli 5 and 7 are individually mandatory and coprime, so their selected classes intersect with density 1/35. The total union is therefore at most 1157/1155-1/35=1124/1155<1, with deficit 31/1155.

## Lemma R90Q49140 (bounded refinement obstruction)

For parent d=90 and quotient period 49140, six moduli 3,9,10,12,13,14 are mandatory. Exhausting their 196560 normalized residue placements gives maximum mandatory union 10560/16380. Granting every other candidate its full reciprocal mass yields total coverage at most 11152/12285<1, with deficit 1133/12285. An independent inclusion-exclusion replay reproduces the entire 15-bin histogram.

## Lemma R90Q196560 (bounded refinement obstruction)

For parent d=90 and quotient period 196560, q=3 is mandatory because all other candidates have mass 76957/98280<1. Normalize its class to 0 mod 3. Moduli divisible by 3 contribute at most their full mass outside it, while every other class contributes only 2/(3q). The total outside capacity is 13073/19656=2/3-31/19656, a deficit of 310 residues modulo 196560. Two independent exact candidate censuses verify the bound.

## Current frontier update

The least unresolved six-prime period in the audited box is L=655200. After exact five-prime exclusions through L=1108800, the next five-prime target is L=1247400. The d=90 refinement census is being screened by the normalized-q=3 capacity lemma. No explicit pair of disjoint half-covers exists yet.

## Lemma Q30-extended (finite eight-prime quotient screen)

On support {2,3,5,7,11,13,17,19} with exponent caps (8,5,3,2,1,1,1,1), 3402 periods have admissible reciprocal mass above two. The exact q=6 screen eliminates 1273. Direct q=30 union-state enumeration, branching on modulus 6, eliminates 340 additional q=6 survivors. Thus 1789 periods survive and the least is 360360. An independent verifier regenerates candidates with SymPy and recomputes every bound using integer weights grouped by gcd(d,30).

## Lemma J655200 (restricted joint obstruction)

For L=655200 there are 91 admissible half-moduli. The q=120 enumeration over 4862 normalized states using anchors 2,3,5,6,8 has minimum forced charge 15352920/(120L), while the available slack is 9834240/(120L). The exact positive gap is 5518680/(120L)=45989/655200. Independent integer/bitset and Fraction/set verifiers pass.

## Lemma J720720 (restricted joint obstruction)

For L=720720 there are 96 admissible half-moduli. Anchors 2,3,5,6,8 alone do not obstruct, but adding admissible modulus 15 gives 150722 normalized q=120 states. Their minimum forced charge is 24608520/(120L), versus slack 21361320/(120L), with gap 3247200/(120L)=41/1092. Two independent complete enumerations and a scope audit pass.

## Lemma J1247400 (restricted joint obstruction)

For L=1247400 there are 101 admissible half-moduli. The 4862-state q=120 anchor enumeration has minimum 33423840/(120L), slack 31097280/(120L), and positive gap 2326560/(120L)=4847/311850. Two independent exact verifiers pass.

## Lemma J1330560 (restricted joint obstruction)

For L=1330560 there are 98 admissible half-moduli. The 4862-state q=120 enumeration has minimum 35323560/(120L), slack 32780520/(120L), and gap 2543040/(120L)=883/55440. Two independent exact verifiers pass.

## Lemma R90Q393120 (bounded refinement obstruction)

For the d=90 quotient family, an exact q=3 screen checks all 602 density-passing periods: modulus 3 is mandatory in every row, 320 are eliminated, and 282 survive. At the least survivor Q=393120, 62 candidates remain. Splitting modulo 9 gives nine exact cases: overlap cases require at least 810432 against budget 420930, while disjoint cases require at least 556416. The minimum contradiction gap is 135486. Independent SymPy and solver-independent replays pass.

## Current frontier update

No explicit pair of disjoint half-covers exists in the artifacts. The active period attacks are L=1081080 and L=1413720; the next d=90 quotient is Q=589680. All lemmas above are restricted finite-family obstructions.
