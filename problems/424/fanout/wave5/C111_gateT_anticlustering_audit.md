# C111 anticlustering audit

## Verdict

Accepted with a strict scope boundary.  The nonasymptotic divisor-moment
inequality and its optimized growing-cutoff corollary are correct.  They do
not imply the fixed-cutoff Gate T.

## Proof audit

For each labelled edge `uv=z` in a fibre with `r_K(z)>T`, the R9 injection
and divisor submultiplicativity give

```text
1 <= tau(u)^q tau(v)^q / T^q.
```

Summing over labelled edges separates channelwise into the product of two
divisor moments.  The exact bounds

```text
U_i <= 36*360^i,  V_{K-i} <= 27*360^(K-i)
```

and `tau(n)^q <= d_(2^q)(n)` give

```text
T^q M_K(T) <= 972 |I_K| 360^K J_K^(2(2^q-1)).
```

R9's injective 60-block code and majority selection give
`N_K >= |I_K|60^K/4`, yielding the normalized constant `3888*6^K`.

For `q=floor(log_2(K/(log K)^3))` and
`log T >= ((log 2)(log 6)+epsilon)K/log K`, the term `q log T`
cancels `K log 6` and leaves `epsilon K/log 2`; the divisor-moment term is
at most `2K log(16K)/(log K)^3=o(K)`.  Hence the stated exponential tail
follows for sufficiently large `K`.

This calculation leaves all fibres with multiplicity between a fixed `L`
and `exp(O(K/log K))`; no fixed positive mass of bounded fibres follows.

## Independent replay

The Python verifier was run normally and with `python -O`; both audit outputs
are byte-identical to the submitted output with SHA-256

```text
867B732D9460EB3A821860FE589FAF8E17D297BA6326ADAF5F2698E43C41FE7F
```

The C++ extractor was independently rebuilt and rerun with 32 threads.  Its
audit output is byte-identical to the submitted census with SHA-256

```text
D3A443E80138C95DCB6618762307A4E5CD4B7875D945C8476AE0C89BDDAED0DC
```

It reproduces `60,512,841` edges, `15,931` repeated fibres, and repeated
edge mass `31,866`.  The six-letter suffix counterexample is therefore also
accepted; bounded-suffix uniqueness is dead.

