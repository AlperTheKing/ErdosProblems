# Codex audit of Round 9 Theorem E

Date: 2026-07-26
Scope: `R9_thmD_thmE.py` and the dependent `R9_thmD_coverage.py` claims.

## Verdict

Theorem E is not proved as written. Its second inequality uses an invalid
distribution of a minimum over a sum. This does not refute Erdős #23.

## Failing step

E2 defines `a_i = yhat_i yhat_{i+1}` and `b_i = BAD_i`, then claims

```
psi(H,x) <= min_i(a_i + b_i) <= 1/25 + min_i b_i.
```

The first inequality may follow from the five constructed cuts. The second
does not follow from `min_i a_i <= 1/25`, because the two minima may occur at
different indices.

A realizable failure of the claimed implication occurs on `And(3)`. Take
`C=(0,1,2,3,4)`, assignment `5->0, 6->1, 7->4`, denominator `q=10`, and
weights `a=(0,0,0,0,0,2,3,5)`. Then

```
yhat = (2,3,0,0,5),
BAD weights = (0,15,15,15,0),
E2 cut bounds = (6,15,15,15,10),
min bound = 6 > q^2/25 = 4, while min BAD = 0.
```

The actual support is the path `5-6-7`, so `psi=0`; the target conclusion is
true here, but E2 does not prove E3.

## Consequences

- E3 is unsupported when only one `BAD_i` vanishes.
- `R9_thmD_coverage.py` accepts exactly that insufficient condition.
- Its `E-COVERED` counts and stated Andrasfai closures are not certificates.
- The Andrasfai witness has BAD counts `[0,C(k-2,2),C(k-2,2),C(k-2,2),0]`, not all zero.
- No conclusion about the actual value of `psi` follows from this audit.

## Sound repairs

- If all five `BAD_i` vanish, then E2 gives `psi <= min_i a_i <= 1/25`.
- If a zero-`BAD` index also satisfies `a_i <= 1/25`, that one cut suffices.
