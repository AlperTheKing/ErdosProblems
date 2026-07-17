# C109: fixed reducible-root growth and the 32-bit C104-BIN frontier

## Verdict

The fixed-root question remains open.  No infinite hard-source family, no
uniform fixed-root bound, and no failure of `C104-BIN` was obtained.

There are, however, two new exact finite facts.

1. The root-`54` record rises from the C104 value `d=12` to

   \[
   d(1,559,219,514)=16,
   \qquad
   1,559,219,515=5\cdot7\cdot17\cdot19\cdot107\cdot1289.
   \]

   The missing endpoint `107` has seed-chain root `54`.

2. An eventwise scan of every hard source and reducible-root upgrade through
   `4,000,000,000` finds no `C104-BIN` failure.  This extends C104's exact
   endpoint by a factor of forty.  The full classification digest is
   `08eb5810482ec820`, exactly the C105 `4e9` digest, and the hard count is
   `106,360,959`, also exactly C105's count.

Thus the proposed fixed-root obstruction does not occur in the complete
32-bit range.  This is finite evidence only.

## 1. The single-root failure threshold

For root `54`,

\[
 2^5\le54-1<2^6.
\]

At threshold parameter `D`, this root belongs to the C104 union when it
witnesses a hard source with `d(h)>=D+1`.  A single root in bin `j=5`
therefore violates `C104-BIN` exactly when

\[
 D\ge33,\qquad d(h)\ge34.                         \tag{1}
\]

At C104's `1e8` endpoint, the only other active reducible root in this bin is
`62`.  It has the same threshold (1), since `2^5<=62-1<2^6`.

## 2. Finite seed chains do not give a pair-count bound

The recursive exact oracle verifies the complete missing initial segments

```text
root 54: 107, 213, 425 missing; 849 generated
root 62: 123, 245 missing;      489 generated
```

Once `849` or `489` is generated, every later node on that seed-2 chain is
generated from its parent.  Hence each fixed root has only finitely many
possible missing endpoints.

This is not a uniform bound on `d(h)`: one fixed endpoint can divide
arbitrarily many candidate successors `h+1`, while the other admissible pairs
may be blocked by unrelated holes.  The chain termination mechanism limits
endpoint labels, not source pair multiplicity.  No argument found here turns
it into a fixed-root pair-count bound.

## 3. Exact fixed-root records

The focused scanner stores a record only when the maximum witnessed pair
count strictly increases.

| root | `h` | `d(h)` | factorization of `h+1` | fixed-root endpoint |
|---:|---:|---:|---|---:|
| 54 | 534 | 1 | `5 * 107` | 107 |
| 54 | 1,064 | 2 | `3 * 5 * 71` | 213 |
| 54 | 4,674 | 3 | `5^2 * 11 * 17` | 425 |
| 54 | 14,024 | 6 | `3 * 5^2 * 11 * 17` | 425 |
| 54 | 512,264 | 8 | `3 * 5 * 13 * 37 * 71` | 213 |
| 54 | 1,182,774 | 9 | `5^2 * 11^2 * 17 * 23` | 425 |
| 54 | 7,634,274 | 12 | `5^2 * 11 * 17 * 23 * 71` | 425 |
| 54 | 1,559,219,514 | 16 | `5 * 7 * 17 * 19 * 107 * 1289` | 107 |
| 62 | 614 | 2 | `3 * 5 * 41` | 123 |
| 62 | 2,694 | 3 | `5 * 7^2 * 11` | 245 |
| 62 | 9,470 | 4 | `3 * 7 * 11 * 41` | 123 |
| 62 | 65,414 | 6 | `3 * 5 * 7^2 * 89` | 245 |
| 62 | 241,814 | 8 | `3 * 5 * 7^3 * 47` | 245 |
| 62 | 552,474 | 9 | `5^2 * 7^2 * 11 * 41` | 245 |
| 62 | 2,778,054 | 12 | `5 * 7^2 * 17 * 23 * 29` | 245 |
| 62 | 298,274,514 | 16 | `5 * 7^3 * 11 * 97 * 163` | 245 |

Both maxima are exactly `16` through `4e9`.  Since `16<34`, neither fixed
root alone comes close enough to force (1) in the complete scanned range.

## 4. Targeted 64-bit searches

`C109_fixed_root_search.py` is not a prefix census.  It factors only
structured successors and decides generatedness recursively from the seeds
`2,3`.  Deterministic Miller--Rabin bases valid below `2^64` certify primes;
deterministically seeded Pollard--Brent supplies factors; every factor is
retested as prime and the product is checked.

The pinned no-hit searches include:

| fixed endpoint/family | exact high-pair candidates | range |
|---|---:|---|
| root `54`, `N=7,634,275 q^2` | 9,585 | prime `q<=100,000` |
| root `54`, `N=1,559,219,515 q^2` | 9,584 | prime `q<=100,000` |
| root `54`, `N=7,634,275 qr` | 21,756 | primes `q<r<=2,000`, `qr=1 mod 3` |
| endpoint `213`, squarefree support | 74,613 | six extra primes `<=100` |
| endpoint `425`, mixed support | 47,541 | six extra primes `<=100` |
| endpoint `107`, squarefree support | 2,564 | seven extra primes `<=50` |

Every row is prefiltered to `d(h)>=34`; every candidate then fails hardness
because at least one admissible pair has both endpoints generated.  These
families are finite and do not exhaust all 64-bit successors.

## 5. Eventwise C104-BIN scan

`C109_bin_failure_scan.cpp` reconstructs the literal C104 state in ascending
order.  For every hard source it forms the complete non-splitless witness-root
set, upgrades each root's maximum witnessed `d`, and tests

\[
 (k-1)\#\{r:2^j\le r-1<2^{j+1},\ \max d(r)\ge k\}\le2^j
\]

immediately after the source event.  It stops at the first failure and would
emit the full offending root set.  Results:

| requested limit | scanned through | hard sources | maximum `d` | first failure |
|---:|---:|---:|---:|---|
| `100,000,000` | `100,000,000` | `3,368,726` | 12 | none |
| `4,000,000,000` | `4,000,000,000` | `106,360,959` | 18 | none |

At `1e8` its classification digest is C104's
`94633c57cc653c6e`.  At `4e9` its classification digest is C105's
`08eb5810482ec820`.  These exact whole-prefix matches guard against a
fixed-root-only implementation accidentally changing the closure.

## 6. Independent audit and prior art

The Python verifier uses the recursive closure oracle rather than the global
SPF state arrays.  It refactors and reclassifies all sixteen record sources,
checks every admissible pair is blocked, checks the fixed witness endpoints,
checks both chain terminations, and pins the four global JSON hashes.  Its
output is `C109_fixed_root_verify.json`.

C104 established no bin failure through `1e8` and the root-`54` record
`d=12`.  C105 classified through `4e9` and found global maximum `d=18`, but
did not isolate fixed-root records or run C104-BIN eventwise there.  C109 adds
those two exact pieces.  The public problem page still lists Erdos #424 as
open and has no claimed partial solution in its discussion as of 2026-07-13:
<https://www.erdosproblems.com/424>.

## 7. Status

The fixed-root obstruction to C104-BIN is not seen through `4e9`.  Root `54`
and root `62` both reach `d=16`, while a one-root failure needs `d>=34`.
The finite chain mechanism does not prove a uniform bound, and the targeted
64-bit families do not prove boundedness or unboundedness.  Consequently
`C104-BIN` remains unproved and unfalsified.

Sources and exact artifacts are pinned in `C109_SHA256SUMS.txt`.
