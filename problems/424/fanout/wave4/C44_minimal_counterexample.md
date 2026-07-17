# C44: minimal-counterexample descent audit

## Verdict

The additive-one theorem

\[
 H_{\le d}(X)\le Q_{\le d}(X)+1                         \tag{AO}
\]

is not proved here, and neither is the weaker asymptotic estimate
\(H(X)\le Q(X)+o(X)\).

A first violation can be normalized rigorously.  It occurs at an even hard
event \(X\), changes the relevant excess from exactly one to exactly two,
and has a critical odd blocker whose seed-2 predecessor is a smaller hole
at least two obstruction ranks lower.  The blocker also has a seed-3 child
strictly below \(X\).  These are genuine descent facts.

The missing implication is global: the smaller blocker data need not yield
an arrived target of compatible rank, nor a same-rank smaller obstruction.
Exact least-grounded counterexamples kill each such conversion.  The first
component-timing failure is at `74`; the first failure of both seed children
to be generated or have the source rank is at `774`.  Through `10^6`, a
rank-two source has a critical seed-3 child of rank thirteen, so rank
inflation along the proposed descent is not even bounded by a small constant.

An independent exact scan through `10^6` found no failure of (AO).  A
trial-division implementation with literal descending approximants agreed
on every membership and rank through `1000`.  This is finite verification,
not a proof.

## 1. Definitions

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},
\]

and let \(G\) be the least subset of \(\mathcal A\) containing `2,3` and
closed under \(a,b\mapsto ab-1\) for distinct \(a<b\).  For an allowed
hole \(n\), put

\[
 \mathcal P(n)=\{(a,b):2\le a<b,\ a,b\in\mathcal A,\ ab=n+1\}.
\]

The obstruction rank is

\[
 \rho(n)=0\quad\text{if }\mathcal P(n)=\varnothing,
\]

and otherwise

\[
 \rho(n)=1+\max_{(a,b)\in\mathcal P(n)}
 \min\{\rho(x):x\in\{a,b\}\setminus G\}.                \tag{1}
\]

A hard hole is a reducible even hole outside the usable seed-3 class, as in
C31/C40.  A target is a missing `q` whose child \(2q-1\) is generated; its
event coordinate is the child and its rank is \(\rho(q)\).  Write

\[
 B_d(X)=H_{\le d}(X)-Q_{\le d}(X).                       \tag{2}
\]

Thus (AO) is the assertion \(B_d(X)\le1\) for every \(X,d\).

## 2. Exact event form

### Lemma 1 (event residues)

Every hard event is congruent to `0` or `2` modulo `6`.  Every target event
is congruent to `3` or `5` modulo `6`.  In particular, hard and target
events never tie.

### Proof

A hard event is allowed and even.  The even residue `4` modulo `6` is
forbidden modulo `3`, leaving `0,2`.  A target child is allowed and odd.
The odd residue `1` modulo `6` is forbidden, leaving `3,5`.  QED.

For fixed `d`, list the hard event coordinates of rank at most `d` as

\[
 h_1<h_2<\cdots
\]

and the target coordinates of rank at most `d` as

\[
 t_1<t_2<\cdots.
\]

### Lemma 2 (order-statistic form)

For fixed `d`, (AO) at every cutoff is equivalent to

\[
                         t_{j-1}<h_j                     \tag{3}
\]

for every `j>=2` for which `h_j` exists, with a missing `t_{j-1}` treated
as failure.

### Proof

At `h_j`, (AO) requires at least `j-1` arrived targets.  This is equivalent
to \(t_{j-1}\le h_j\), and Lemma 1 makes equality impossible.  Between hard
events the excess can only decrease, so checking the hard coordinates is
sufficient.  QED.

### Lemma 3 (first-violation normalization)

Assume \(X\) is the least coordinate for which (AO) fails for some rank,
and choose the least such `d` at `X`.  Then:

1. `X` is a hard event of some rank `r<=d`;
2. \(B_d(X-1)=1\) and \(B_d(X)=2\);
3. if `d>0`, then \(B_{d-1}(X)\le1\).

One may not conclude from these facts that `r=d`.

### Proof

Only a hard event can increase (2), so `X` is hard and its rank is at most
`d`.  Minimality of `X` gives \(B_d(X-1)\le1\).  The event adds exactly one
to this prefix and the resulting integer is greater than one, forcing the
values one and two.  Minimality of `d` gives the last assertion.  QED.

## 3. What the rank recurrence really gives

### Lemma 4 (hard rank gate)

Every hard source has obstruction rank at least two.

### Proof

