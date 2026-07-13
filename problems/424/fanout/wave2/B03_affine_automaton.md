# B03: affine residue automata

## Verdict

The density of the affine orbit (S) is **not decided here**.  The requested
finite-residue exact-decoding route has, however, a rigorous negative answer
in its standard global form:

> No finite automaton whose states are residue classes and whose
> unique-decoding certificate is disjointness of the incoming affine images
> of those whole classes can have weighted spectral radius at least (1) at
> exponent (1).

In fact every such automaton has radius strictly below (1), and its orbit
language has counting function (O(X^sigma)) for some (sigma<1).  Thus no
positive-density proof for (S) can come from this class of exact renewal
certificates.  Language-specific uniqueness that holds only on the generated
positive orbit, rather than on whole residue classes, is not ruled out.

Code: [`affine_automaton_search.py`](../../compute/wave2/B03/affine_automaton_search.py).
Tests: [`test_affine_automaton_search.py`](../../compute/wave2/B03/test_affine_automaton_search.py).

## 1. Exact reduction and distinctness

Write (T_k(x)=kx-1), for (k\in\{2,3,5\}), and require (x\ne k).
The only allowed exits from the three seeds are

\[
2\xrightarrow{3}5,\quad 2\xrightarrow{5}9,
\qquad
3\xrightarrow{2}5,\quad 3\xrightarrow{5}14,
\qquad
5\xrightarrow{2}9,\quad 5\xrightarrow{3}14.
\]

Every value reached from (9) or (14) is greater than (5), and every
(T_k) strictly increases such a value.  Consequently all later operations
have distinct inputs, and exactly

\[
S=\{2,3,5\}\mathbin\cup \mathcal O(9)\mathbin\cup\mathcal O(14),       \tag{1}
\]

where the two orbits on the right allow every word over ({2,3,5}).
This removes the (x\ne k) side condition without dropping it.

For a nonempty word (w=(k_1,\ldots,k_m)), applied from left to right, write

\[
F_w=T_{k_m}\circ\cdots\circ T_{k_1},\qquad
F_w(x)=a_wx-b_w.
\]

Induction using

\[
(a,b)\longmapsto(ka,kb+1)
\]

gives the exact invariant

\[
a_w\ge2,\qquad 1\le b_w<a_w.                         \tag{2}
\]

The strict upper bound in (2) is the obstruction below.

## 2. Certificate model

Fix a modulus (M).  A state is a full residue class

\[
C_r=r+M\mathbb Z.
\]

An edge (e:r\to s) is labelled by a nonempty block (w_e) and must satisfy
(F_{w_e}(C_r)\subseteq C_s).  To decode the last edge from the output
residue, require the sets

\[
F_{w_e}(C_r),\qquad e:r\to s,
\]

to be pairwise disjoint for each fixed target state (s).  These sets are
arithmetic progressions of density (1/(a_eM)), where (a_e=a_{w_e}).

The weighted transition matrix is

\[
A(t)_{rs}=\sum_{e:r\to s}a_e^{-t}.                    \tag{3}
\]

Splitting a state that consists of several residues into singleton residue
states preserves this model and its path language, so using singleton classes
does not lose the usual finite residue-state constructions.

## 3. Strict subcriticality theorem

**Theorem.** Every finite globally residue-decodable block automaton defined
above satisfies

\[
\rho(A(1))<1.                                          \tag{4}
\]

**Proof.** For each target (s), disjointness inside (C_s) and arithmetic
progression densities give

\[
\sum_r A(1)_{rs}\le1.                                  \tag{5}
\]

Thus (A(1)^T) is substochastic and (ho(A(1))\le1).

Suppose equality held.  The elementary recurrent-class lemma for a finite
substochastic matrix then supplies a nonempty set (K) of states such that,
for every (s\in K), the incoming edges from states in (K) have total
weight exactly (1).  Their disjoint periodic images therefore have the same
density as (C_s).  A periodic subset of (C_s) with full relative density is
all of (C_s).  Hence, for

\[
U=\bigcup_{r\in K}C_r,
\]

every (y\in U) has a predecessor (x\in U) and a nonempty block (w) with

