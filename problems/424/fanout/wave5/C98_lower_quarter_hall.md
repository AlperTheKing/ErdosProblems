# C98: lower-quarter Hall structure and local countermodels

## Verdict

No proof or falsifier of

\[
                 2D(X)\ge 7A_H(\lfloor X/4\rfloor)       \tag{LQ}
\]

is claimed.  This sidecar proves a uniform combinatorial equivalence for
`(LQ)` and gives two exact root-labelled falsifiers to narrower local
mechanisms.

For an integer `Y`, let `H_Y` be the hard roots persistent through `Y` and
let `S_Y` be the splitless roots healed through `4Y`.  Give every `h in H_Y`
seven demand slots and every `e in S_Y` two labelled supply slots.  Join
`h` to both copies of `e` exactly when

\[
                             e\le 2h.                    \tag{1}
\]

The following is rigorous.

* If `(LQ)` holds at every integer scale through `Y`, this graph has an
  integral matching that gives seven distinct slots to every `h in H_Y`.
* Conversely, such a matching at `Y` implies `(LQ)` at `X=4Y`.

Thus a size-local disjoint family always exists if the lower inequality is
true, but proving that it exists is equivalent to proving all the prefix
inequalities.  Hall matching does not make the arithmetic frontier weaker.

The coefficient `7/2` is bookkeeping, not a factorization constant.  If the
C92 upper gate

\[
 A_H(X)\le D(X)+A_H(\lfloor X/4\rfloor)+1              \tag{2}
\]

is combined with `D(X)>=c A_H(floor(X/4))`, the resulting same-scale ratio
is `c/(c+1)`.  Crossing the C91 threshold `3/4` requires `c>3`; `7/2` is the
smallest half-integer above `3`.  At `c=7/2`, the exact composition is

\[
                         7A_H(X)\le9D(X)+7.             \tag{3}
\]

Root-labelled computation independently replayed through `X=10^6` finds no
failure of `(LQ)`.  Its minimum positive ratio is

\[
 {D(4Y)\over A_H(Y)}={309\over87}={103\over29}
 \quad\hbox{at }Y=2064.                                \tag{4}
\]

At that cutoff only nine of the 618 supply slots are spare.  At least 96 of
the 100 healed roots in `(Y,2Y]` are compulsory in any capacity-two witness.
This is the isolated frontier: a proof must control fresh, closure-dependent
one-step healing events, not just downward shadows of the hard sources.

## 1. Root-labelled finite start

### 1.1 The first hard source already needs unrelated supply

At `Y=54`, the persistent hard set is `{54}`.  Its complete forced descent is

```text
54: 55 = 5*11,  5 generated, 11 a hole
11: 12 = 2*6,   2 generated, 6 splitless
```

Grant a support-local mechanism every healed root `e` for which `e+1`
shares any prime with any successor in this descent.  This is deliberately
broader than the prime-square shadow or direct obstruction leaf.  The full
prime support is

```text
{2,3,5,7,11},  radical 2310.
```

The complete bank `D(216)` is:

| root `e` | `e+1` | first generated iterate | generating pair |
|---:|---:|---:|:---|
| 6 | 7 | 41 | `3*14` |
| 18 | 19 | 69 | `5*14` |
| 20 | 21 | 77 | `3*26` |
| 38 | 39 | 149 | `3*50` |
| 66 | 67 | 131 | `3*44` |

Only `6,20,38` are support-local.  Their two copies have total capacity
`6<7`.  The unrelated roots are `18` and `66`, so at least one unrelated
slot is forced even for the first hard source.

The C74 prime-square shadows are `24` and `120`; neither is in `D(216)`.
The multiplicative lifts of the sole obstruction leaf `6` are the roots
with `7|(e+1)`, namely only `6,20` inside this bank.  Hence the larger
prime-support relation fails after both canonical mechanisms are included.

This is an exact falsifier to the proposed support-local mechanism, not a
counterexample to `(LQ)` itself: the full bank has ten slots.

### 1.2 First failure of every downward-only family

Suppose a construction only assigns a hard root `h` to healed splitless
roots `e<=h`.  At `Y=174`, the exact source set is

```text
54, 74, 114, 144, 174.
```

The 17 members of `D(696)` with root at most `174` are

```text
6, 8, 18, 20, 30, 38, 48, 56, 60,
66, 78, 92, 110, 120, 126, 146, 168.
```

The eight fresh upper roots are

