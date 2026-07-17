# C108: C104-BIN adversary and moving square-root tail gate

## Verdict

No proof or counterexample to C104-BIN was obtained.  The exact scan found no
failure through

\[
X=3,000,000,000.
\]

The useful outcome is a strictly weaker sufficient target which incorporates
both requested relaxations: exponent `alpha=1/2` and a moving cutoff

\[
J(D)=\lceil\sqrt D\rceil=o(D).
\]

The target has an exact per-root token formulation.  For a reducible witness
root `r`, define

\[
 q_X(r)=\max\bigl(\{d(h)-1:h\le X,\ h\text{ hard, and }r
             \text{ witnesses }h\}\cup\{0\}\bigr).                 \tag{1}
\]

In denominator bin `I_j=[2^j,2^(j+1))`, give `r` the capped load

\[
 w_j(r)=\min\{\lceil\sqrt{q_X(r)}\rceil,j\}.                       \tag{2}
\]

The sharply stated next lemma is:

**C108-MOVE-PACK.**  In every bin, after optionally exempting one root, the
`w_j(r)` token copies inject into the `2^j` integer slots of `I_j`, with every
token of `r` assigned to a slot no greater than `r-1`.

This lemma implies

\[
 \#R_{X,D,j}\le 1+{2^j\over\sqrt D}
 \qquad(j\ge\lceil\sqrt D\rceil),                                  \tag{3}
\]

which is enough for C99.  No theorem claim for C108-MOVE-PACK is made.  Its
canonical nested-neighborhood gate has no failure through `3*10^9`, and the
largest exact total token load is `43/128` of a bin.

## 1. General moving-tail reduction

Write

\[
 N_{X,D,j}=\#\{r\in R_{X,D}:2^j\le r-1<2^{j+1}\}.
\]

Suppose that for fixed `alpha>0`, fixed `C`, and some integer function
`J(D)=o(D)`, one has uniformly

\[
 N_{X,D,j}\le 1+C{2^j\over D^\alpha}
 \qquad(j\ge J(D)).                                                  \tag{4}
\]

This additive one is harmless and permits one exceptional root per bin.  In
an early bin the trivial bound `N_{X,D,j}<=2^j` gives reciprocal mass at most
one.  In a tail bin, (4) gives reciprocal mass at most

\[
 2^{-j}+C D^{-\alpha}.
\]

Every witness root through `X` has `r-1<X`, so there are at most
`1+floor(log_2 X)` bins.  Therefore, with `Sigma_D(X)` denoting the reducible
root reciprocal mass,

\[
 {\Sigma_D(X)\over D}
 \le {J(D)\over D}+{2^{1-J(D)}\over D}
     +{C(1+\lfloor\log_2X\rfloor)\over D^{\alpha+1}}.                \tag{5}
\]

Take `D=floor((ln X)^c)`.  Equation (5) is `o(1)` whenever

\[
 {1\over\alpha+1}<c<\log 2,                                        \tag{6}
\]

provided `J(D)=o(D)`.  Such a `c` exists precisely when

\[
 \alpha>{1\over\log2}-1.
\]

For `alpha=1/2` and `J(D)=ceil(sqrt(D))`, equation (5) becomes

\[
 {\Sigma_D(X)\over D}
 =O(D^{-1/2})+O\left({\log X\over D^{3/2}}\right)=o(1)              \tag{7}
\]

for every fixed `2/3<c<log 2`.  Combined with C99's low-pair sieve, this is
the required reducible-root estimate.  Thus full linear C104-BIN is not
needed.

## 2. Exact packing implication

Fix `X,j`, list the roots with `q_X(r)>0` as

\[
 r_1<r_2<\cdots<r_s,
\]

and give every token of `r_i` the nested slot neighborhood

\[
 [2^j,r_i-1]\cap\mathbb Z.
\]

The standard earliest-deadline matching is feasible exactly when

\[
 \sum_{i=1}^k w_j(r_i)\le r_k-2^j
 \qquad(1\le k\le s).                                                \tag{8}
\]

Allowing the least root as the single exception replaces the sum in (8) by
`sum_(i=2)^k`.  This is the exact C108 gate.

