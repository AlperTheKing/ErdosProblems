# C32: exact streaming energy for the R-D reservoir at ray `(3,2,1)`, `K=5`

## Result

The C26 in-memory product expansion stopped before

\[
N_5=2(7779)(2111340)=32848227720
\]

because one raw product array exceeded the memory lane.  A disjoint
high-product-band decomposition removes that obstruction without changing the
reservoir.  The exact `K=5` result is

\[
\boxed{E_5=32964715932},\qquad
\boxed{\frac{E_5}{N_5}=\frac{2747059661}{2737352310}
=1.003546255615\ldots}.
\]

The complete source-block collision matrix, with rows and columns ordered by
`k=2,3`, is

```text
16445373288   35749664
   35749664 16447843316
```

Consequently

```text
within collision pairs = 22,494,442
cross-k collision pairs = 35,749,664
distinct products       = 32,790,241,278
maximum multiplicity    = 6
```

and the exact multiplicity histogram is

```text
r=1 : 32,732,509,822 products
r=2 :     57,479,103 products
r=3 :        249,764 products
r=4 :          2,546 products
r=5 :             42 products
r=6 :              1 product
```

This is not a gate-(E) falsifier.  The exact sequence now available on this
ray is

```text
K=2: 1.001543209877
K=3: 1.005084915228
K=4: 1.006166320928
K=5: 1.003546255615
```

These are finite values only.  In particular, the decrease at `K=5` does not
prove that `sup_K E_K/N_K` is finite.

## Exact band decomposition

For source rectangle `k`, write

\[
R_{K,k}=U_k\times V_{K-k}.
\]

Fix a bit shift `s`.  A pair `(u,v)` belongs to the unique band

\[
B_q=\{(u,v):q2^s\le uv<(q+1)2^s\},
\qquad q=\left\lfloor\frac{uv}{2^s}\right\rfloor.
\]

For a fixed row factor `u`, the sorted column interval in this band is found
exactly by the two integer endpoints

\[
v\ge\left\lceil\frac{q2^s}{u}\right\rceil,
\qquad
v<\left\lceil\frac{(q+1)2^s}{u}\right\rceil.
\]

Thus binary search materializes every product exactly once and no product can
cross a band boundary.  Within each band, the product values from every source
rectangle are radix-sorted and run-merged.  If `c_i(n)` is the multiplicity
from source `i`, the code adds

\[
c_i(n)c_j(n)
\]

to every collision-matrix entry `(i,j)`.  Summing independently computed
bands therefore gives the full global energy, including all cross-`k`
collisions.

The implementation parallelizes independent bands over 16 workers.  For the
`s=38` run there were 546 nonempty bands and the largest band contained
128,443,745 product values across both source rectangles.  The observed
resident set stayed below 17 GB, within the assigned 64 GB lane.  The method
uses exact `uint64` products and `uint128` counters; floating point is used
only to print the decimal copy of the reduced exact fraction.

## Validation

Before `K=5`, the streaming implementation was run at `K=2,3,4`.  It matches
C26 exactly on all of the following fields:

- block supports, color counts, and FNV fingerprints;
- source pair counts;
- total and distinct product counts;
- full collision matrices;
- total energy and reduced fraction;
- within- and cross-source collision counts;
- maximum multiplicity and complete multiplicity histogram.

The `K=5` computation was then repeated with two different exact partitions:

```text
s=38: 546 bands, peak band size 128,443,745
s=37: different band partition, peak band size 64,561,547
```

The independent partitions agree on every energy field listed above.  Their
JSON files differ only in band metadata and SHA-256, as expected.

The C26 tie ambiguity is explicit in the command-line interface: `g0` and
`g2` are separate tie policies.  The ray `(3,2,1)` has no tied color block, so
the `K=5` value is tie-independent.  For ray `(2,1,1)`, the policy continues
to select the requested side of the unique `6/6` split at `k=1`.

## Reproduction

From `problems/424/compute/wave3/C32_rd_energy_streaming`:

```powershell
g++ -std=c++20 -O3 -march=native -fopenmp rd_energy_stream.cpp -o rd_energy_stream.exe
./rd_energy_stream.exe 3 2 1 3 5 38 g0 result_321_K5_s38.json 16
./rd_energy_stream.exe 3 2 1 3 5 37 g0 result_321_K5_s37.json 16
python verify_partition_equivalence.py result_321_K5_s37.json result_321_K5_s38.json --output verify_K5_partitions.json
```

Validation against C26 is performed by `verify_streaming.py`; the recorded
`K=2,3,4` run gives `PASS` on all three rows.

SHA-256:

```text
rd_energy_stream.cpp
  09ff3e435f98c4ebd0f73350ba5ed7eecb164e7d819f86c1f4e45ff40d564361
verify_streaming.py
  5410b667d8b91893a8723d91f8fe07684a73759000f611bbfe8ce4d0751331f9
verify_partition_equivalence.py
  2c62fc8e15a9304066f705e61778898563b44a2ee98cebad118915f9bc870a26
result_321_K5_s37.json
  1528631ee409c920e1d0dcee4592b88d857e37d04a72fb06f4ad75b04d7161aa
result_321_K5_s38.json
  1c7b3663a31ae893375d0ae731070d200cace3647b60c04edaf665899ca84b5e
verify_K2_K4.json
  96024e295a705b3d376cc3e7d2eacedf273a24c6ceaaa35bd4d524e0465f9190
verify_K5_partitions.json
  0f3abbdabba987474ee1a3f37bce3615dc19c81dac0a66da4c1de6a73d9269b0
```

## Finite-only conclusion

The previously infeasible `K=5` energy is exact and remains within a factor
`1.004` of pair mass.  It supplies no evidence that `E_K/N_K` is unbounded at
the tested scale and therefore no falsifier to gate (E).  Establishing or
refuting a uniform asymptotic bound remains open.