```text
182, 198, 200, 210, 228, 246, 306, 308.
```

Thus the full inequality has margin

\[
                    2\cdot25-7\cdot5=15,
\]

but every downward-only family has capacity

\[
                    2\cdot17-7\cdot5=-1.              \tag{5}
\]

This is the first downward-capacity failure in the exact trajectory.  It
rules out every construction assembled solely from shadows bounded by their
source, independently of how those shadows are selected.

### 1.3 Tight finite Hall instance

At `Y=2064`, the exact data are

```text
|H_Y|                         = 87
|S_Y| = D(8256)               = 309
roots e<=Y                    = 209
roots Y<e<=2Y                 = 100
total slot margin             = 2*309-7*87 = 9.
```

The complete root lists, all first-death labels, all generating pairs, all
87 prefix margins, and a 609-slot greedy matching are in
`C98_lower_quarter_1e6.json`.

The downward bank supplies only `418` of the `609` required slots.  The
fresh bank must supply at least `191`, so at least

\[
                         \lceil191/2\rceil=96           \tag{6}
\]

of its 100 distinct roots are necessary.  The saved greedy matching attains
this minimum and leaves exactly nine slots unused.

## 2. Why `7/2` appears

Write

\[
 B=A_H(\lfloor X/4\rfloor).
\]

Assume the upper comparison `A_H(X)<=D(X)+B+C` and a lower comparison
`D(X)>=cB`, where `c>0`.  Then

\[
 A_H(X)\le D(X)+{D(X)\over c}+C,
\]

and therefore

\[
 D(X)\ge {c\over c+1}\bigl(A_H(X)-C\bigr).            \tag{7}
\]

The C91 contraction needs a coefficient strictly larger than `3/4`.
Equation (7) crosses that threshold exactly when `c>3`.  If the lower
comparison is encoded with two integral copies of every healed root, its
rates are half-integers; the first admissible rate is

\[
                              c={7\over2}.              \tag{8}
\]

With `C=1`, substituting (8) in (7) gives (3).  Hence the numbers `7` and
`2` express the smallest two-copy integer weighting that clears the
contraction threshold.  They do not arise from seven canonical descendants
of one hard root; Section 1.1 exactly falsifies such a support-local reading.

## 3. Uniform quarter-shell lemma

Put `U(n)=2n-1`.  Let

* `D_0(Y)` count the splitless roots `e<=Y` healed through `4Y`;
* `F(Y)` count the splitless roots `Y<e<=2Y` for which `U(e)` is generated.

### Lemma C98.1 (fresh one-step decomposition)

For every integer `Y>=1`,

\[
                         D(4Y)=D_0(Y)+F(Y).             \tag{9}
\]

In particular no root exceeding `2Y` contributes to `D(4Y)`, and every
contributor in `(Y,2Y]` heals at depth exactly one.

### Proof

A structural splitless root is a hole, so its first generated chain member
has the form `U^j(e)` with `j>=1`.  If `U^j(e)<=4Y`, then

\[
                         U(e)=2e-1\le4Y,
\]

which gives `e<=2Y`.  This partitions every root counted by `D(4Y)` into
the two ranges in (9).

If `Y<e<=2Y`, then `e>=Y+1` and

\[
                         U^2(e)=4e-3\ge4Y+1.
\]

Thus the only positive-depth chain member visible through `4Y` is `U(e)`.
The root contributes exactly when that member is generated, proving (9).
QED.

The lower inequality is therefore exactly

\[
             2D_0(Y)+2F(Y)\ge7A_H(Y).                 \tag{10}
\]

At `Y=2064`, the two terms on the left are `418` and `200`; (10) has only
nine units of slack.  This is why the fresh one-step term cannot be treated
as an optional correction.

## 4. Uniform Hall equivalence

For `X=4Y+r`, `0<=r<=3`, the right side of `(LQ)` is `7A_H(Y)` and
`D(X)>=D(4Y)`.  Hence `(LQ)` for every integer `X` is equivalent to

\[
                 2D(4Y)\ge7A_H(Y)\quad(Y\ge0).         \tag{11}
\]

For fixed `Y`, define the bipartite slot graph

\[
 \mathcal H_Y=H_Y\times\{1,\ldots,7\},
 \qquad
 \mathcal S_Y=S_Y\times\{0,1\},                       \tag{12}
\]

and join `(h,i)` to `(e,j)` when `e<=2h`.

