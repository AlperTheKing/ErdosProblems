# C112 structural-deficit audit

## Verdict

Accepted with the antecedent explicitly open.  The structural-incidence
theorem and the exponent criterion are correct; neither
`s(h)>=d(h)-8` nor `s(h)>=d(h)^(3/4)-8` is proved.

## Logical audit

Different admissible factor pairs of one hard source have disjoint odd
endpoints.  Choosing one structural missing endpoint from each of `s(h)`
pairs therefore gives distinct incidences for that source.  A fixed endpoint
`p=2^j(r-1)+1` divides `h+1` for at most `floor((X+1)/p)` sources.  Summing
over `j>=1` gives at most `(X+1)/(r-1)` incidences per structural root, hence

```text
H_high(X) <= (X+1) W_E(X)/L
```

whenever every counted source has at least `L` structural pairs.

With `K=floor((log X)^c)`, C99 gives `B_K(X)=o(X)` for `c<log 2` and
`W_E(X)=O((log X)^(1/2))`.  The hypothesis
`s(h)>=A d(h)^alpha-B` makes `L` asymptotic to
`A(log X)^(c alpha)`.  A valid `c` exists precisely when
`1/(2 alpha)<log 2`, i.e. `alpha>1/(2 log 2)`.  Thus `alpha=3/4`
is sufficient and is strictly weaker than a linear deficit-eight bound.

## Exact replay

The independent verifier was rerun normally and with `python -O`; both audit
outputs are byte-identical with SHA-256

```text
7A864A144F6BDF7AF2A9BF07383360C99202809F1007CD9C74BA0A9BA2BBE1F1
```

All pinned hashes pass after resolving the report's separate `fanout` path.
The replay confirms `39,229` prime lifts through `999,979`, largest source
`2,067,095,547,081,902`, and no hard lift.  The separately written C115
classifier independently found the same zero-hard-lift count through the
same prime limit.  This finite exclusion is not promoted to the universal
power bound.

