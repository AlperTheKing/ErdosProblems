# P116: exact adversarial search for BC108

## Verdict

No BC108 falsifier was found in the exact domains below.

This is a finite-search report, not a proof of BC108.  Every acceptance and
score computation used Python integers.  Floating point was not used to
accept a row.  The search target was exactly

\[
  \delta>0,\qquad \Delta_+(B)\cap(B+B+b)=\varnothing,
  \qquad \sum_u(t_u-n_u)_+>p,
\]

with `b` in `{1,2}`.  Here `n_u` counts folds with lower high endpoint `u`
and `t_u` counts loose fold triangles of color `u`.

## Independent reconstruction

`bc108_core.py` reconstructs sums, differences, folds, loose triangles,
colors, and the BC108 residual without importing a P108 scorer.  It agrees
exactly with P108 on all seven mandatory rows:

```text
P75, P94, P98, P105, P88_b1, P88_b2, P88_q2_literal_hole.
```

The separate `verify_bc108_artifacts.py` implementation independently
recomputes retained boundary rows from raw marks.

## Complete new-width domain

`exhaustive_w31_50.json` exhausts every endpoint-normalized integer Sidon
ruler of widths `31,...,50`, including both orientations because every
oriented ruler occurs in the enumeration.  For each ruler it tests every
translation with positive direct defect and both phases.  It also tests the
lift

```text
B -> 2B+1,  h -> 2h,  b=1
```

whenever the lifted defect is positive.

```text
endpoint-normalized rulers                         1,890,468
direct positive-defect candidates                 69,296,680
direct literal-hole rows                          24,042,660
direct rows with loose triangles                     181,932
direct BC108 failures                                      0
q=2 parity-lift candidates                        34,648,340
positive-defect q=2 lifts                             83,016
positive-defect lifted rows with triangles            17,385
parity-lift BC108 failures                                 0
```

The aggregate decision-stream SHA-256 is

```text
f4a90b8060e3a90797bcbc5c7a0e5371a1610bd29bf451bb20bc855295d96b7b
```

## Archived and mutation domains

`archive_mutation_search.json` contains two deterministic domains.

### Archived bases

All `2,526` oriented Sidon bases extracted by the P86 archive loader were
tested at every positive-defect endpoint translation, for both phases, and
at every positive-defect q=2 parity lift.

```text
direct positive-defect candidates                  1,615,708
direct literal-hole rows                              320,040
direct triangle rows                                  239,027
direct BC108 failures                                       0
positive-defect parity lifts                              622
parity BC108 failures                                       0
```

Decision-stream SHA-256:

```text
cdfbc90412f6251f0c8355c953908907538e97a090c010befff771e62d84e3e8
```

### Named hard-seed mutations

The seed list consists of both orientations of the seven P108 mandatory
rows, P106, and all twenty P110 dimension-falsifier rows.  The exact
mutation generator produced:

```text
seed orientations                                         56
raw one-deletion orientations                         13,684
raw direct-insertion orientations                     20,868
raw endpoint one-swap orientations                    33,976
distinct mutated orientations                         31,958
```

Every positive-defect endpoint translation and both phases were then tested.

```text
direct positive-defect candidates                 71,341,316
direct literal-hole rows                          12,442,570
direct triangle rows                              12,422,762
direct BC108 failures                                      0
positive-defect parity lifts                               0
```

The largest residual in this domain was `-17`, at a P75 insertion/translation
with `(p,h,b,delta,C_S,T_F,excess)=(27,1046,1,35,44,35,10)`.

Decision-stream SHA-256:

```text
2f9d2c86eb32dbcd7de2683adc3d0f8fea0b07bd62c8a0e3364afc977481c140
```

## Targeted hard-row searches

### P88 literal-hole subsets

The exact Boolean model enumerated every subset of P88 that retains its
maximum mark, has positive defect, and satisfies the literal-hole clauses.
It separately treated `b=1` and `b=2`.

```text
phase     original conflicts   minimum deletions   live subsets   failures
b=1              200                   12              2,052          0
b=2              193                   12                355          0
```

Positive defect permits at most thirteen deletions.  Thus this is the full
positive-defect induced-subset domain under the fixed P88 endpoint.

