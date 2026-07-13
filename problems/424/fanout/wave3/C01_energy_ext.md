# C01: exact unthinned cross-colour energy extension

## Result

`compute/wave3/C01_energy_ext.py` extends
`compute/claude_rc_energy_probe.py` to the full dyadic reservoirs

\[
U=G_0\cap(Y/2,Y],\qquad V=G_2\cap(Z/2,Z]
\]

without thinning. The full `3 x 5` grid through `B=10^7` was feasible. The
largest case processes exactly `12,641,373,468` products in 45.289 s with
0.782 GiB peak process RSS. It gives

\[
 E=14,801,623,234,\quad |UV|=11,709,110,523,\quad
 E/(|U||V|)=1.170887267,\quad \kappa=92.623421830.
\]

Here `|UV|` denotes the number of distinct products, and

\[
 \kappa=\frac{EYZ}{|U|^2|V|^2}.
\]

## Exact algorithm

1. Generate `G cap [1,B]` by the exact ascending recurrence: apart from the
   seeds, `n in G` iff `n+1=ab` for distinct `a,b in G`. SPF factorization
   enumerates all divisor pairs. The proved mod-3 invariant skips only
   `n = 1 (mod 3)`.
2. Recursively partition the integer product axis into disjoint half-open
   buckets `[L,H)`. Exact binary searches count the pairs in each bucket.
   Split until each bucket has at most `100,000,000` pairs and `H-L <= 2^32`.
3. Materialize only `uv-L` for the current bucket as `uint32`, stable-radix
   sort in 11-bit digits, and count equal runs. If a run has length `r`, add
   `r^2` to `E` and one to the distinct-product count.
4. Sum bucket results. Disjoint product-value intervals make this exact;
   equal products cannot straddle buckets. Energy uses unsigned 128-bit
   accumulation. At most 24 OpenMP workers are admitted by the CLI.

The largest primary run had 261 buckets, the largest containing 99,766,163
pairs. Two `uint32` arrays for that bucket require 0.743 GiB; measured peak
process RSS was 0.782 GiB. A single legacy `int64` product array for all
12,641,373,468 pairs would occupy 94.186 GiB before sorting workspace.

## Validation

Generation at `B=10^7` returned

```text
|G|=4,952,270   |G0|=2,117,269   |G2|=2,835,001
wall=0.303 s    peak RSS=0.064 GiB
```

The total agrees with the independent `compute/census.cpp` checkpoint. The
bucket algorithm was compared to the original full-product sort on three real
instances, forcing a 10,000-product bucket cap:

| Y | Z | products | exact E | distinct | buckets | equal |
|---:|---:|---:|---:|---:|---:|:---:|
| 1,000 | 1,000 | 4,218 | 4,254 | 4,200 | 1 | yes |
| 1,000 | 10,000 | 56,943 | 58,665 | 56,098 | 9 | yes |
| 10,000 | 10,000 | 711,288 | 747,772 | 693,478 | 103 | yes |

The largest case was independently rerun with 12 workers and a 25,000,000
bucket cap. This changed the partition from 261 to 713 buckets and the peak
RSS from 0.782 to 0.225 GiB, while reproducing both exact integers:

```text
E=14,801,623,234   distinct=11,709,110,523
wall=56.226 s      peak RSS=0.225 GiB
```

## Exact table

All rows use `B=10^7`, full unthinned reservoirs, 24 workers, and a
100,000,000-product bucket cap. Wall time excludes generation but includes
bucket planning, materialization, radix sorting, and run counting. RAM is
peak process working-set RSS sampled every 10 ms.

