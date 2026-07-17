# C113: moving token packing from missing-endpoint chains

## DIRECT ROUTE

1. **Exact final deliverable.** Prove or exactly refute, uniformly in `X`,
   the C108-MOVE-PACK inequalities
   \[
   \sum_{i=2}^k \min\{\lceil\sqrt{q_X(r_i)}\rceil,j\}
      \le r_k-2^j
   \]
   for the sorted reducible witness roots `r_1<...<r_s` with
   `2^j<=r_i-1<2^(j+1)`.  A fallback deliverable is a strictly weaker proved
   packing inequality that implies C110-CAR with
   `alpha>1/log(2)-1` and `J(D)=o(D)`.
2. **Current frontier lemma or finite certificate.** Construct an explicit
   injection of each nonleast root's capped square-root token copies into
   integer slots no larger than `r-1`, using the root's missing-endpoint
   `U`-chain and distinct complementary divisor pairs of hard sources.
3. **Logical bridge.** The displayed nested inequalities are exactly Hall's
   conditions for the nested slot neighborhoods `[2^j,r_i-1]`; hence they
   prove C108-MOVE-PACK.  A root with `q_X(r)>=D` then contributes at least
   `ceil(sqrt(D))` tokens when `j>=ceil(sqrt(D))`, yielding the C110
   square-root bin tail and therefore C110-CAR and the C99 contraction route.
4. **Next falsifiable action.** Reconstruct every source-root-endpoint-pair
   incidence through a bounded exact prefix, define candidate token labels
   only from that arithmetic data, and test injectivity and every nested
   deadline at each root-load upgrade; reject a candidate at its first exact
   counterexample before attempting its proof.
5. **Exit condition.** Exit with a uniform proof, an exact violating tuple
   `(X,j,k)` with its full arithmetic certificate, or a proved weaker packing
   theorem with an explicit derivation of C110-CAR.  Abandon any branch whose
   token labels merely restate the deadline inequalities or lack that bridge.

## Status

The requested uniform inequality remains open.  No exact C108-MOVE-PACK
falsifier and no weaker packing sufficient for C110-CAR was obtained.  The
unconditional result of this task is the constant-three packing theorem
below.  It proves C108-MOVE-PACK on the subfamily `q_X(r)<=9`, but it does not
have the square-root saving required by C110-CAR.

The explicit complementary-pair token map in Section 2 passes its exact test
through `X=10^7`, but its proposed uniform Hall bridge is false: one forced
gap can serve six roots.  A direct construction search for the first
geometrically capable target counterexample is exhausted below `2^64` for a
shared source, but that is only a finite exclusion.

## 1. A uniform three-token packing

### Theorem C113.1

Fix `X` and `j>=1`, put `B=2^j`, and list any subset of reducible witness
roots in the bin as

\[
 r_1<\cdots<r_k,\qquad B\le r_i-1<2B.
\]

Then

\[
 3(k-1)\le r_k-B.                                      \tag{6}
\]

Consequently, if every listed root has `q_X(r)<=9`, then

\[
 \sum_{i=2}^k w_j(r_i)\le r_k-B                       \tag{7}
\]

for every prefix.  An explicit packing is obtained by processing roots in
increasing order and assigning each nonleast root's tokens to the least
currently unused slots in `[B,r_i-1]`.

### Proof

Every witness root is even and belongs to the allowed set, so its residue
modulo six is `0` or `2`.  Also `2^j` is `2` or `4` modulo six.  If
`B=2 (mod 6)`, the allowed even integers after `B` occur at offsets

\[
 4,6,10,12,16,18,\ldots.
\]

If `B=4 (mod 6)`, they occur at offsets

\[
 2,4,8,10,14,16,\ldots.
\]

In both lists the `m`-th offset is at least `3(m-1)`.  The `m`-th member of
an arbitrary subset can only occur later, proving (6).  Since
`q_X(r)<=9` gives

\[
 w_j(r)=\min\{\lceil\sqrt{q_X(r)}\rceil,j\}\le3,
\]

(7) follows.  At each deadline `r_i-1`, (7) says that the stated
earliest-deadline assignment has enough unused slots.  QED.

Before retaining this invariant, direct enumeration of every allowed-root
prefix for `1<=j<=20` checked `699,050` deadlines and returned no failure.

This is a genuine uniform packing, but its constant token count gives no
decay in a threshold `D>9`, so it does not imply C110-CAR.

## 2. Missing-chain/complementary-pair token map

For a root `r` whose load is attained by a hard source `h`, put `N=h+1` and
choose a missing endpoint `p=U^t(r)` in one admissible complementary divisor
pair of `N`.  For every other admissible pair, let `a` be its smaller factor
and define

