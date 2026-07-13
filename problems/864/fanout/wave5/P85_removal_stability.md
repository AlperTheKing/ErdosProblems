# P85: removal and additive-stability audit for the fold hypergraph

## Verdict

The removal/stability lane does **not** close the reflected-center frontier.
It also does not produce an infinite counterfamily.

There are three rigorous conclusions.

1. P82 extracts the direct consequence supplied by uncoloured graph removal:
   `C_S >= epsilon*p^2` forces `T_F >= eta(epsilon)*p^3`.
2. The constant-parameter Balog--Szemeredi--Gowers hypotheses are
   incompatible with the exact Sidon fibres.  Every subset of `B` has
   quadratic doubling and only quadratic second energy, and every dense fold
   projection has a quadratic, not linear, restricted sumset.
3. Dependent random choice and corners theorems return incidence patterns in
   the rank-labelled fold graph.  Those patterns do not retain the integer
   endpoint phase `H-b`.  The P75 ruler is an exact countermodel to every
   pointwise implication from a loose triangle, a rank corner, or a projected
   `K_{2,2}` to a forbidden `B+B+B` representation.

The surviving target is therefore genuinely phase-sensitive.  One must prove
that a *positive density* of the P82 configurations, together with positive
defect, forces the single coefficient

\[
                 r_{B+B+B}(H-b)>0,                    \tag{1}
\]

or prove an equivalent joint fold/Fourier estimate.  None of the four general
tools tested below supplies the distinguished integer `H-b`.

## 1. Setup

Use the notation of P82.  Thus

\[
 B\subseteq[0,h-1],\quad |B|=p,\quad H=h-1=\max B,
 \quad b\in\{1,2\},                                  \tag{2}
\]

`B` is integer Sidon with diagonals, the defect is positive, and

\[
 \Delta^+(B)\cap(B+B+b)=\varnothing .                \tag{3}
\]

Every fold has the unique ordered form

\[
                 a+c+h=u+v,\qquad a\le c<u\le v,    \tag{4}
\]

and gives the hyperedge `(a_A,c_C,u_U)` of the linear tripartite
3-graph `H_F`.  A loose triangle consists of

\[
\begin{array}{rcl}
 a+c+h&=&r+s,\\
 a+z+h&=&u+w,\\
 x+c+h&=&u+y.                                        \tag{5}
\end{array}
\]

Equivalently, the full literal hole says

\[
                   r_{B+B+B}(w-b)=0\qquad(w\in B).   \tag{6a}
\]

In particular, it implies the endpoint instance

\[
                   r_{B+B+B}(H-b)=0.                 \tag{6}
\]

For `b=1`, reflecting the high pair in (4) gives

\[
              a+c+(H-u)+(H-v)=H-1.                  \tag{7}
\]

Thus folds are representations of `H-1` by two points of `B` and two
points of `H-B`; the hole forbids a representation by three points of `B`.
For `b=2`, (7) and the forbidden target differ by one.

## 2. What removal does, and where it stops

P82.2 applies graph removal to the tripartite shadow `G_F`.  Since the
canonical fold triangles are edge-disjoint, a quadratic fold count makes
`G_F` a constant distance from triangle-free and hence produces a cubic
number of shadow triangles.  After deleting the canonical triangles, these
are exactly the loose triangles (5).

Applying dense hypergraph removal directly to `H_F` gives no stronger input.
The 3-graph has `3p` vertices but at most `p(p+1)/2` edges, so its density
among the `p^3` possible tripartite triples is `O(1/p)`.  The only dense
object is the shadow graph, and its removal conclusion is precisely P82.2.

Subtracting equations in (5) gives, among two other analogous identities,

\[
                         a+z+y=x+c+w.                 \tag{8}
\]

This is a nontrivial equal-three-sum relation.  Indeed, `a` and `x` are the
respective minima of the two triples.  If their multisets were equal, then
`a=x`; after cancellation, either `z=c,y=w`, which makes the first two folds
equal because `(a,c)` determines a fold, or `z=w,y=c`, which contradicts
`z<u<=w`.

Conversely, a fixed unordered collision of two three-multisets supports at
most `2(3!)^2=72` role assignments in (8).  Therefore

\[
 T_F\ge\eta p^3
 \quad\Longrightarrow\quad
 \#\{\{L,R\}:L,R\in\tbinom{B}{3}_{\rm multi},
          L\ne R,\ \sum L=\sum R\}\ge {\eta p^3\over72}.       \tag{9}
\]

This is the strongest phase-free additive consequence needed here.  The
target value `H-b` has disappeared from (8)--(9).  Removal and its standard
stability refinements count translation-invariant configurations; they do
not select one coefficient of `1_B*1_B*1_B`.

As a purely incidence-level model, for every finite abelian group `G` the
tripartite hypergraph

