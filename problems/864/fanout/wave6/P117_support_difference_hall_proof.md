# P117: support--difference Hall, closed cores, and the arm-cycle frontier

## Verdict

I did not obtain a complete proof or an arithmetic falsifier to P113.  I
did obtain a strictly more structured lemma tree which reduces P113 to one
closed-core counting statement.  The reduction uses all three supporting
folds and all three represented pairwise phase differences; it does not pass
through the false abstract STS or outer-span statements.

The new exact proof frontier is the following.

> **Closed-core cycle-excess lemma.**  In a family of loose triangles in
> which every occurring supporting fold and every occurring represented
> phase-difference label occurs at least twice, the total positive cycle
> excess of the P108 arm graphs is at most the number of supporting folds
> which occur only as base folds.

This statement is equivalent to saying that such a closed core has at most
as many triangles as supporting folds.  Together with the private-resource
peeling lemma proved below, it implies the full P113 Hall inequality.

An exact CP-SAT optimization found no violation of this closed-core lemma on
the P94, P106, or any of the 20 dense P110 dimension-falsifier rows.  On all
these rows the stronger assertion that the maximal closed core matches to
its supporting folds also holds.  This is finite evidence, not a proof.

## 1. The three actual mark triangles

Let a loose triangle have the P83 normal form

\[
\begin{array}{lll}
 F_0=(a,c,u+R,s),&F_Z=(a,c+Z,u,s+R+Z),
 &F_X=(a+X,c,u,s+R+X).
\end{array}                                                    \tag{1}
\]

Write

\[
 q_0=a+c,\qquad q_Z=a+c+Z,\qquad q_X=a+c+X              \tag{2}
\]

for the three fold phases.  Integer Sidonicity gives a unique unordered
pair of marks representing each positive difference.  The three P113
difference resources therefore have the following *unique* mark-edge
representations:

\[
\begin{array}{c|c}
 |q_Z-q_0|=|Z|&\{c,c+Z\},\\
 |q_X-q_0|=|X|&\{a,a+X\},\\
 |q_Z-q_X|=|Z-X|&\{s+R+X,s+R+Z\}.
\end{array}                                                   \tag{3}
\]

Every fold is likewise represented uniquely by its low pair and by its
high pair.  Consequently (1) contains three genuine graph triangles on the
mark set `B`:

\[
\begin{array}{c|ccc}
 A\text{-cycle}&F_0:[a,c]&F_Z:[a,c+Z]&D_Z:[c,c+Z],\\
 C\text{-cycle}&F_0:[a,c]&F_X:[a+X,c]&D_X:[a,a+X],\\
 U\text{-cycle}&F_Z:[u,s+R+Z]&F_X:[u,s+R+X]
                 &D_{Z-X}:[s+R+X,s+R+Z].
\end{array}                                                   \tag{4}
\]

Here the brackets denote unordered mark edges; signs may be restored by
orienting every edge from its smaller endpoint to its larger endpoint.
This proves that P113 is not merely a statement about triples of integers
and their spans.  Its three difference resources are the closing edges of
three coherently factorized mark triangles.  This factorization is exactly
the information missing from P114's abstract ordered-triple model.

## 2. Private-resource peeling

For a family `X` of loose triangles let

\[
 {cal N}(X)={\cal F}(X)\mathbin{\dot\cup}{\cal D}(X)             \tag{5}
\]

be the disjoint union of its supporting folds and represented positive
difference labels.  A resource is *private* in `X` if it occurs in exactly
one triangle of `X`.

### Lemma P117.1 (closed-core reduction)

Assume that every nonempty family `Y` having no private resource satisfies

\[
                         |Y|\le |{\cal F}(Y)|.          \tag{6}
\]

Then every family `X` satisfies the P113 Hall inequality

\[
                         |X|\le |{\cal F}(X)|+|{\cal D}(X)|.
                                                               \tag{7}
\]

#### Proof