\[
 g_r(a)=
 \begin{cases}
 r-a+1,&a\equiv r\pmod3,\\
 r-2a+2,&a\not\equiv r\pmod3.
 \end{cases}                                           \tag{8}
\]

Both `a` and `r` are allowed residues, and (8) always has residue `1`
modulo three.  Thus `g_r(a)` cannot itself be a witness root.  The tested
token map gives `r` the two baseline slots `r-2,r-1`; each further token may
use either `g_r(a)-2` or `g_r(a)-1` when

\[
 B+2\le g_r(a)<r.                                      \tag{9}
\]

Duplicate labels are removed, and an exact augmenting-path matching is run
over all roots in the bin.  This uses the actual missing endpoint
`U^t(r)` and the actual complementary pairs of a source attaining the root
load; it is not a reformulation of the deadline inequality.

`C113_invariant_scan.py` reconstructs the complete closure through
`X=10,000,000`.  It finds `392,961` hard sources, maximum pair count `12`,
and `15,192` root-load upgrades.  At the final cutoff, (8)-(9) have no local
token shortage and the global matching has no failure.  Normal and
`python -O` outputs are byte-identical, with SHA-256

```text
8a05ec3fa5d2e82037886c2d43c30993f0eef0f7f6f1e8d39325110c44a4d382
```

This finite pass does not prove the map.  The intended shortcut was that a
forced gap would occur for at most two roots, matching its two adjacent
slots.  That assertion is exactly false.  The first degree-three gap is

```text
X = 10000000, j = 7, gap = 142, roots = [170, 174, 188].
```

The maximum forced-gap degree in the same exact reconstruction is `6`.
The augmenting matching still succeeds, but there is no proved Hall bound
controlling these cross-root collisions.

`DEAD: forced-gap Hall shortcut -- a forced gap has degree 6 at X=10^7, so
the proposed degree-two collision bound and its Hall bridge are false.`

Two simpler source invariants fail earlier.  At `h=4674`, the three pairs
are `(5,935),(11,425),(17,275)`.  Root `54` is witnessed by endpoint `425`
and has `q=2`, hence weight `2`, but only one lower missing endpoint/root is
available (`11`, rooted at `6`).  Root `54` is the least root in its bin, so
this is not a C108-MOVE-PACK counterexample.

## 3. Exact falsifiers of stronger statements

The uncapped linear version of the nested inequality is false.  At
`X=3,000,000,000`, bin `j=7`, the prefix ending at root `188` is

| root | `q_X(r)` | attaining source | endpoint |
|---:|---:|---:|---:|
| `140` | `11` | `217115814` | `557` |
| `144` | `11` | `387992142` | `287` |
| `170` | `15` | `1763337894` | `677` |
| `174` | `11` | `290378274` | `347` |
| `186` | `9` | `70116402` | `371` |
| `188` | `15` | `1559219514` | `749` |

After exempting root `140`, the exact linear load is

\[
 11+15+11+9+15=61>188-128=60.                    \tag{10}
\]

The C108 load for the same prefix is only `4+4+4+3+4=19`, so (10) is not a
target falsifier.

Another tempting strengthening assigns the full cap `j` to every reducible
even root whose first `U`-node is missing.  It first fails in bin `18` at
roots `262148,262158`, where `18>262158-2^18=14`.  This superset is invalid:
root `262148` has only the missing chain endpoint `524295`, which is divisible
by `9`, while its next `U`-node `1048589` is generated.  Any source using
`524295` satisfies the seed-three easy condition and therefore cannot be
hard.  Thus `q_X(262148)=0` for every `X`.

## 4. Full-prefix target audit

`C113_vulnerable_prefix_scan.cpp` is an owned copy of the C108 exact scanner
that retains every root certificate within `8j^2` of a dyadic boundary.  Its
run through `X=3,000,000,000` reproduces

```text
hard sources               81206966
maximum pair count         18
classification FNV-1a-64  6b2d96f7618ce698
C104-BIN failure           null
C108 weighted failure      null
```

The independent integer replay checks `726` retained certificates in `24`
bins and `702` nontrivial prefixes.  It finds no C108-MOVE-PACK failure.  The
minimum square-root slack is `12`, at `(j,r)=(7,144)`, where `4<=16`.  It
also finds no retained prefix capable of failing even if all its present
roots later attain the full cap.  The normal and optimized replay outputs
are byte-identical with SHA-256

```text
c12f575d1ab01693b445504dc30d874abb4bd04b6925af0c5cb87e5f2d592219
```