All factors of its odd successor are odd.  Every missing factor `q>3` is an
allowed odd hole and has the admissible seed-2 pair

\[
 q+1=2\frac{q+1}{2}.
\]

Its seed-2 predecessor is allowed, distinct from `2`, and missing; otherwise
closure would generate `q`.  Hence every missing odd factor has rank at
least one.  Equation (1) gives hard rank at least two.  QED.

Call a pair in (1) critical for a rank-`r` hole when its minimum missing
rank is `r-1`.

### Lemma 5 (two-rank critical pullback)

Let `h` be a hard hole of rank `r`.  There is a critical pair for `h` and a
missing odd endpoint `q` in that pair such that

\[
 \rho(q)=r-1.
\]

Putting \(p=(q+1)/2\), one has

\[
 p<h,\qquad p\notin G,\qquad \rho(p)\le r-2.             \tag{4}
\]

Following forced seed-2 parents of odd holes and forced seed-3 parents of
3-easy even holes from `p` terminates at a smaller structural root which is
either splitless or hard and still has rank at most `r-2`.

### Proof

The maximum in (1) is attained, giving a critical pair and an endpoint of
rank `r-1`.  Since `h+1` is odd, the endpoint `q` is odd.  Its seed-2
predecessor `p` is allowed and must be missing.  The pair `(2,p)` in the
recurrence for `q` gives

\[
 \rho(q)\ge\rho(p)+1,
\]

which proves (4).  Every forced-parent step decreases both coordinate and
rank.  At termination the hole is even and is neither odd nor 3-easy; it is
therefore splitless or hard.  QED.

### Lemma 6 (smaller seed children)

Let `(a,q)` be a critical pair as in Lemma 5.  Then `a>=5`, and

\[
             2q-1<3q-1<h.                               \tag{5}
\]

If either seed child is a hole, its rank is at least `r`.  If `2q-1` is
generated, it is an arrived target of rank `r-1` before `h`.

### Proof

Both factors are odd.  The cofactor `a` cannot be `3`: since `q` is an
allowed missing value distinct from the seed `3`, `(3,q)` would make `h`
seed-3-easy.  Thus `a>=5`.  Since `h=aq-1`, (5) follows.  The seed pairs
`(2,q)` and `(3,q)` contribute `r-1` to (1), giving the lower rank bounds.
The generated seed-2 case is exactly the target definition.  QED.

Lemmas 5 and 6 are the full unconditional local descent obtained from the
rank recurrence.  Crucially, they give no upper bound on the ranks of the
two smaller seed children.

## 4. The missing rank descent

The minimal lemma tree can now be stated without hiding the frontier.
Consider:

\[
 B_2(X)\le1                                                \tag{Base}
\]

and, for every `d>=3`,

\[
 B_d(X)>0\quad\Longrightarrow\quad B_{d-1}(X)\ge B_d(X).
                                                               \tag{RD}
\]

### Proposition 7

`(Base)` and `(RD)` imply (AO).

### Proof

If \(B_d(X)\ge2\), Lemma 4 gives `d>=2`.  For `d=2`, `(Base)` is a
contradiction.  For `d>=3`, repeatedly apply `(RD)` to obtain
\(B_2(X)\ge2\), again contradicting `(Base)`.  QED.

Neither `(Base)` nor `(RD)` is proved here.  `(RD)` is the exact aggregate
step which a minimal-rank counterexample descent needs.  Lemma 5 does not
prove it: it attaches lower-rank holes to individual factor obstructions,
whereas `(RD)` compares all hard demand with all globally arrived target
capacity.  Fibers over one critical root can be large, and unrelated
components supply the actual target surplus.

## 5. Exact falsifiers for local conversions

The following claims were tested on the actual least grounded set before
being used.  Each is false.

| proposed conversion | first failure | exact obstruction |
|---|---:|---|
| adjacent allowed odd event is a compatible target | `54` | `53` and its parent `27` are both generated |
| a critical component has any arrived seed-2 boundary | `74` | critical `q=15`, root `8`; no root-`8` target before `74` |
| an adjacent odd hole pulls back two ranks | `114` | source rank `2`, but `rho(113)=4`, `rho(57)=3` |
| the critical seed-3 child is generated or has source rank | `174` | critical `q=35`; `rho(104)=3>2` |
| an arrived critical-component boundary is rank-compatible | `492` | root-`8` target `449` has parent `225` of rank `5>3` |
| one of the two smaller seed children is generated or has source rank | `774` | critical `q=155`; ranks of `309,464` are `4,3`, versus source rank `2` |

