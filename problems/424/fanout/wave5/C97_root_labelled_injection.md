# C97: first obstruction to a healed derivation-leaf injection

## Verdict

The exact recurrence

\[
 A_H(X)\le D(X)+A_H(\lfloor X/4\rfloor)+1                 \tag{R}
\]

remains alive.  C97 neither proves nor falsifies `(R)`.

There is an exact root-labelled formulation of the frontier.  If
`\mathcal H_X` is the set counted by `A_H(X)` and `\mathcal D_X` is the
healed splitless set counted by `D(X)`, then `(R)` is equivalent to the
existence of an injection of finite labelled sets

\[
 \mathcal H_X\longrightarrow
 \mathcal D_X\sqcup\mathcal H_{\lfloor X/4\rfloor}\sqcup\{\star\}. \tag{1}
\]

The natural normalization sends every root that is still persistent at `X`
and is at most `floor(X/4)` to its identical label in the quarter-scale set.
It remains to map the young persistent roots

\[
 \mathcal Y_X=\{h\in\mathcal H_X:h>\lfloor X/4\rfloor\}  \tag{2}
\]

into `\mathcal D_X` with one exception.

C97 tests an unfiltered direct-ancestry version of this normalized map:
a hard root may use every structural splitless leaf in its complete exact
missing-factor derivation, but only after that leaf has healed.  This map is
false.  Its first exact Hall obstruction is

\[
                         \boxed{X=114}.                  \tag{3}
\]

At this cutoff the source labels are `{54,74,114}` and the complete healed
leaf neighborhoods are `{6}`, `empty`, and `empty`.  The matching number is
`1`; the singleton raises total capacity only to `2<3`.  Arbitrary bounded,
or even unbounded, multiplicity on eligible leaf targets does not help,
because two sources have degree zero.

The scalar recurrence itself has slack at this cutoff:

```text
A_H(114)=3,  D(114)=3,  A_H(28)=0.
```

The two additional bank roots are `18` and `20`.  Neither lies in any of the
three source derivation supports.  Thus a successful proof of `(R)` must be
nonlocal already at the third hard-root birth; following every exact missing
factor to every structural leaf is still insufficient.

## 1. Exact labelled reduction

Put `U(n)=2n-1`.  A hard root belongs to `\mathcal H_X` when every literal
iterate `U^j(h)<=X` is a hole.  A structural splitless root belongs to
`\mathcal D_X` when some such iterate at most `X` is generated.

### Lemma C97.1 (finite injection formulation)

For every integer `X`, `(R)` holds if and only if an injection (1) exists.
Moreover,

\[
 \mathcal H_X\cap[2,\lfloor X/4\rfloor]
 \subseteq \mathcal H_{\lfloor X/4\rfloor}.             \tag{4}
\]

Hence an injection
\(\mathcal Y_X\to\mathcal D_X\sqcup\{\star\}\) is sufficient for `(R)`.

### Proof

The equivalence is the elementary cardinality criterion for injections
between finite sets.  For (4), persistence through `X` implies persistence
through every smaller cutoff.  Sending each root in the left side of (4) to
its identical quarter-scale label is injective.  Any injection of the
remaining labels in (2) into the disjoint healed bank and singleton then
extends it to (1).  QED.

The normalized young-root condition is sufficient, not logically necessary:
an unrestricted injection in (1) may rematch quarter-scale labels.  At the
obstruction cutoff `X=114`, however, `\mathcal H_28` is empty, so this
distinction disappears.

## 2. Complete missing-factor leaves

For an allowed value `n`, let

\[
 \mathcal P(n)=\{(a,b):2\le a<b,\ ab=n+1,\ a,b\text{ allowed}\}.
\]

Let `G` be the actual least generated closure.  Define the unfiltered
complete leaf support `widehat L(n)` of a hole recursively by

\[
 \widehat L(n)=
 \begin{cases}
 \{n\},&\mathcal P(n)=\varnothing,\\
 \displaystyle\bigcup_{(a,b)\in\mathcal P(n)}
 \ \bigcup_{z\in\{a,b\}\setminus G}\widehat L(z),&\text{otherwise}.
 \end{cases}                                             \tag{5}
\]

Every factor in `P(n)` is smaller than `n`.  Every pair of a hole has at
least one hole factor.  Thus (5) terminates, is nonempty, and contains every
structural splitless obstruction reached through every missing factor, not
merely through a selected factorization.

### Lemma C97.2 (leaf landing)

Every `e in widehat L(n)` is a structural splitless root.  If its first generated
literal chain member is at most `X`, then \(e\in\mathcal D_X\).

### Proof

Induction down the strictly decreasing factor recursion proves that every
terminal value in (5) has no admissible pair.  Such a nonseed allowed value
is a structural splitless hole.  The second assertion is exactly the healed
bank definition.  QED.

This gives the explicit leaf-local relation

\[
 h\sim_X e\quad\Longleftrightarrow\quad
 e\in\widehat L(h)\text{ and }e\in\mathcal D_X.       \tag{6}
\]

## 3. First exact Hall obstruction

### Proposition C97.3

The normalized relation (6), augmented by one singleton target, first fails
at `X=114`.  At that cutoff its maximum matching has size `1`, and its total
capacity after the singleton is `2` for `3` sources.

### Exact certificate

The young persistent source set is

```text
Y_114 = {54,74,114},       H_28 = empty.
```

Their complete admissible pairs and supports are