\[
            \{(x_A,y_C,z_U):x+y+z=0\}                \tag{10}
\]

is linear, has `|G|^2` edges, and has `|G|^3-|G|^2` loose shadow triangles.
This is not an admissible integer-ruler counterfamily; it records exactly
why linearity and cubic loose-triangle density alone contain no endpoint
phase.

## 3. Exact BSG obstruction

### Lemma P85.1 (Sidon energy rigidity)

For every `X subseteq B`, with `m=|X|`,

\[
 |X+X|={m(m+1)\over2},\qquad
 |X-X|=m(m-1)+1,qquad
 E_+(X)=2m^2-m.                                      \tag{11}
\]

Here `E_+(X)` is the ordered number of solutions of
`x_1+x_2=x_3+x_4`.

### Proof

Every unordered sum is unique.  Its ordered multiplicity is one on the `m`
diagonal sums and two on the `m(m-1)/2` off-diagonal sums, giving

\[
 E_+(X)=m+4\binom m2=2m^2-m.
\]

Every positive difference is also unique, and adjoining its negative and
zero gives the difference-set formula.  QED.

The energy-form BSG theorem starts at

\[
                         E_+(B)\ge p^3/K.             \tag{12}
\]

By (11), its effective parameter is

\[
                         K\ge {p^3\over2p^2-p}>p/2.   \tag{13}
\]

It is therefore not a constant-parameter inverse theorem here.  More
decisively, (11) shows that no unbounded subset of `B` has constant doubling,
so any argument claiming that (9) yields a linear-sized constant-doubling
subset has asserted a false bridge.

The graph form of BSG also fails at its restricted-sum premise.  In each of
the three P82 projections `(a,c)`, `(a,u)`, and `(c,u)`, the projected pairs
are distinct unordered pairs of elements of `B`.  Hence Sidonicity gives

\[
            |B+_{\Gamma}B|=|\Gamma|=C_S.             \tag{14}
\]

The same statement holds for positive-difference labels.  If
`C_S>=epsilon*p^2`, the restricted sumset in (14) is quadratic, whereas
graph BSG requires a restricted sumset of size `O_epsilon(p)` to return a
linear-sized structured subset.

One may instead apply BSG to the full sum support `S=B+B`.  The folds give
one popular difference,

\[
                         r_{S-S}(h)=C_S.              \tag{15}
\]

Its contribution `C_S^2=Omega(p^4)` to `E_+(S)` is still a factor `p^2`
below the constant-parameter threshold `|S|^3=Theta(p^6)`.  Thus the single
fold spike does not trigger BSG on `S` either.

## 4. DRC and corners

Under the hypothetical bound `C_S>=epsilon*p^2`, each of the three
projections of `H_F` is a dense bipartite graph.  Dependent random choice
therefore produces, for every fixed `r` and sufficiently large `p`, large
common-neighbour sets and in particular projected `K_{r,r}` subgraphs.
This conclusion only records which rank-labelled pairs extend to folds.
It does not retain the fourth fold variable `v`, its reflection `H-v`, or
the target `H-b`.  A new arithmetic lemma converting such a grid to (1)
would be needed; DRC itself contains no such conversion.

The phase erasure can be made exact.  Given any endpoint-normalized Sidon
set `B_0 subseteq [0,h_0-1]` and any integer `q>=2`, put

\[
 B_q=qB_0+(q-1),\qquad h_q=qh_0.                     \tag{16}
\]

Then `max B_q=h_q-1`, `B_q` is Sidon, and (16) preserves every fold and
therefore the complete unlabelled hypergraph `H_F`.  Also every difference
of `B_q` is `0 mod q`, while every member of `B_q+B_q+1` is `-1 mod q`.
Consequently the full `b=1` literal hole is automatic.  The defect becomes

\[
 {3p^2-p+2\over2}-qh_0.                              \tag{17}
\]

Equation (17) explains both the force and the limitation of this example:
incidence conclusions and the literal hole can coexist exactly, but a
fixed finite seed cannot be scaled indefinitely while retaining positive
defect.  Thus (16) is a barrier to phase-blind DRC, not an asymptotic
counterfamily.

The corners theorem has a separate scale obstruction.  In the integer
value grid `[0,h-1]^2`, the fold projection has at most `O(p^2)` points.
Sidonicity gives `h-1>=p(p-1)/2`, so its grid density is `O(p^{-2})`, not a
fixed positive density.  In the rank grid `[p]^2`, a hypothetical quadratic
fold count does have fixed density and corners follow.  But a rank corner

\[
                  (i,j),\ (i+d,j),\ (i,j+d)           \tag{18}
\]

says nothing about the integer differences between the corresponding marks
of `B`.  It cannot select `H-b` without a new distribution theorem for the
mark map `i -> b_i`.

## 5. Exact admissible countermodel

The P75 ruler

