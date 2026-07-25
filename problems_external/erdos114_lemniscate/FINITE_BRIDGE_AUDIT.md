# Finite-bridge audit — 2026-07-23

## Verdict

The advertised small-degree computation does **not** provide the finite bridge
required by the direct route. The route is therefore stopped.

## Reproducible evidence

Repository audited:

`https://github.com/MendozaLab/erdos-experiments`

Local snapshot:

`mendoza_erdos_experiments/README.md`

The current root README states that the reported margins come from three tested
families:

1. the Eremenko--Hayman family;
2. \(z^n+c\) on a grid; and
3. random monic samples.

It then states verbatim:

> These are not certified global gaps over all monic polynomials.

Consequently, exhaustive interval arithmetic inside those families cannot
prove the universal quantifier over all monic degree-\(n\) polynomials in
Erdős Problem 114.

The same repository also records a historical no-op branch-and-bound failure
for exploratory degrees 13--16 under
`scripts/erdos-114/archive/exploratory_2026-03-27/README.md`. Although that bug
was later patched and is not by itself an objection to later runs, it further
confirms that a `PROVEN` label must not be treated as the missing global
certificate without auditing the covered parameter domain.

## Missing logical bridge

No proved compact parameter reduction from the space of every normalized monic
degree-\(n\) polynomial to the three tested families is supplied. Therefore the
reported computations cannot cover even one full degree \(n\ge3\), regardless
of interval-rounding correctness within the implemented domains.

This triggers the registry exit condition: the claimed \(n\le14\) finite
certificates do not replay as certificates for the stated all-polynomial
problem.