This is finite evidence only.  Event loads are monotone, so the scanner's
null target field covers every cutoff through `3*10^9`; it supplies no
uniform theorem.

## 5. Direct counterexample construction at the first capable cluster

After removing the impossible root `262148`, the first active-root prefix
that can violate a full-cap packing is

\[
 262158<262172<262176,qquad j=18.                 \tag{11}
\]

Root `262158` is already witnessed by the exact hard source
`h=1921614474`, whose product `h+1=1921614475` has `d=6`.  It therefore
takes the least-root exemption.  The missing initial `U`-chain endpoints of
the other two roots are

\[
\begin{aligned}
262172 &: 524343,\ 1048685,\\
262176 &: 524351,\ 1048701.
\end{aligned}                                      \tag{12}
\]

A shared hard source with `d>=258` and one endpoint from each line of (12)
would give both roots weight at least `17`, producing

\[
 17+17=34>262176-2^{18}=32,                       \tag{13}
\]

an exact C108-MOVE-PACK falsifier.  Of the four endpoint combinations, the
pair `(524343,1048701)` forces the product to be divisible by `9` and hence
cannot be hard.  The other three combinations were exhaustively enumerated
for products below `2^64`.

| endpoints | max multiplier | eligible multipliers | `d>=258` | max `d` |
|---|---:|---:|---:|---:|
| `524343,524351` | `67093762` | `22364587` | `219101` | `1536` |
| `1048685,524351` | `33546913` | `14909740` | `924273` | `2688` |
| `1048685,1048701` | `16773472` | `5591157` | `801900` | `2688` |

The arithmetic sieves count admissible complementary pairs exactly.  The
recursive closure checker then classified all `1,945,274` threshold
candidates and found `hard_rows=[]`; none is a hard source.  Hence
there is no shared-source falsifier of the form (12)-(13) below `2^64`.
This does not exclude separate attaining sources for the two roots or larger
products and is not a target proof.

`DEAD: first compatible cap-violating cluster -- every feasible shared
missing-endpoint product with d>=258 below 2^64 is generated; finite 64-bit
exhaustion gives no bridge to uniform X.`

A separate exact scan of the recurrent C105 `d=8` single-source family tested
`293,118` eligible primes in `(10^6,10^7]`, found six hard members, and found
no target failure.  Its closest new prefix had slack `3781`.  Fixed-root
plus-prime lifts from all eight hard bases witnessing root `262158` reached
pair count `8` but did not create (13).  These bounded family exclusions are
not extended further under the direct-proof guard.

## 6. Artifact checks

All created files have the `C113_` prefix under `compute/wave5`.  The
decisive output hashes are:

| artifact | SHA-256 |
|---|---|
| `C113_invariant_scan_10000000.json` | `8a05ec3fa5d2e82037886c2d43c30993f0eef0f7f6f1e8d39325110c44a4d382` |
| `C113_vulnerable_prefix_scan_3000000000.json` | `e49ec8f7c1a750f41732c4d87ef1277d752d79325f41100248def54020e1e87e` |
| `C113_boundary_replay_3000000000.json` | `c12f575d1ab01693b445504dc30d874abb4bd04b6925af0c5cb87e5f2d592219` |
| `C113_cluster_multiplier_sieve.json` | `6ef7e867980fb931b45669f3ecf7d157b7d83ed46b1049806565981ba3f44a15` |
| `C113_cluster_closure_check_all.json` | `69051624db06ec87e3b736d010c9b6b4586bde4ac0e5502ce506ba03a1ccefec` |
| `C113_cluster_endpoint_sieve.json` | `f93d5c72f8644069db5f9d9de97f8c5e8872184030b98e718634975758dc533d` |
| `C113_cluster_endpoint_closure_check_all.json` | `bae01ae639d336230dade05a32413f6c52d130dde36c637ce16bbd6a6d042bd0` |

Normal and `python -O` invariant scans are byte-identical.  Normal and
optimized boundary replays are also byte-identical.  No shared ledger was
edited.

## 7. Precise outcome

1. C108-MOVE-PACK: neither proved nor refuted.
2. C110-CAR-sufficient weaker packing: not obtained.
3. Uniform proved result: Theorem C113.1, the three-token packing, sufficient
   only while `q_X(r)<=9`.
4. Stronger linear nested packing: exactly refuted by (10).
5. Complementary-pair token map: exact finite pass, but no theorem because
   the required collision bound is false.
6. First direct cap-capable shared-source construction: exactly absent below
   `2^64`, with no uniform implication.