```text
B = {3,5,69,169,211,223,251,329,373,403,409,501,505,
     519,631,639,689,715,775,863,883,915,931,953,977,987}
(p,h,b,delta) = (26,988,1,14)
```

is Sidon, endpoint-normalized, has positive defect, and satisfies the full
literal hole.  Exact reconstruction gives

\[
 C_S=51,\qquad T_F=25,
 \qquad r_{B+B+B}(986)=0.                             \tag{19}
\]

The same exact audit gives

\[
\begin{array}{c|r}
\text{quantity}&\text{value}\\ \hline
E_+(B)&1326=2p^2-p\\
E_3(B)=\sum_t r_{B+B+B}(t)^2&340766\\
\text{trivial ordered part of }E_3&99476\\
\text{nontrivial ordered part of }E_3&241290\\
\text{unordered unequal three-sum pairs}&4106\\
\text{distinct primary collisions from the 25 loose triangles}&19
\end{array}                                           \tag{20}
\]

Thus even a large supply of nontrivial three-sum collisions does not fill
the endpoint coefficient.  In the three projections `(a,c)`, `(a,u)`, and
`(c,u)`, the maximum balanced biclique order is exactly two.  Their rank-grid
corner counts are respectively

\[
                              14,\quad12,\quad10.      \tag{21}
\]

Equations (19)--(21) are exact counterexamples to the pointwise statements

```text
loose triangle       => endpoint three-sum representation,
projected K_2,2      => endpoint three-sum representation,
rank-grid corner     => endpoint three-sum representation.
```

They do not falsify a positive-density asymptotic theorem.

An exact scan of the 134 endpoint-normalized, positive-defect literal-hole
rows in `compute/p46/carry_statistics.json` found loose triangles in 88
rows.  The largest absolute count was

\[
 (p,h,b,C_S,T_F)=(152,29747,1,256,144),               \tag{22}
\]

and the largest ratio in that stored corpus was `T_F/p^3=1/343`, at `p=7`.
These are finite corpus facts only.  In particular, (22) proves neither
`T_F=o(p^3)` nor an infinite positive-density family.

The load-bearing countermodel checks are independently reproduced by

```powershell
python -B problems/864/compute/p75/verify_hard_fold_counterexample.py
python -B problems/864/compute/p82/verify_p75_loose_triangles.py
```

All additional counts above used integer counters.  For the corpus scan,
write `AC`, `AU`, and `CU` for the three projected edge sets and let
`N_AU(a)={u:(a,u) in AU}` and `N_CU(c)={u:(c,u) in CU}`.  The exact formula

\[
 T_F=\sum_{(a,c)\in AC}|N_{AU}(a)\cap N_{CU}(c)|-C_S                 \tag{22a}
\]

reconstructs the scan without floating-point arithmetic or randomized
sampling.

## 6. The surviving phase lemma

Let `C=H-B`.  Replace every fold (4) by its four-variable record

\[
 {\cal F}=\{(a,c,\alpha,\beta)\in B^2\times C^2:
                    a\le c,\ \alpha\le\beta,
                    a+c+\alpha+\beta=H-1\}.          \tag{23}
\]

The map `(a,c,u,v) -> (a,c,H-v,H-u)` is a bijection from the folds
to `F`, so `|F|=C_S`.

The P82 shadow forgets `beta` and then counts loose triangles.  Any removal
or stability completion must instead prove a statement of the following
form.

> **Open phase-density lemma.**  For every `eta>0`, all sufficiently large
> data satisfying (2)--(3), positive defect, and
> `T_F>=eta*p^3` have `r_{B+B+B}(H-b)>0`.

By P82.2, this lemma implies `C_S=o(p^2)`, and P77.1 then supplies the desired
joint fold/Fourier reduction.  P75 shows that one loose triangle, any fixed
rank corner, and a projected `K_{2,2}` are all insufficient premises.  The
positive-density quantifier and the integer phase in (23) cannot be removed.

## 7. Prior art and claim boundary

The removal input is the standard graph removal lemma; see Conlon--Fox,
[*Graph removal lemmas*](https://arxiv.org/abs/1211.3487).  The energy
threshold used above is the standard BSG threshold; a modern sharp form is
Reiher--Schoen, [*Note on the Theorem of Balog, Szemeredi, and
Gowers*](https://arxiv.org/abs/2308.10245).  The DRC conclusion used here is
described by Fox--Sudakov, [*Dependent Random
Choice*](https://arxiv.org/abs/0909.3271).  The corners theorem applies to
fixed-density subsets of a coordinate grid; its mismatch with the value and
rank grids is the scale/phase calculation in Section 4.

P85 proves the rigidity and obstruction lemmas (9), (11), (14), and
(16)--(18), and records the exact audits (19)--(22).  It does not prove the
open phase-density lemma and does not claim an infinite counterfamily.
