# C28: exact interval-envelope count for Fable's C-M mass gate

## Result

For

\[
D_{a,b,c}=2D_{a-1,b,c}\cup(3D_{a,b-1,c}+1)
             \cup(5D_{a,b,c-1}+3),\qquad D_{0,0,0}=\{0\},
\]

the exact count at Fable's ray `(3,2,1)`, `k=5`, is

\[
\boxed{|D_{15,10,5}|=330\,159\,210\,305}.
\]

Here

\[
M=2^{15}3^{10}5^5=6\,046\,617\,600\,000,
\]

so

\[
\frac{|D|}{M}=0.05460229704372242756\ldots,\qquad
\frac{\sqrt{30}|D|}{M}=0.29906909782444419005\ldots.
\]

The integer was obtained twice over the full modulus, with different tile
boundaries, and once more over the exact reachable range. No floating-point
value enters membership or acceptance.

## Algorithm

Let `M_*` be the target modulus and let `M_s=2^a3^b5^c` for a state
`s=(a,b,c)`. Partition `[0,M_*)` into disjoint target tiles
`I=[L,H)`. For every state define

\[
P_s=M_*/M_s,\qquad
J_s(I)=\left[\left\lfloor L/P_s\right\rfloor,
             \left\lceil H/P_s\right\rceil\right)\cap[0,M_s).
\]

Only the packed membership bits for `D_s` on `J_s(I)` are computed.
States are evaluated by total degree, retaining two adjacent degree layers.
The three residue channels are

```text
d = 2x       (d = 0 mod 2)
d = 3x + 1   (d = 1 mod 3)
d = 5x + 3   (d = 3 mod 5)
```

The implementation expands 32, 21, or 12 child bits at once into these
residue positions with BMI2 `PDEP`, then ORs the channels. Tiles are
independent and are summed with OpenMP. There is no hashing, probabilistic
filter, external sort, or global support vector.

## Exactness proof

**Lemma 1 (offset range).** A suffix with multiplier `P` has the form
`x -> Px+q` with `0 <= q < P`.

This holds at the empty suffix and is preserved by each map `px+r`, since
`0 <= r < p`.

**Lemma 2 (closed tile envelopes).** If `d` is in `J_s(I)` and
`d=px+r`, where `0 <= r < p`, then `x` is in the envelope of the
corresponding child state.

Indeed, the child has scale ratio `pP_s`, and `x=floor(d/p)`. The
endpoint identities

\[
\left\lfloor\frac{\lfloor L/P_s\rfloor}{p}\right\rfloor
=\left\lfloor\frac{L}{pP_s}\right\rfloor
\]

and

\[
\left\lfloor\frac{\lceil H/P_s\rceil-1}{p}\right\rfloor
=\left\lfloor\frac{H-1}{pP_s}\right\rfloor
=\left\lceil\frac{H}{pP_s}\right\rceil-1
\]

give both bounds.

**Lemma 3 (local recurrence is exact).** The packed array computed for
state `s` equals the indicator of `D_s` on `J_s(I)`.

Induct on `a+b+c`. The base array contains exactly `0`. Lemma 2
guarantees that every inverse lookup required on `J_s(I)` is present in
the child array. The three residue tests and inverse quotients are exactly
the three terms of the defining union. OR therefore handles all collisions
exactly.

**Theorem.** The reported sum is `|D_{15,10,5}|`.

By Lemma 3, each terminal tile count is exact. The target tiles form a
disjoint partition of `[0,M_*)`, and every generated offset lies in that
interval by Lemma 1. Summing their popcounts neither omits nor duplicates an
offset.

`PDEP` is only a packed implementation of the injective index map
`x -> px+r`; it changes no logical operation.

## Complexity and resources

For tile width `B`,

\[
|J_s(I)|\le B/P_s+1.
\]

There are `(15+1)(10+1)(5+1)=1056` states, and

\[
\sum_s\frac1{P_s}
=\left(\sum_{i=0}^{15}2^{-i}\right)
 \left(\sum_{j=0}^{10}3^{-j}\right)
 \left(\sum_{\ell=0}^{5}5^{-\ell}\right)
<2\cdot\frac32\cdot\frac54=\frac{15}{4}.
\]