| Y | Z | U size | V size | products | exact E | distinct | E/(UV pairs) | kappa | s | GiB |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 1,000 | 57 | 74 | 4,218 | 4,254 | 4,200 | 1.008534851 | 239.102619877 | 0.001 | 0.033 |
| 1,000 | 10,000 | 57 | 999 | 56,943 | 58,665 | 56,098 | 1.030240767 | 180.924919144 | 0.001 | 0.033 |
| 1,000 | 100,000 | 57 | 12,253 | 698,421 | 724,115 | 685,754 | 1.036788699 | 148.447526503 | 0.004 | 0.034 |
| 1,000 | 1,000,000 | 57 | 136,590 | 7,785,630 | 8,108,390 | 7,627,536 | 1.041455862 | 133.766421167 | 0.030 | 0.092 |
| 1,000 | 10,000,000 | 57 | 1,439,628 | 82,058,796 | 85,679,002 | 80,287,574 | 1.044117221 | 127.240134078 | 0.244 | 0.430 |
| 10,000 | 1,000 | 712 | 74 | 52,688 | 55,040 | 51,524 | 1.044640146 | 198.269083238 | 0.002 | 0.033 |
| 10,000 | 10,000 | 712 | 999 | 711,288 | 747,772 | 693,478 | 1.051292866 | 147.801293695 | 0.007 | 0.034 |
| 10,000 | 100,000 | 712 | 12,253 | 8,724,136 | 9,434,448 | 8,385,702 | 1.081419180 | 123.957166655 | 0.030 | 0.098 |
| 10,000 | 1,000,000 | 712 | 136,590 | 97,252,080 | 106,256,268 | 93,036,166 | 1.092586071 | 112.345779254 | 0.282 | 0.518 |
| 10,000 | 10,000,000 | 712 | 1,439,628 | 1,025,015,136 | 1,125,727,562 | 978,110,558 | 1.098254574 | 107.145205557 | 3.332 | 0.522 |
| 100,000 | 1,000 | 8,781 | 74 | 649,794 | 682,150 | 634,003 | 1.049794242 | 161.558007997 | 0.007 | 0.033 |
| 100,000 | 10,000 | 8,781 | 999 | 8,772,219 | 9,715,771 | 8,320,744 | 1.107561382 | 126.257835347 | 0.032 | 0.099 |
| 100,000 | 100,000 | 8,781 | 12,253 | 107,593,593 | 121,003,357 | 101,449,492 | 1.124633481 | 104.526064180 | 0.365 | 0.570 |
| 100,000 | 1,000,000 | 8,781 | 136,590 | 1,199,396,790 | 1,392,364,892 | 1,114,230,390 | 1.160887626 | 96.789289044 | 4.398 | 0.601 |
| 100,000 | 10,000,000 | 8,781 | 1,439,628 | 12,641,373,468 | 14,801,623,234 | 11,709,110,523 | 1.170887267 | 92.623421830 | 45.289 | 0.782 |

For every fixed `Y` in the requested set, kappa decreases as `Z` grows. On
the `Y <= Z` rows it falls from 239.103 at the smallest balanced scale to
92.623 at the largest tested scale. The collision factor remains close to
the diagonal (`E/(|U||V|) <= 1.171`), while 92.63% of the 12.64 billion pair
products in the largest case are distinct. These are finite exact facts, not
an asymptotic energy bound; using the full `G0,G2` windows also retains the
reservoir-density circularity noted in the prior probe.

## Commands executed

From repository root `E:\Projects\ErdosProblems`:

```powershell
python problems\424\compute\wave3\C01_energy_ext.py --limit 10000000 --workers 24 --bucket-products 100000000 --validation-only
```

```powershell
python problems\424\compute\wave3\C01_energy_ext.py --limit 10000000 --workers 24 --bucket-products 100000000 --no-validate --cases 1000:1000,1000:10000,1000:100000,1000:1000000,1000:10000000,10000:10000,10000:100000,10000:1000000,10000:10000000,100000:100000,100000:1000000
```

```powershell
python problems\424\compute\wave3\C01_energy_ext.py --limit 10000000 --workers 24 --bucket-products 100000000 --no-validate --cases 100000:10000000
python problems\424\compute\wave3\C01_energy_ext.py --limit 10000000 --workers 24 --bucket-products 100000000 --no-validate --cases 10000:1000,100000:1000,100000:10000
```

Partition-invariance rerun:

```powershell
python problems\424\compute\wave3\C01_energy_ext.py --limit 10000000 --workers 12 --bucket-products 25000000 --no-validate --cases 100000:10000000
```

One-command reproduction of the complete table (equivalent to the split
primary runs above, and also performs the product-sort validation):

```powershell
python problems\424\compute\wave3\C01_energy_ext.py --limit 10000000 --workers 24 --bucket-products 100000000 --full-grid
```

The Python driver auto-compiles its embedded C++20/OpenMP kernel with `g++`
and caches the executable under the system temporary directory. Measured
environment: Python 3.12.4, NumPy 2.2.6 (not used by the kernel), g++ 16.1.0,
64 physical/128 logical CPUs, Windows x86-64. The final verified script
SHA-256 is `d677c0a0a8ec41abbae15a4c934c97f9b856a5817e79cf012b5927aa7f9ee645`;
the one-command run on this hash reproduced every exact table integer.