### P106 near-falsifier repair

P106 itself has BC108 residual `+9`, but is not a literal hole.  For `b=1`
its 124 literal conflicts require at least seven deletions; there are exactly
ten minimum hitting sets.  Exhausting every Sidon- and hole-preserving
completion of those ten cores visits 217 nodes and reaches at most `p=63`.
Positive defect at the P106 endpoint requires `p=67`.

For `b=2`, 227 conflicts require thirteen deletions; the four minimum cores
have only six completion nodes and reach at most `p=55`.  Hence the nearest
minimum-cardinality hole repairs do not return to the positive-defect range.

The independent q=2 P88 insertion audit gives the same obstruction from the
other side: 41 single insertions preserve Sidon plus the literal hole, but
their pairwise-compatibility graph has clique number three, whereas seven
insertions are needed for positive defect.

## Exact induced-subset models

Four dense archived parents, indices `174, 2473, 2486, 2500` in the P86
deterministic ordering, were modeled with Boolean mark variables.  Fold and
triangle variables are exact conjunctions of their mark supports; all
literal-hole clauses and the positive-defect cardinality threshold are
included.  Both phases were tested.

The first 120-second single-worker pass returned three `INFEASIBLE` and five
`UNKNOWN` results.  The five unresolved jobs were rerun as pure feasibility
problems with eight workers.  All five returned `INFEASIBLE`:

```text
parent 174:  b=1 INFEASIBLE, b=2 INFEASIBLE
parent 2473: b=1 INFEASIBLE, b=2 INFEASIBLE
parent 2486: b=1 INFEASIBLE, b=2 INFEASIBLE
parent 2500: b=1 INFEASIBLE, b=2 INFEASIBLE
```

No `UNKNOWN` result is counted as evidence in this report.

## Independent difference-Hall audit

`search_bc108_falsifier.py` is a separately written scorer.  In addition to
BC108 it tests whether the color excess copies can be injected into the arm
difference labels.  Its exact live domains comprise:

```text
complete widths 31..40                         3,479,796 rows
archived translations                            312,887 rows
positive archive parity lifts                         372 rows
P88 one-deletion translations                    101,355 rows
```

It reports zero BC108 failures and zero difference-Hall failures.  Its
retained rows were checked by the independent Edmonds-Karp verifier in
`verify_bc108_search.py`.

## Artifact hashes

```text
aad17fb6006e51d44e8d739ec684f285af27dae14756f382d114f17925f8f6a5  exhaustive_w31_50.json
353671b5ef5ab1848281cf302e2a91c17a309d23b70e7c275dd1a6461d879866  archive_mutation_search.json
41c52b97d4e4a5d5532a126132eb4021400434816ee41d15c0015eb6782a3ad9  p88_hole_subsets.json
f44fb03fe868ed30eff9d76c0fde4ed6da8ff0f42a8e06f7a61a3163f5b3edca  p106_hole_repair.json
```

The per-parent CP and parallel-rerun hashes are recorded by
`external_verification.json`.  `independent_verification.json` records the
artifact hashes and the independently recomputed retained rows.

## Reproduction

```powershell
python problems/864/compute/p116/search_bc108.py `
  --min-width 31 --max-width 50 --workers 61 `
  --output problems/864/compute/p116/exhaustive_w31_50.json

python problems/864/compute/p116/search_archives_mutations.py `
  --workers 61 --max-swap-width 2000 `
  --output problems/864/compute/p116/archive_mutation_search.json

python problems/864/compute/p116/search_p88_hole_subsets.py `
  --output problems/864/compute/p116/p88_hole_subsets.json

python problems/864/compute/p116/search_p106_hole_repair.py `
  --output problems/864/compute/p116/p106_hole_repair.json
```

## Boundary of the result

The search provides no finite counterexample to BC108 in the declared
domains.  It does not prove BC108 for arbitrary positive-defect literal-hole
rows.  The surviving proof target remains

\[
  \sum_u(t_u-n_u)_+\le p.
\]

The separately surviving difference-label injection is a stronger possible
mechanism, but this report establishes it only on the listed finite domains.