Thus a tile requests fewer than `3.75 B + 1056` logical state bits in
total. Only adjacent degree layers are resident. Across all tiles the work
is `O(M_*)`, while memory is `O(B)` and independent of `M_*`.

The `2^30`-bit run had a conservative bound of 272,909,440 bytes per
worker, or 17,466,204,160 bytes for 64 workers. A single packed target
vector would require 755,827,200,000 bytes; the NumPy byte-vector method
would require 6,046,617,600,000 bytes for the terminal state alone.

Exact monotone min/max recurrences give

```text
min D_15,10,5 =       92,264,843
max D_15,10,5 = 4,534,479,454,208
```

The first two verification runs intentionally scanned all `M_*`. The third
run processed only `2^30`-bit tile indices `[0,4224)`, skipping the
exact empty upper quarter, and returned the same count.

## Validation and benchmarks

| k | state | modulus | exact count | normalized mass |
|---:|---|---:|---:|---:|
| 1 | `(3,2,1)` | 360 | 60 | 0.408248290464 |
| 2 | `(6,4,2)` | 129,600 | 13,068 | 0.349296912860 |
| 3 | `(9,6,3)` | 46,656,000 | 3,542,949 | 0.322176345589 |
| 4 | `(12,8,4)` | 16,796,160,000 | 1,054,111,467 | 0.307455421497 |
| 5 | `(15,10,5)` | 6,046,617,600,000 | **330,159,210,305** | **0.299069097824** |

The first four counts match the existing dense Boolean DP exactly. Measured
packed-DP runs were:

| state | tile bits | threads | time (s) | peak bytes/worker bound |
|---|---:|---:|---:|---:|
| `(3,2,1)` | `2^20` | 32 | 0.001275 | 184 |
| `(6,4,2)` | `2^20` | 32 | 0.001363 | 32,976 |
| `(9,6,3)` | `2^20` | 32 | 0.008019 | 266,568 |
| `(12,8,4)` | `2^26` | 64 | 0.350399 | 17,056,896 |
| `(15,10,5)` | `2^30` | 64 | 193.149440 | 272,909,440 |
| `(15,10,5)` | `2^26` | 64 | 290.218861 | 17,056,896 |

The two complete `k=5` partitions used 5,632 and 90,102 tiles and
returned the same integer. The bounded current-binary run used 4,224
`2^30`-bit tiles and returned it again in 179.510390 seconds. An
independent literal-set implementation checked every one of the 105 states
through `(6,4,2)`. Packed comparisons passed 110/110, including terminal
tile widths `1, 7, 65, 1000, 65537`.

## Reproduction

```powershell
g++ -std=c++20 -O3 -march=native -fopenmp -Wall -Wextra -Wpedantic `
  -o problems/424/compute/wave3/C28_interval_dp/packed_tiled_dp.exe `
  problems/424/compute/wave3/C28_interval_dp/packed_tiled_dp.cpp

problems/424/compute/wave3/C28_interval_dp/packed_tiled_dp.exe `
  --a 15 --b 10 --c 5 --tile-bits 1073741824 --threads 64

python problems/424/compute/wave3/C28_interval_dp/verify_small.py
```

Machine-readable results and SHA-256 values are in
`problems/424/compute/wave3/C28_interval_dp/result.json`.

## Prior-work comparison

Section 5 of `R2_GPTPRO56.md` supplies the exact union recursion. The
existing `claude_rd_offset_mass_deep.py` evaluates it with full NumPy
Boolean arrays, and `C27_rd_mass_bracket.md` records the ray only through
`k=4`. C28 preserves that recurrence but replaces each full state array by
an exact tile envelope and packed residue scatter. This removes the memory
barrier and supplies the previously absent `k=5` integer.

This is an exact finite point, not an asymptotic proof of gate (M). It
extends the normalized sequence to `0.299069097824...`; no conclusion
about its positive limiting value is assumed.