```text
P(54)  = {(5,11)},   widehat L(54)  = {6};
P(74)  = {(5,15)},   widehat L(74)  = {8};
P(114) = {(5,23)},   widehat L(114) = {8,12}.
```

Indeed, `5` is generated, while

```text
P(11) = {(2,6)},
P(15) = {(2,8)},
P(23) = {(2,12),(3,8)}.
```

The roots `6`, `8`, and `12` are splitless.  Their exact first generated
chain members are

```text
6  -> 11 -> 21 -> 41,                                  41+1=3*14;
8  -> 15 -> 29 -> 57 -> 113 -> 225 -> 449,             449+1=9*50;
12 -> 23 -> 45 -> 89 -> 177 -> 353 -> 705 -> 1409
   -> 2817 -> 5633,                                    5633+1=9*626.
```

Consequently, only `6` has healed by `114`, and (6) gives

```text
N(54)={6},  N(74)=empty,  N(114)=empty.
```

The maximum matching is `54 -> 6`.  A singleton can cover either `74` or
`114`, but not both.  Since the latter two sources have no edge, changing
the capacity of `6` cannot remove the obstruction.

The exact all-integer scan checks every cutoff `2<=X<114` and finds no prior
failure, so (3) is the first cutoff for this relation.

## 4. The required nonlocal targets

The complete healed bank at `X=114` is

```text
D_114 = {6,18,20}.
```

Its first-generation certificates are

```text
6  -> 11 -> 21 -> 41,   41+1=3*14;
18 -> 35 -> 69,         69+1=5*14;
20 -> 39 -> 77,         77+1=3*26.
```

Both factors in each displayed product are generated.  The roots `18` and
`20` are splitless because their successors `19` and `21` have no admissible
distinct pair.  But

\[
 \{18,20\}\cap\bigl(\widehat L(54)\cup\widehat L(74)
 \cup\widehat L(114)\bigr)
 =\varnothing.                                           \tag{7}
\]

Thus the scalar bank has enough labels, while exact blocker ancestry does
not expose them.  Equation (7), rather than a counting deficit in `(R)`, is
the structural obstruction.  For this one cutoff, the explicit nonlocal map

```text
54 -> 6,   74 -> 18,   114 -> 20
```

does inject the source set into `D_114`; the last two arrows are precisely
the information absent from the derivation supports.

## 5. Verification

`C97_leaf_injection.py` independently constructs the least closure through
`10000`, computes all complete supports by recursion, and runs exact
bipartite matching at every integer cutoff until the first failure.

`C97_leaf_injection_verify.py` imports neither C97 nor C95/C96.  It uses
trial divisors and a memoized recursive definition of generated membership.
It verifies the factor sets, support sets, three leaf heal times, the bank
set `{6,18,20}`, and all `113` cutoffs from `2` through `114`.  Normal and
`python -O` outputs are byte-identical.

Reproduction from the repository root:

```powershell
python problems/424/compute/wave5/C97_leaf_injection.py `
  --limit 10000 `
  --output problems/424/compute/wave5/C97_leaf_injection_10000.json

python problems/424/compute/wave5/C97_leaf_injection_verify.py `
  --claim problems/424/compute/wave5/C97_leaf_injection_10000.json `
  --output problems/424/compute/wave5/C97_leaf_injection_verify_10000.json
```

SHA-256:

```text
10F24BA17118E8879423776F8B50C7DCB0119163CA1AE2734B1E60A8B61344A7  C97_leaf_injection.py
9BF7883232CF3524E1A7A0984621ECCB8745717563F7CF9E008E39C5147C04AA  C97_leaf_injection_verify.py
4724AF329D094AE0A325278C34E285D6E1CAA88E77F8863831700897C7245151  C97_leaf_injection_10000.json
28457708716999486031C63D71A96D6C4115AF42A7154C60EB2592CBD3D5C4D9  C97_leaf_injection_verify_10000.json
```

## 6. Relation to earlier lanes

C38 already defines a rank-filtered all-lower shadow `L(n)`, proves that it
terminates in structural splitless leaves, and tests a different bank network
for `H<=Q+C E`.  C74 records the rank-filtered support
`L(114)={8,12}`.  C97 does not claim those leaf sets or the grounded descent
principle as new.  Its `widehat L` removes the rank filter and follows every
missing endpoint, so it contains the C38 shadow.  The new obstruction applies
the actual healed-root bank `D(X)` from C91--C96 to this broader ancestry
relation and locates its first normalized Hall failure at `X=114`.  C38's
unit-capacity DAG and deterministic forests use different targets and first
fail at `1536` and `144`, respectively.

C95 studies the signed birth/death/heal event process.  C97 does not pair
events, amortize prefixes, or repeat the `10^9` scalar census.  Its graph is
static at each cutoff and uses exact root labels from grounded missing-factor
derivations.

C96 proves theorem-strength analytic and arithmetic-class obstructions and
shows that the prime-square shadow may heal too late.  C97 does not count
ambient arithmetic classes and does not reuse that shadow.  It gives the
first Hall obstruction even after admitting every exact splitless leaf in
every missing-factor branch.

The official Problem 424 page, checked 2026-07-13, still lists the problem
as open with no claimed partial solution or comments.  A repository search
found no earlier statement of the healed-`D(X)` obstruction in Proposition
C97.3.  Lemma C97.2 is the unfiltered analogue of C38's grounded-shadow
lemma, included to make the tested relation precise.  These are internal
reduction and obstruction results; no density theorem is claimed.