\[
y=F_w(x)=a_wx-b_w.                                     \tag{6}
\]

First, (0\notin U): otherwise (6) and (2) would give
(x=b_w/a_w\in(0,1)), not an integer.  The nonempty periodic set (U)
contains negative integers, so let (y) be its largest negative integer and
use (6).  If (x\ge1), then (2) gives
(a_wx-b_w\ge a_w-b_w\ge1), impossible.  The case (x=0) was excluded.
Thus (x\le-1), but then

\[
y=a_wx-b_w<x<0.
\]

This makes (x\in U) a negative integer larger than the chosen (y), a
contradiction.  Equality is impossible, proving (4).  \(\square\)

The negative-integer step is not a heuristic extension of the orbit.  Whole
residue classes are two-sided periodic sets, and global image disjointness is
precisely what makes residue decoding an exact arithmetic certificate.

## 4. Exact counting consequence

Because the edge set is finite, (A(t)) is continuous in (t).  From (4)
there is a (sigma<1), sufficiently close to (1), with
(ho(A(\sigma))<1).  Hence the exact path-weight sum

\[
\sum_{P} a(P)^{-\sigma}
\]

converges, by the finite matrix geometric series; (a(P)) is the product of
the slopes on path (P).

For (x_0\ge2), one letter satisfies

\[
T_k(x)-1=k(x-1)+(k-2)\ge k(x-1).
\]

Therefore a path ending at (y\le X) has

\[
a(P)(x_0-1)\le y-1\le X-1,
\]

and in particular (a(P)\le X-1).  It follows exactly that

\[
\#\{P:F_P(x_0)\le X\}
\le (X-1)^\sigma\sum_P a(P)^{-\sigma}
=O(X^\sigma).                                          \tag{7}
\]

Unique decoding identifies paths with output values, so (7) proves zero
density for every sublanguage certified by this model.  This is the requested
renewal/counting check, but on the negative side: the critical case cannot
occur.

## 5. Exact finite searches

The program performs three integer-only replays.

1. For a one-letter decoder modulo (30), an output residue (q) may be
   colored only by a (k\in\{2,3,5\}) dividing (q+1).  There are (22)
   colorable residues, (8) ambiguous residues, and exactly (384) policies.
   For a target colored (k), exponent-one column mass is (1) only when all
   (k) solutions of (kr-1\equiv q\pmod {30}) stay in the recurrent set.
   Exact greatest-fixed-point deletion leaves an empty core for all (384)
   policies; (24) die in three rounds and (360) in four rounds.

2. Natural exact-cover trees were searched modulo (30).  A node (t\pmod d)
   may be a block leaf of slope (d), or split into its (2), (3), or (5)
   children.  Allowing every block with at most (c) occurrences of each
   letter gives the same exact fixed-point sizes

   \[
   30,22,15,7,0
   \]

   for each (c=1,2,3).  This bounded search is diagnostic; the theorem, not
   the cutoff, rules out all finite global residue decoders.

3. The direct orbit from the two admissible roots in (1) reproduces

   \[
   |S\cap[1,X]|=212,2061,20192
   \]

   at (X=10^3,10^4,10^5), respectively.

Reproduce from `problems/424/compute/wave2/B03`:

```powershell
python -m unittest -v
python affine_automaton_search.py --modulus 30 --max-block-cap 3 --orbit-limit 100000
```

The test run reports four passing tests.  The standalone run checks (3279)
block coefficient invariants in addition to the searches above.

## 6. Boundary of the result

The theorem does **not** prove that (S) has zero lower density.  It uses
disjointness of affine images of entire residue classes.  A finite automaton
might conceivably be unambiguous only on paths reachable from (9) and (14),
even though the corresponding full arithmetic progressions intersect; the
column-density argument would then not apply.  Likewise the census through
(10^9), including its declining ratios, supplies no limiting-density bound.

Thus the verified conclusion is an obstruction: a critical finite residue
renewal proof must use a weaker, orbit-relative notion of uniqueness, or the
density question for (S) must be attacked by a method that controls
collisions without selecting globally disjoint residue images.
