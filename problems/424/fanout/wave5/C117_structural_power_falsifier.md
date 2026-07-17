# C117: structural-power falsifier

## DIRECT ROUTE

1. **Exact final deliverable.** Give an independently replayed hard even hole
   violating `s(h) >= d(h)^(3/4)-8`; otherwise give a reproducible extremal
   table from a prespecified sparse-template search and one exact structural
   pattern that a proof of the C112 power target must explain.  Finite
   non-falsification is not a theorem.
2. **Current frontier finite certificate.** Classify hard-shaped products
   `N=h+1` with large exact admissible-pair count `d(h)` and minimize
   `log(max(1,s(h)+8))/log(d(h))`, with special attention to growing `d` and
   bounded or slowly growing `s`.
3. **Logical bridge.** The exact integer inequality
   `(s(h)+8)^4 < d(h)^3` is equivalent to a counterexample to C112's
   `3/4` target.  A proved unbounded family with exponent below
   `1/(2 log 2)` would refute every C112 power criterion with that larger
   exponent; a finite low-ratio table only identifies the obstruction a proof
   must control.  C112.2 supplies the bridge from any surviving uniform power
   bound to `H(X)=o(X)`.
4. **Next falsifiable action.** Run a deterministic exact recursive-closure
   search over multi-prime lifts, squarefree `N=R` and `N=3R` templates, and
   templates with nontrivial prime powers.  Enumerate every source divisor
   from its prime-power factorization, then independently replay every
   retained extremal's hardness, `d`, `s`, endpoints, and seed-root taxonomy.
5. **Exit condition.** Stop on an independently replayed `3/4` falsifier, or
   after the declared template budgets are exhausted and the retained
   extremals pass independent replay.  Abandon any template immediately if it
   ceases to have an explicit source factorization or exact recursive closure
   classification.

## Status

Finite adversarial search complete; C112's power target remains open.

## Verdict

No counterexample to

\[
                         s(h)\ge d(h)^{3/4}-8
\]

was found.  This is a finite adversarial result, not a theorem claim and not
evidence promoted to the existence of any asymptotic power bound.

The six declared exact searches made `192,500` candidate evaluations.  Runs
used different template lanes, so this total is not asserted to be globally
deduplicated.  Exact factor enumeration put `186,819` candidates at or above
the corresponding run's `d` threshold.  Their closure states were

```text
generated: 186,811
hard:            8
other:           0
splitless:       0
```

There were zero `3/4` falsifiers.  The maximum tested pair count was `128`,
and the largest tested source was

```text
132131012341607575950114
```

Every retained hard source and its complete endpoint/root taxonomy passed a
separately written recursive replay.

## 1. Exact acceptance

Every candidate starts from an explicit prime-power factorization of
`N=h+1`.  Source divisors and all admissible distinct pairs are enumerated
from that factorization.  Endpoint closure states are then evaluated by the
exact least recursive closure classifier: factor `n+1`, enumerate every
admissible pair, and recurse only to smaller endpoints.  No contiguous state
array or probabilistic classification is used.

Only the two hard arithmetic shapes are admitted:

```text
N = 1 (mod 3), with 3 not dividing N;
N = 3R, with R = 1 (mod 3) and 3 not dividing R.
```

For `B=8`, the reported exponent proxy is

\[
                  \rho_8(h)={\log(s(h)+8)\over\log d(h)}.
\]

Floating point is used only to display this ratio.  A `3/4` falsifier is
accepted exactly if

\[
                         (s(h)+8)^4<d(h)^3.             \tag{1}
\]

Thus no floating-point quantity can create or suppress a counterexample.

## 2. Search lanes

All generated sources satisfy `h>4*10^9`.

| artifact | candidate evaluations | closure-classified | tested `d` | hard | largest source |
|---|---:|---:|---:|---:|---:|
| `C117_base_powers_5k.json` | 5,000 | 5,000 | 24--40 | 0 | 37,574,230,562,709,158,065,448 |
| `C117_focused.json` | 1,500 | 1,500 | 8--72 | 0 | 8,642,908,561,266,374,604 |
| `C117_diverse_26k.json` | 26,000 | 20,319 | 1--128 | 0 | 4,721,584,507,441,840,041,852 |
| `C117_slot_sweep_100k.json` | 100,000 | 100,000 | 8--18 | 8 | 1,782,870,115,185,196,331,634 |
| `C117_cross_seed_fiber_30k.json` | 30,000 | 30,000 | 24--72 | 0 | 63,046,033,713,844,708,450,824 |
| `C117_second_generation_fiber_30k.json` | 30,000 | 30,000 | 24--72 | 0 | 132,131,012,341,607,575,950,114 |

The `5,681` diverse prime-power candidates below that run's `d>=12` filter
still had their source pairs enumerated, but were not recursively classified.
The other `186,819` rows were classified exactly.