If `j>=ceil(sqrt(D))` and `q_X(r)>=D`, then (2) gives

\[
 w_j(r)\ge\lceil\sqrt D\rceil.
\]

An injection for all nonexceptional roots therefore gives

\[
 (N_{X,D,j}-1)\sqrt D\le2^j,
\]

which proves (3).  The cap in (2) is the moving-cutoff mechanism: for fixed
`j`, arbitrarily large future values of `q_X(r)` do not increase the token
load beyond `j`.

## 3. Adversarial failures of simpler packings

The uncapped linear load `q_X(r)` supports neither natural one-sided local
packing.

* Packing each root's linear tokens only at slots at or above `r-1` fails at
  `X=5114`.  In bin `j=8`, root `512` has `q=3`, source `5114`, and witness
  endpoint `1023`, but only one slot remains from denominator `511` to the
  upper bin boundary.  The exact failed inequality is `3<=1`.
* Packing the linear tokens only at slots at or below `r-1` fails at
  `X=112664`.  In bin `j=6`, root `68` has `q=7`, source `112664`, and witness
  endpoint `1073`, while `[64,67]` has four slots.  The exact failed inequality
  is `7<=4`.

These are falsifiers of the local packing mechanisms, not of C104-BIN.

The stronger simultaneous linear budget

\[
 \sum_{r\text{ in bin }j}q_X(r)\le2^j                              \tag{9}
\]

also has no failure through `3*10^9`, but is nearly saturated: its maximum is
`127/128` in bin `j=7`.  It is not adopted as the proof target.  The moving
square-root load in (2) has much more room and ignores fixed-root load growth
beyond the moving cutoff.

## 4. Exact computation

`C108_weighted_token_gate.cpp` reconstructs the least closure in increasing
order using exact divisor enumeration.  It stores every root's maximum `d`,
updates all threshold counts, tests C104-BIN eventwise, and tests (8) at the
endpoint.  All endpoint loads are monotone in `X`, so an endpoint pass of (8)
also certifies every earlier cutoff.

At `X=3,000,000,000` it reports:

| quantity | exact result |
|---|---:|
| hard sources | `81,206,966` |
| maximum `d(h)` | `18` |
| classification FNV-1a-64 | `6b2d96f7618ce698` |
| C104-BIN failures | `0` |
| linear weighted-budget failures | `0` |
| moving square-root deadline failures | `0` |
| moving square-root deadline failures after least-root exemption | `0` |

The exact extrema are:

| gate | maximum | location |
|---|---:|---:|
| C104 linear ratio `D*N/2^j` | `15/16` | `j=5,D=15,N=2` |
| half-tail squared constant `D*N^2/2^(2j)` | `275/4096` | `j=7,D=11,N=10` |
| moving token mass `sum(w_j)/2^j` | `43/128` | `j=7` |
| simultaneous linear mass `sum(q_X)/2^j` | `127/128` | `j=7` |

Thus the direct half-tail inequality with `C=1` has no failure through the
full range, even without the additive one or moving cutoff.  This remains
finite evidence only.

## 5. Independent replay

`C108_token_gate.py` is an independent full-SPF implementation.  Through
`10^6` it exactly matches the C++ hard-source count and all 12 nonempty bins'
threshold counts, linear token sums, and moving square-root sums.

`C108_gate_replay.py` also compares the C++ pass at `10^8` with C104's pinned
raw artifact.  It matches the hard-source count, maximum pair count,
classification digest `94633c57cc653c6e`, and all 19 nonempty threshold-bin
vectors.  Its `3*10^9` replay checks 350 threshold entries using integers and
`Fraction` only and reproduces all four exact extrema above.

Normal and `python -O` executions of both Python verifiers are byte-identical.
A second C++ pass through `10^6` is also byte-identical to the first.

## 6. Precise status

C104-BIN remains open.  The exact next theorem target for the relaxed C99
route is C108-MOVE-PACK, or directly the count bound (4) with some
`alpha>1/log(2)-1` and `J(D)=o(D)`.  For the concrete half-power route, a
falsifier to the canonical gate is an exact tuple `(X,j,k)` violating (8)
with the capped loads (2).  No such tuple occurs through `3*10^9`.
