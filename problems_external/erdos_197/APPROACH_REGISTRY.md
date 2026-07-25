# Erdős Problem 197 — Approach Registry

## Statement

Partition \(\mathbb N\) into two sets \(A_0,A_1\). For each \(c\in\{0,1\}\),
construct an enumeration \(e_c:\mathbb N\to A_c\) such that no three distinct
values in arithmetic progression occur in increasing or decreasing value order
along the enumeration.

Equivalently, if
\[
x,\quad x+d,\quad x+2d\in A_c\qquad(d>0),
\]
then their three positions under \(e_c^{-1}\) are neither increasing nor
decreasing.

## DIRECT ROUTE R1 — finite-state 2-adic construction

1. **Exact final deliverable.** An explicit two-colouring \(c:\mathbb N\to
   \{0,1\}\), explicit bijections \(e_i:\mathbb N\to c^{-1}(i)\), and a proof
   that every monochromatic three-term arithmetic progression has a
   non-monotone position pattern in its colour's enumeration.
2. **Current frontier lemma or finite certificate.** A finite-state
   block-recursive certificate whose transition table simultaneously assigns
   colours and orders every block, together with a finite invariant proving
   that the first decisive binary digit of any monochromatic progression forces
   a peak or valley in its position pattern.
3. **Logical bridge.** The block recursion must partition every positive
   integer exactly once and give both induced orders order type \(\omega\).
   The invariant then applies to every \(x,d>0\), so the two induced
   enumerations are the required partition and permutations.
4. **Next falsifiable action.** Enumerate small binary block morphisms and
   state-transition invariants; reject a template immediately by an exact
   progression witness, and promote a survivor only if its transition graph
   admits a finite inductive invariant covering arbitrary bit length.
5. **Exit condition.** Exit with success only after the construction and
   invariant are independently replayed. Exit this route as
   `DEAD: finite-state route — no inductive invariant for the frozen template
   classes` if the audited template classes are exhausted and no new direct
   finite-state mechanism is identified.

## DIRECT ROUTE R2 — finite extension lemma and compactness

1. **Exact final deliverable.** The same explicit partition and enumerations,
   or a nonconstructive existence proof with all compactness steps stated.
2. **Current frontier lemma or finite certificate.** A uniform finite extension
   lemma: every valid ordered two-colouring of an initial interval can be
   extended across a quantitatively specified next block while preserving all
   old and crossing progression constraints.
3. **Logical bridge.** Iterating the uniform extension lemma gives nested valid
   finite objects. König's lemma yields infinite colour orders; an explicit
   fairness condition in the extension lemma guarantees that every integer
   appears and that both orders have type \(\omega\).
4. **Next falsifiable action.** Formulate the exact finite extension CSP and
   test the smallest block ratios exhaustively, extracting either a reusable
   symmetry/averaging proof or a minimal obstruction.
5. **Exit condition.** Exit with success only after a proved uniform extension
   lemma. Exit as `DEAD: compactness route — finite feasibility has no uniform
   extension bridge` if only unrelated bounded instances remain.

## Audit route A1 — definition and certificate audit

1. **Exact final deliverable.** Independent verification that the proposed
   construction matches the original monotone-AP definition.
2. **Current frontier lemma or finite certificate.** A verifier that checks
   colour partition, bijectivity on finite prefixes, and both increasing and
   decreasing position patterns for every finite three-term progression.
3. **Logical bridge.** The verifier is a falsification tool; a proof still
   requires the R1 invariant or R2 extension lemma.
4. **Next falsifiable action.** Differentially test two independent checkers on
   hand-built positive and negative examples before accepting search output.
5. **Exit condition.** Any parser, convention, or verifier disagreement blocks
   promotion of a candidate.

## Prohibited substitutes

- A valid construction only up to a finite cutoff.
- A density bound for one avoidable set.
- A three-set partition.
- Avoidance of progressions with only selected common differences.
- An order on a colour class that is not an enumeration of order type
  \(\omega\).
- Solver `UNKNOWN`, timeout, or bounded `NO_HIT`.

## Route status — 2026-07-23

- **R2 DEAD.** `R2_OBSTRUCTION.md` gives a valid ordered colouring of `[10]`
  to which 11 cannot be added in either colour at any position. The universal
  extension frontier is false. Any replacement must specify a provably
  extendible invariant subclass before computation.
- **R1 DEAD.** The audited automatic templates exhaust 2,342,592 cases and
  none survives through `[31]`; the best prefix reaches `[15]` and is
  independently replayed. `R1_ANNULAR_OBSTRUCTION.md` proves a quantified
  three-block obstruction for the annular family and gives an explicit forced
  precedence cycle at `r=6`, `lambda=12/5`. The remaining parameter continuum
  has no finite inductive invariant or theorem-closing bridge. Therefore this
  route exits as `DEAD: reformulation maze — no inductive invariant connecting
  the surviving finite-state or annular templates to all positive integers`.

