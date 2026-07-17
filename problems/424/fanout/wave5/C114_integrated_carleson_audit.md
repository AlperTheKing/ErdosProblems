# C114 integrated-Carleson audit

## Verdict

Accepted with the selected-square condition left open.  The exact layer-cake
identity and the implication from `B_m=o(m^3)` to C99 are correct.  Neither
the uniform integrated Carleson estimate nor the selected-square estimate is
proved.

## Logical audit

For each root, its contribution to `T_D` persists exactly for
`D<=min(q_X(r),j(r)^2)`.  Summing these indicator layers gives C114.1.
Monotonicity over the `2m+1` integers in `(m^2,(m+1)^2]` yields

```text
(2m+1) T_((m+1)^2) <= B_m.
```

Below bin `m+1`, at most `2^(j-1)` odd denominators occur in bin `j`, so
their dyadic reciprocal majorant is at most `1/2` per bin.  With
`D=(m+1)^2`, this proves

```text
Sigma_D/D <= 1/(2(m+1)) + B_m/((2m+1)(m+1)^2).
```

Taking `m=floor((log X)^(c/2))`, `2/3<c<log 2`, makes
`B_m=o(m^3)` sufficient for the residual term, while C99 controls the
low-pair and structural-bank terms.  The exponent comparisons are strict.
The condition is weaker than the full integrated Carleson estimate because
the latter gives `B_m=O(log X)=o(m^3)`.

## Independent replay

Normal and optimized integrated probes reproduce SHA-256
`EB4B0608...A9EC`; normal and optimized layer-cake checks reproduce
`51E9F90B...9A1A`.  The C++ source-incidence scanner was independently
rebuilt and rerun through `10^9`; its JSON is byte-identical with SHA-256
`D468AECD...F030`, reproducing `29,010,146` hard sources and maximum `d=16`.

The exact hard-source witness `h=77,317,236`, `d=4`, `A=2`, `M=1` kills
the proposed source-local inequality `AM>=d-1`.  The remaining eventwise
inequality has no summable cross-source budget and is not promoted.