### Theorem C98.2 (quarter-shell Hall equivalence)

The inequalities

\[
                 2D(4z)\ge7A_H(z)\quad(1\le z\le Y)   \tag{13}
\]

imply that `H_Y x {1,...,7}` has a matching saturating every left slot.
Conversely, a left-saturating matching at `Y` implies the member `z=Y` of
(13).

### Proof

Let `T` be any subset of the left slots and let `R` be its set of underlying
hard roots.  If `R` is empty there is nothing to prove.  Otherwise put
`h=max R`.

Every member of `R` is persistent through `Y`, hence also through the
smaller cutoff `h`.  Since all its roots are at most `h`,

\[
                             |R|\le A_H(h).             \tag{14}
\]

Every splitless root healed through `4h` is healed through `4Y`.  Moreover,
if its first generated iterate is `U^j(e)<=4h`, then `j>=1` and
`2e-1<=4h`, so `e<=2h`.  Therefore both copies of every member of `D(4h)`
belong to the neighborhood of `T`.  By (13),

\[
 |N(T)|\ge2D(4h)\ge7A_H(h)\ge7|R|\ge|T|.              \tag{15}
\]

Hall's theorem gives a matching saturating all left slots.

Conversely, a saturated graph uses `7A_H(Y)` distinct slots from a right
side of size `2D(4Y)`, giving the `z=Y` inequality.  QED.

Because the neighborhoods are nested by source size, the matching can be
constructed greedily: sort sources and supply slots increasingly and give
each source the next seven unused slots.  The prefix inequalities in (15)
ensure that the seventh new slot never exceeds `2h`.  The JSON certificate
does exactly this at `Y=2064`.

The theorem supplies a precise disjoint-family formulation, but also a
precise obstruction: proving its Hall conditions is the original lower
inequality at all smaller scales.  A matching search alone cannot bypass
the closure arithmetic.

## 5. Exact computation and independent replay

`C98_lower_quarter_hall.py` uses an SPF table, ascending closure, and exact
integer event accounting.  It checks every `Y<=250000`, stores all labels
needed for the three witnesses, and records:

```text
lower-quarter failures                 0
minimum positive margin                3 at Y=54
minimum D(4Y)/A_H(Y)                   103/29 at Y=2064
first downward-capacity failure        Y=174
tight Hall instance                    609 used, 9 unused slots
```

`C98_lower_quarter_verify.py` imports no scanner code.  It enumerates factor
pairs by trial division and evaluates closure membership recursively.  It
reconstructs the complete sets at `Y=54,174,2064`, verifies every saved
first death and generating pair at `Y=174`, and checks every edge and slot
of the 609-slot matching.  Normal and `python -O` outputs are byte-identical.

Reproduction:

```powershell
python problems/424/compute/wave5/C98_lower_quarter_hall.py `
  --limit 1000000 --hall-cutoff 2064 `
  --output problems/424/compute/wave5/C98_lower_quarter_1e6.json

python problems/424/compute/wave5/C98_lower_quarter_verify.py `
  --claim problems/424/compute/wave5/C98_lower_quarter_1e6.json `
  --output problems/424/compute/wave5/C98_lower_quarter_verify_1e6.json
```

SHA-256:

```text
4EA88456F79A72E87144FDAB58B6F7ABE83EE6DA388EF9C6D1F7DB95862CCED9  C98_lower_quarter_hall.py
AE98535C4E76853C14A3D2427C143A4D2355D2F7D73BB09EFE38F79D8D9E6906  C98_lower_quarter_verify.py
584BE9C113A4590779AC92C87323746D53655EF580A8B661B49574F5BEDDCE38  C98_lower_quarter_1e6.json
52C1479790890C7DC3C1DD371A262406E3867ECB71A46CA5D0B9EDAC876D58CE  C98_lower_quarter_verify_1e6.json
```

## 6. Scope

C98 does not repeat C95's upper-event amortization or C96's broad
asymptotic equivalence.  It returns:

1. a proved uniform Hall formulation specific to the lower quarter gate;
2. a proved fresh one-step decomposition of its supply;
3. an exact support-local falsifier at the first hard root;
4. an exact falsifier to every downward-only family; and
5. a root-labelled near-saturated disjoint family at `Y=2064`.

The remaining theorem-strength frontier is an all-scale lower bound for the
fresh closure events `F(Y)` in (9).  No resolution of Problem 424 is claimed.