The rank inflation is not a one-off discrepancy.  Through `10^6`, the
largest observed critical-child jump is

\[
 h=586674,\quad \rho(h)=2,\quad q=117335,\quad
 \rho(3q-1)=\rho(352004)=13.                              \tag{6}
\]

Thus this smaller-coordinate child jumps eleven ranks.  Also, structural
root `6` occurs in `7,230` critical-endpoint pullbacks through `10^6`.
These are finite facts, but they show exactly why one blocker, one root, or
one bounded-rank local object cannot serve as unit capacity.

At `74`, even allowing either an arrived critical-component boundary or a
strictly lower-rank hard root fails: the critical root `8` is splitless and
has no arrived target.  At `492`, timing succeeds but rank compatibility
fails.  These two examples separate the two necessary global issues.

## 6. Exact computation

The main checker reconstructs `G` in increasing order from all admissible
divisors, computes (1), sweeps every hard/target event, and tests all claims
above.

| limit | hard | targets | max event rank | additive-one failures |
|---:|---:|---:|---:|---:|
| `100,000` | `5,108` | `6,783` | `11` | `0` |
| `1,000,000` | `45,583` | `67,537` | `14` | `0` |

At `10^6`, the maximum prefix excess is `0` for ranks `0,1`, is `1` for
rank `2` first at `(362,2)`, and is `0` for every `d>=3`.  Hence the finite
gate finds no failure of `(Base)` or `(RD)`.  These values agree with the
C31 census and strict event at `(362,2)`.

The independent verifier uses trial divisors and literal approximants

\[
 S_0=\mathcal A,\qquad
 S_{k+1}=\{2,3\}\cup\{ab-1:a<b,\ a,b\in S_k\}.
\]

Through `1000` it stabilizes after seven updates, with zero membership and
rank mismatches.  It independently asserts the `74`, `114`, `174`, `492`,
and `774` records in the table.

Reproduction:

```powershell
python problems/424/compute/wave4/C44_minimal_counterexample/check_descent.py `
  --limit 1000000 `
  --output problems/424/compute/wave4/C44_minimal_counterexample/result_1e6.json

python problems/424/compute/wave4/C44_minimal_counterexample/verify_small.py `
  --limit 1000 `
  --output problems/424/compute/wave4/C44_minimal_counterexample/verify_1000.json
```

SHA-256:

```text
check_descent.py   114AB73CDA4F958334B19549CEEBC29863C07EE7EC70BA9766CEBC5295FE4F4B
verify_small.py    FAA89B2DB54374CD3E5724DA5782268AE80DFF32FB1686066F89B446316D799A
C44Arithmetic.lean DC21AF1DCF592ACCA356EBD4CFF6FF3CED8BD7DDBF497FA5E77BCFD2633D4547
result_100k.json   8FAE9412213001C6F1AC0618EC4A907EC0FDB9596A35EF2D37A8D7B51B0FB01C
result_1e6.json    1959B80148A93F6F07E5FC0279A8E88EBFB4CD1E06ECE8906F52222E09280B81
verify_1000.json   4AC4DBA1A981DCCA71219DF4CFADD2C73E31DA48E535134931BECDDC070BFF91
```

## 7. Lean verification

`C44Arithmetic.lean` proves the arithmetic cores of:

* `firstViolationJump`;
* `criticalPullbackDropsTwoRanks`;
* `nonSeedOddCofactorAtLeastFive`;
* `seedThreeChildBelowHardSource`;
* `hardEventResidue` and `targetEventResidue`.

It compiles with Mathlib using:

```powershell
lake env lean ..\..\problems\424\compute\wave4\C44_minimal_counterexample\C44Arithmetic.lean
```

The Lean file verifies only these arithmetic implications.  It does not
formalize or assume `(Base)`, `(RD)`, or (AO).

## 8. Prior-art and final status

The official Problem 424 page still lists the problem as open and points to
the original Erdos references, Guy's discussion, and OEIS A005244.  Searches
of those entries and the exact rank/event terminology found no prior
minimal-counterexample rank descent.  This is a limited novelty check, not
a claim about all unpublished work.

The rigorous output of this lane is therefore:

1. the exact first-violation normal form;
2. the two-rank critical pullback and smaller seed-child lemmas;
3. the sufficient aggregate rank descent `(RD)`;
4. exact least-grounded counterexamples to every tested local bridge from
   the pullback lemmas to `(RD)`.

The theorem remains open.  Any completion of this route must prove a global
rank-compatible transport statement such as `(RD)` without assigning
bounded capacity to critical factors, structural roots, adjacent events, or
bounded-rank seed descendants.
