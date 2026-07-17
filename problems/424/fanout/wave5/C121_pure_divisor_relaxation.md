# C121: pure-divisor relaxation is false

For an arithmetic hard-shape product `n=h+1`, ignore membership in the least
closure and allow an adversary to choose either endpoint of every admissible
factor pair as its blocker.  A pair is then forced to use a structural blocker
only when both endpoint seed-2 roots are structural splitless.

The relaxation

```text
2 * forced_both_structural >= d(h) - 8
```

is false.  The first exact failure below `10^6` is

```text
h = 237404,  d(h) = 12,  forced_both_structural = 1.
```

This is not an actual hard hole: it has the generated factor pair
`237405 = 17 * 13965`.  One complete generation certificate is

```text
237404 <- (17,13965)
17 <- (2,9), 9 <- (2,5), 5 <- (2,3)
13965 <- (2,6983), 6983 <- (3,2328), 2328 <- (17,137)
137 <- (2,69), 69 <- (5,14), 14 <- (3,5)
```

Thus any proof of the C116 structural bound must use the absence of a
generated complementary pair, hence the actual two-seed closure history.
Pure divisor arithmetic and the seed-3 shape restriction do not suffice.

The exact SPF scan tested 113,571 arithmetic hard-shape products through
`h=10^6`; normal and optimized outputs are byte-identical with SHA-256

```text
BA233A0AD72353589AAF96E7AE75BA3F57A0B2FE564883D7BDE69F50132C26F4
```

Artifacts:

```text
compute/wave5/C121_pure_divisor_relaxation.py
compute/wave5/C121_pure_divisor_1m.json
compute/wave5/C121_pure_divisor_1m_O.json
```