Starting with `X`, repeatedly choose a private resource, record it, and
delete its unique incident triangle.  Suppose `k` triangles are deleted and
the residual family is `Y`.  Recorded resources are pairwise distinct:
after its incident triangle is deleted, a recorded resource never occurs
again.  They are also disjoint from `N(Y)`.  If `Y` is empty, (7) follows
immediately.  Otherwise `Y` has no private resource, so (6) gives

\[
 |X|=k+|Y|\le k+|{\cal F}(Y)|\le |{\cal N}(X)|.
\]

This is (7).  QED.

Thus P113 is reduced to a statement in which **every one of the six actual
resources of each triangle is repeated**.  This is substantially narrower
than arbitrary Hall: all tree-like parts of the incidence system disappear
before any arithmetic argument is needed.

Call the terminal family `Y` the six-resource closed core.  If
`d_Y(F)` is the number of triangles of `Y` containing a fold `F`, then every
occurring fold has `d_Y(F)>=2`, and

\[
                         3|Y|=\sum_F d_Y(F).            \tag{8}
\]

Consequently (6) is equivalent to the discharging inequality

\[
 \sum_{F:d_Y(F)>3}(d_Y(F)-3)
 \le \#\{F:d_Y(F)=2\}.                                \tag{9}
\]

This is one concrete local form of the remaining core theorem.  In
particular, a closed core of maximum fold degree at most three is already
settled.

## 3. Exact arm-graph form of the core theorem

Use the P108 arm graphs.  For a fixed shared high endpoint `u`, their
vertices are folds

\[
             F_i=(a_i,c_i,u,v_i),\qquad
             v_i=a_i+c_i+h-u,                          \tag{10}
\]

and a loose triangle is the directed arc `i -> j` whose arm folds are
`F_Z=F_i`, `F_X=F_j` and whose base fold has low pair `(a_i,c_j)`.
Let `G_u(Y)` be the graph induced by the triangles of the closed core, after
discarding isolated vertices, and put

\[
             e_u=|E(G_u(Y))|,\qquad n_u=|V(G_u(Y))|.   \tag{11}
\]

Every fold has a unique first high endpoint, so the arm-vertex sets for
different `u` are disjoint.  Let `B_0(Y)` be the supporting folds of `Y`
which never occur as either arm fold.  Since every triangle is exactly one
arm arc,

\[
 |Y|=\sum_u e_u,qquad
 |{\cal F}(Y)|=|B_0(Y)|+\sum_u n_u.                   \tag{12}
\]

Therefore (6) is *exactly* the following scalar inequality:

\[
 \boxed{\displaystyle
       \sum_u(e_u-n_u)\le |B_0(Y)|.}                  \tag{CE117}
\]

Only arm components with more arcs than vertices contribute positively.
For an undirected connected component with `e` arcs and `n` vertices,
`e-n` is its cycle-space dimension minus one.  Thus CE117 says that every
independent arm cycle beyond the first is paid by a distinct fold which is
used only as a base.  P108.2 supplies the exact cancellation on each
directed cycle,

\[
                 \sum_{i\to j\text{ on }C}w_{ij}
                 =\sum_{i\in C}v_i.                  \tag{13}
\]

The missing proof is now sharply located: combine (13) with the repeated
difference-edge condition from (3)--(4) to inject excess arm cycles into
`B_0(Y)`.  No interval Hall statement, literal-hole assumption, positive
defect, or asymptotic estimate is present in CE117.

### Lemma tree

The exact dependency tree is

\[
\begin{array}{c}
 \text{P83 normal form + Sidonicity}\\
 \Downarrow\\
 \text{three factorized mark cycles (4)}\\
 \Downarrow\\
 \text{private-resource peeling, P117.1}\\
 \Downarrow\\
 \text{CE117 for every six-resource closed core}\\
 \Downarrow\\
 \text{P113 Hall}\\
 \Downarrow\\
 T_F\le C_S+|\Delta^+(B)|=O(p^2)\\
 \Downarrow\\
 \text{P82 closes the positive-density fold alternative.}
\end{array}                                                     \tag{14}
\]

Only CE117 is unproved.

## 4. An actual arithmetic falsifier to outer-support plus span

