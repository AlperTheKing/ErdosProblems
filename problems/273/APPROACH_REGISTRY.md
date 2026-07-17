# Approach Registry


## A1 — Published Selfridge residues

**Status:** source obstruction. Erdős–Graham p. 24 asserts existence but gives no residues/citation. The displayed 12-class system is an exact reconstruction, not a historical identification.

## A2 — p >= 5 using only divisors of 360

**Status:** DEAD. The eligible set after excluding modulus 2 is `{4,6,10,12,18,30,36,40,60,72,180}` and its exact reciprocal sum is `7/9`. Any union of one class per distinct modulus has density at most `7/9`, so it cannot cover.

## A3 — Parity split and disjoint half-covers

**Status:** ALIVE; current frontier F1. A p >= 5 cover is equivalent to two disjoint distinct covers with half-moduli `d` satisfying `2d+1` prime. The reconstructed 360 odd fiber supplies `H0={2,3,5,6,9,15,18,20,30,36,90}`.

## A4 — Smooth half-period scan

**Status:** ACTIVE. Exact scan over 1296 periods `2^a3^b5^c7^e11^f`, with `(a,b,c,e,f)` bounded by `(8,5,3,2,1)`, ranks H1 families by exact reciprocal mass before SAT.

## A5 — General two-half-cover search

**Status:** RESERVED. If complementing H0 is infeasible in tested families, jointly select two disjoint admissible half-covers instead of fixing H0.

## A4 update — smooth fixed-H0 support

**Status:** DEAD for the full prime support `{2,3,5,7,11}`, at arbitrary exponents, by Lemma T5. Nine single-prime extensions with `r in {17,19,23,29,31,37,41,43,47}` are also dead by Lemma R1; `r=13` remains alive.

## A5 update — general two-half-cover search

**Status:** ACTIVE. Exact joint density screening selects `L=27720` with 43 admissible half-moduli as the least finite target. A full two-fiber residue assignment is being solved exactly; density partitioning alone is not a covering certificate.

## A3 update — fixed-H0 frontier closed on six-prime support

**Status:** DEAD for every half-modulus supported on `{2,3,5,7,11,13}` at arbitrary exponents, by Lemma T13. Independently, any fixed-H0 refinement with maximum half-modulus at most 185 is dead by Lemma B185. Neither result is a global obstruction to fixed-H0 refinements using other primes and larger moduli.

## A5 update — period 27720 dead; period 138600 active

**Status:** `L=27720` is DEAD by Lemma J27720 and an exact exhaustive tree. Overlap-capacity models also reject `L=55440` and `L=110880`, pending complete independent certificates for those two solver results. `L=138600` is ACTIVE: its capacity system is feasible, while its first 12-modulus allocation is residue-infeasible; alternate allocations are being enumerated.

## A5 update — certified 55440 obstruction

**Status:** `L=55440` is DEAD by eight exact Farkas rays and an independent 420-case local-union certificate. The first `L=138600` allocation is also DEAD by a three-parity pigeonhole obstruction, while the full `L=138600` period remains ACTIVE.

## A5 update — exact quotient screens and split frontier

Status: ACTIVE. Exact certificates now rule out joint periods 32760, 27720, 55440, 83160, 110880, 138600, 166320, and 221760. In the five-prime exponent box, the combined q=6/q=30 screen has least survivor 831600. Adding prime 13 yields the smaller allocation survivor 360360; both branches remain construction targets.

## A6 — fiber-composition collision removal

Status: ALIVE as a verified local transformation. Lemma R105525 replaces one admissible parent fiber by five distinct admissible child fibers, all above 138600. It is being tested as a recursive way to remove duplicated half-moduli from two covers. No global pair of disjoint half-covers follows from the gadget alone.

## A7 — broader support census

Status: ACTIVE. The exact eight-prime census covers 10368 periods and its mandatory-anchor screen removes 918 of 3402 mass-supercritical rows. It supplies rankings beyond the original five-prime family without treating density or allocation feasibility as coverage.

## A5 update — later smooth-period obstructions

Status: ACTIVE. Exact quotient certificates now also eliminate L=360360, 831600, 997920, and 1108800. The active incompatible targets are L=655200 on support including 13 and L=1247400 on the five-prime support.

## A6 update — refinement census reaches baseline fibers

Status: ACTIVE but no collision removed yet. Every H0 parent reaches reciprocal mass one in the stated quotient box, but exact finite obstructions kill d=3,Q420, d=15,Q13860, d=90,Q49140, and d=90,Q196560. The isolated R105525 gadget remains valid; it is not attached to H0.

## A5 update — q30-ranked periods through 1330560

Status: ACTIVE. Exact certificates now also eliminate L=655200, L=720720, L=1247400, and L=1330560. The strengthened L=720720 proof needs anchor 15. The active q30-ranked period targets are L=1081080 and L=1413720; no finite cover has yet been found.

## A6 update — d=90 quotient frontier

Status: ACTIVE. The exact q=3 screen eliminates 320 of 602 density-passing quotient periods. The least survivor Q=393120 is DEAD by a q=9 obstruction with minimum scaled gap 135486. The next quotient target is Q=589680.

## A7 update — independently audited extended q30 screen

Status: ACTIVE. In the eight-prime exponent box, q=6 and q=30 eliminate 1613 of 3402 mass-supercritical periods. Exactly 1789 survive; this remains a bounded screen and does not imply global nonexistence.

## DIRECT ROUTE — governing entry

1. **Final deliverable:** either an explicit finite pair of disjoint half-covers with every `2d+1` prime, hence a verified covering system for Problem 273, or a global theorem excluding all such systems.
2. **Current frontier:** no direct frontier is presently established. The verified `R105525` refinement gadget is not connected to any baseline collision, and no explicit disjoint half-cover pair exists.
3. **Bridge:** a construction branch may resume only with an explicit finite refinement/covering certificate whose composition into the final pair is stated. A negative branch may resume only with a lemma quantified over all admissible moduli, not one common-period family.
4. **Next falsifiable action:** none authorized until such a bridge is written here. Do not select another smooth period, quotient period, support box, or asymptotic surrogate merely because it is the next survivor.
5. **Exit condition:** immediately stop any branch whose output is only another restricted-family obstruction or equivalent reformulation and does not strengthen the stated bridge.

## Guard decision — restricted-screen cascade stopped

**Status: STOPPED.** The A4/A5/A7 sequence of smooth-period, q30/q120, and successive quotient-family exclusions produced exact bounded results but no explicit disjoint half-cover and no global impossibility bridge. Further ranked-period and `d=90` survivor attacks are prohibited under the direct-proof guard unless a new direct route is first recorded above.
