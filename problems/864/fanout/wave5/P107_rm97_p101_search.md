# P107: positive-defect literal-hole search for RM97 and P101

## Verdict

No counterexample was found.  This is a finite exact result, not a proof of
RM97 or P101.

P107 closes two complete subset lattices with CP-SAT and audits nine seeded
mutation lanes.  Every retained candidate was reconstructed independently
with integer arithmetic.  No computation used more than 16 workers.

## 1. Complete P88 subset lattice

Let `B_88` be the 60-mark P88 ruler in `[0,3285]`, put `h=3286`, and retain
the terminal mark `3285`.  P107 optimized over **every subset** `B` of
`B_88` satisfying

```text
|B| >= 47,
Delta_+(B) intersect (B+B+b) = empty,
b in {1,2}.
```

The cardinality threshold is exactly strict positive defect: at this fixed
`h`, `delta>0` iff `|B|>=47`.  Sidonicity is hereditary from `B_88`.

The exact P101 optima were

| offset | max `T_F-C_S` | CP-SAT status |
|---:|---:|---|
| 1 | -24 | OPTIMAL |
| 2 | -25 | OPTIMAL |

The separate joint RM97 optimization chose both the subset and a Hall window
`J`.  Its objective was

```text
#{demands I with I subseteq J} - #{residual endpoint slots in J}.
```

For both offsets the exact maximum was `0`, with status `OPTIMAL`.  Hence
there is no RM97 failure anywhere in this complete subset domain.

## 2. Complete positive-defect P94 subset lattice

Let `B_94` be P94's 104-mark literal-hole row, with `h=14484`, `b=1`, and
terminal mark `14483`.  P107 optimized over every endpoint-preserving subset
with strict positive defect.  Here this is exactly the family

```text
B subseteq B_94, 14483 in B, |B| >= 99,
```

so the model covers every deletion of at most five nonterminal marks.  Both
Sidonicity and the literal hole are hereditary.

The P101 optimum was `T_F-C_S=-15`, status `OPTIMAL`.  The RM97 Hall-window
optimum was `0`, status `OPTIMAL`.  Thus neither candidate fails in this
complete subset lattice.

## 3. Seeded mutation lanes

The exact mutation audit visited 3,384,139 coordinate-labelled candidates.
The count deliberately includes occupied/reinserted coordinates before the
Sidon filter; the `Sidon` column gives the actual Sidon candidates.

| lane | visited | Sidon | full gate | P101 fail | RM97 fail |
|---|---:|---:|---:|---:|---:|
| P105 source translations, `gamma=0..1559`, both offsets | 3,120 | 3,120 | 372 | 0 | 0 |
| P105 source one/two deletions, both offsets | 3,192 | 3,192 | 0 | 0 | 0 |
| P105 source direct insertions, both offsets | 6,570 | 6 | 0 | 0 | 0 |
| P105 source one-delete/one-insert, both offsets | 367,920 | 336 | 0 | 0 | 0 |
| P94 one/two deletions | 5,356 | 5,356 | 5,356 | 0 | 0 |
| P94 direct insertions | 14,483 | 47 | 0 | 0 | 0 |
| P94 one-delete/one-insert | 1,491,749 | 4,841 | 18 | 0 | 0 |
| P98 (`P94-{4740}`) direct insertions | 14,483 | 48 | 1 | 0 | 0 |
| P98 one-delete/one-insert | 1,477,266 | 4,896 | 122 | 0 | 0 |

Exactly 5,869 evaluations reached all four gates: Sidon, endpoint,
`delta>0`, and the literal hole.  The best P101 margins in the lanes were
`-19` for P105 translations, `-20` for P94 deletions, and `-22` for the P98
replacement lane.  Every full-gate row matched all RM97 demands.

## 4. Arithmetic and reproduction

`core.py` independently rebuilds all diagonal-inclusive sums, positive
differences, folds, loose triangles, collision folds, residual intervals,
and the exact earliest-deadline interval matching.  CP-SAT only selects a
finite subset and, for RM97, an integer Hall window.  All accepted gates and
objectives are replayed with Python integers.

Run:

```powershell
python -B problems/864/compute/p107/search_p88_subsets.py --workers 16 `
  --seconds 300 --b 1 2 `
  --output problems/864/compute/p107/p88_subset_search.json

python -B problems/864/compute/p107/search_p88_rm97.py --workers 16 `
  --seconds 600 --b 1 2 `
  --output problems/864/compute/p107/p88_rm97_search.json

python -B problems/864/compute/p107/search_p94_subsets.py --workers 16 `
  --seconds 600 `
  --output problems/864/compute/p107/p94_subset_search.json

python -B problems/864/compute/p107/search_mutations.py --workers 16 `
  --output problems/864/compute/p107/mutation_search.json

python -B problems/864/compute/p107/verify_result.py `
  problems/864/compute/p107/p88_subset_search.json
python -B problems/864/compute/p107/verify_result.py `
  problems/864/compute/p107/p88_rm97_search.json
python -B problems/864/compute/p107/verify_result.py `
  problems/864/compute/p107/p94_subset_search.json
python -B problems/864/compute/p107/verify_mutations.py `
  problems/864/compute/p107/mutation_search.json
```

Output SHA-256 digests:

```text
37F06955B7CDD3B7A63C0EA7E5941ED2DC9E3071F02E9A04D872F594F08499B7  p88_subset_search.json
F7D696599C5710EBA07895A125FE578F47FC6FA6F8124755067DD072C692715F  p88_rm97_search.json
4374570E4D87088C809D85A9C49E3C1FDB133BB89CF0A1A7E88214CCD92F8992  mutation_search.json
F6814FB5DADF33700DADA52BC59126C0E0A3C4CFAA48E55AA410A47EB81A8DE7  p94_subset_search.json
```