P114 gave an abstract counterexample to keeping only the two outer phase
vertices and the span.  The following seven-mark endpoint fold system shows
that this weakening already fails inside the actual arithmetic class:

\[
 B=\{0,9,12,20,22,26,27\},\qquad h=28.                \tag{15}
\]

It is integer Sidon.  Its six canonical folds are

\[
\begin{split}
 &(0,12,20,20),\ (0,20,22,26),\ (0,26,27,27),\\
 &(9,9,20,26),\ (9,12,22,27),\ (12,12,26,26).
\end{split}                                                   \tag{16}
\]

There are two loose triangles.  Their support-fold phase triples are

\[
                  (12,20,21),\qquad(21,18,12).         \tag{17}
\]

Both have the same outer supporting folds, of phases `12` and `21`, and
the same span difference `9`.  Hence their outer-support-plus-span rows are
identical and have rank one.  The full P113 resources separate them: their
three difference sets are respectively

\[
                       \{1,8,9\},\qquad\{3,6,9\},      \tag{18}
\]

and their middle supporting folds are distinct.  Thus any proof must retain
the middle support or the two shorter differences (and in general all
three symmetric choices), exactly as required in the assignment.

This falsifier also rules out the otherwise attractive matrix row

\[
              e_{F_{\min}}-e_{F_{\max}}+e_{q_{\max}-q_{\min}}.
                                                               \tag{19}
\]

It is not enough to orient the outer span and appeal to a graphic or lift
matroid.

## 5. Exact gates performed

All arithmetic in the following checks was integer or Boolean.

1. Re-running `compute/p113/audit_support_difference_hall.py` gives zero
   P113 failures on 791,869 width-at-most-30 systems and on all 2,085 P88
   translations.  Difference-only matching fails on three P88 rows, while
   full support--difference matching succeeds.

2. Six-resource private peeling leaves no nonempty core in any of the
   791,869 width-at-most-30 systems.

3. The maximal closed cores in the named hard rows have parameters

\[
\begin{array}{c|ccc}
 &|Y|&|{\cal F}(Y)|&|{\cal D}(Y)|\\ \hline
 \text{P94 translation maximum}&10&10&11\\
 \text{P88 at }\gamma=0&4&4&4\\
 \text{P106 RM97 falsifier}&4&4&4.
\end{array}                                                   \tag{20}
\]

4. On the 20 dense P110 dimension-falsifier rows, three maximal cores are
   empty.  Every one of the 17 nonempty cores has
   `|Y|<=|F(Y)|`; their largest sizes are `(104,113)` and `(64,80)`.
   Every one of those 17 cores also has a support-fold matching saturating
   all its triangles.

5. An exact CP-SAT model independently optimized

\[
                |Y|-|{\cal F}(Y)|                       \tag{21}
\]

over **all** closed subfamilies of P94, P106, and each of the 20 P110 rows.
For every resource `r` it imposed

\[
 2y_r\le\sum_{T\ni r}x_T\le \deg(r)y_r,qquad
 x_T,y_r\in\{0,1\}.                                  \tag{22}
\]

All 22 optimizations were proved optimal with value zero.  The empty family
attains zero, so this says precisely that no closed subfamily with positive
triangle excess exists in those rows.

These gates strongly distinguish CE117 from the false support-only Hall
statement: support Hall can fail before peeling, but every exact hard
failure is removed by a private difference resource, and the terminal core
is support-payable.

## 6. Claim boundary

The proved new facts are the factorized three-cycle representation (4), the
closed-core reduction P117.1, the exact equivalence between the core support
bound and CE117, and the arithmetic falsifier (15)--(19).

No proof is claimed for CE117, the closed-core support bound, or P113.  No
P113 falsifier was found.  A next proof attempt should work directly with a
minimal CE117 counterexample: every resource then has degree at least two,
every fold has triangle degree at least two, and (9) forces a fold of degree
at least four.  The specific remaining task is to transport each unit of
`d_Y(F)-3` along the repeated mark edge in (4) until it reaches either a
degree-two fold or a base-only fold, proving (9) or CE117 without identifying
different occurrences of the same fold or difference label.