The templates are:

1. powers `N0*p^e`, `e=2,3,4`, over C112's `d=8,s=0` core;
2. same-residue substitutions and divisor-raising mutations of five unrelated
   hard shapes with `d=8,12,16,18`;
3. unanchored squarefree `R` and `3R` products with two, four, or six minus
   primes and varying plus-prime support;
4. unanchored mixed prime-power exponent vectors in both hard shapes;
5. composite-`q` replacements of the recurrent affine factor;
6. multi-plus lifts, plus-prime squares/cubes, plus-prime pairs, and neutral
   pairs of minus primes; and
7. the same four divisor-raising fibers seeded by the newly found sparse hard
   survivors, not just by the original C105 examples.

## 3. Sparse extremal table

The only hard survivors occurred in fixed-`d` same-residue slot sweeps.

| `d` | hard survivors | min `s` | max `d-s` | min `rho_8` | representative `h` |
|---:|---:|---:|---:|---:|---:|
| 8 | 5 | 0 | 8 | 1.000000000000 | 4,751,710,742 |
| 16 | 3 | 9 | 7 | 1.021865710313 | 158,020,616,214 |

For the two representatives, the exact sides of (1) are respectively

```text
(d,s)=(8,0):   (s+8)^4=4096,  d^3=512
(d,s)=(16,9):  (s+8)^4=83521, d^3=4096
```

so neither is close to the strict falsifier direction.  The minimum observed
`rho_8` is `1`, while

```text
1/(2 log 2) = 0.7213475204444817.
```

This finite ratio comparison says nothing about an unknown constant `A`, an
unknown additive constant `B`, or behavior as `d` tends to infinity.  In
particular, it does not prove C112's `3/4` target or any weaker power law.

## 4. Structural pattern to explain

Across the declared lanes, exactly `86,319` divisor-raising candidates were
recursively classified.  Every one was generated.  Hardness survived only
when a prime label was replaced without increasing the divisor shape.

The extremal `d=16` survivor has

```text
h = 158020616214
N = 5 * 7^3 * 11 * 269 * 31139
s = 9
```

All sixteen admissible pairs have exactly one generated endpoint and one
missing endpoint.  The sixteen missing endpoints have seed-root taxonomy

```text
structural splitless: 9
hard:                 4
other hole:           3
```

Thus its seven nonstructural pairs are precisely the four hard-root and three
other-root blockers.  A proof must explain the observed dichotomy: a
divisor-raising operation creates a generated-generated complementary pair,
or a surviving hard source has only a bounded collection of nonstructural
blocker roots.  This is the requested structural pattern, not a claimed
lemma.

## 5. Independent replay

`C117_structural_power_verify.py` does not import the search program.  It
refactors each retained `N` with `sympy.factorint`, enumerates source and
recursive divisors with `sympy.divisors`, computes seed roots by iterating
`p -> (p+1)/2`, and checks hardness, `d`, `s`, every endpoint, every root,
the complete taxonomy, and (1).

All eight records pass.  Normal and `python -O` outputs are byte-identical:

```text
0DB3E13323CF8E25C1DE8EF1BD88DB4BEDD08B83B4D035D08FB2A832B6049CC1
  C117_slot_sweep_100k_verify.json
```

The aggregate manifest records every run parameter, family count, streaming
digest, artifact hash, implementation hash, and extremal row.  Its normal and
optimized outputs are also byte-identical:

```text
4FB5E1CF259CDECA5A3ED15047789F7E5474BA95FAA131411226B771635A1FCE
  C117_manifest.json
```

## 6. Reproduction

The exact arguments for all six runs are embedded in `C117_manifest.json`.
The final hard table and its independent replay are reproduced by:

```powershell
python problems/424/compute/wave5/C117_structural_power_falsifier.py `
  --prime-limit 1000000 --max-bits 80 --min-d 8 `
  --base-power-budget 0 --base-multi-budget 0 --squarefree-budget 0 `
  --prime-power-budget 0 --composite-q-budget 0 --slot-sweep-budget 100000 `
  --fiber-sweep-budget 0 --shape-substitution-budget 0 `
  --shape-expansion-budget 0 --extremal-lift-budget 0 --mutation-budget 0 `
  --extremal-limit 64 --progress-every 5000 `
  --output problems/424/compute/wave5/C117_slot_sweep_100k.json

python problems/424/compute/wave5/C117_structural_power_verify.py `
  --claim problems/424/compute/wave5/C117_slot_sweep_100k.json `
  --output problems/424/compute/wave5/C117_slot_sweep_100k_verify.json

python problems/424/compute/wave5/C117_build_manifest.py `
  --output problems/424/compute/wave5/C117_manifest.json
```
