# Algebraic audit of the fixed `K_19-C_19` equality cell

Status: **CONCRETE NECESSARY LEMMAS; THE CELL IS NOT CLOSED**.  This note was
derived from `N19_MECHANISM.md` without inspecting the CNF generator and
without running a SAT solver or a broad graph search.  It proves new exact
constraints on any orientation in the frozen connected missing-cycle cell.

The scope remains exactly `K_19-C_19`, with outdegree 8 at every vertex and
three unreachable incidences in every source row and target column.  None of
the results below excludes another missing 2-factor, another order, or SSNC
in general.

## 1. Notation

All indices lie in `Z/19Z`.  Let

- `A` be the `0/1` adjacency matrix of the proposed orientation;
- `M` be the symmetric adjacency matrix of the fixed missing cycle, so row
  `M_v` is the indicator of `{v-1,v+1}`;
- `Z` be the unreachable matrix, with `Z[v,u]=1` exactly when `u in W_v`;
- `O(v)=N+(v)` and `C_v={v} union O(v)`;
- `T_u=V minus ({u} union N-(u))=O(u) union {u-1,u+1}`; and
- `R_u={v:Z[v,u]=1}`.

The frozen equality ledger gives

\[
 A\mathbf 1=A^{\mathsf T}\mathbf 1=8\mathbf 1,
 \qquad
 Z\mathbf 1=Z^{\mathsf T}\mathbf 1=3\mathbf 1.       \tag{1}
\]

Each `R_u` has three vertices, contains no fixed missing pair, and induces a
directed triangle in `A`.  For `v in R_u`, let `pi_u(v)` be the unique
in-neighbour of `v` in this triangle.  Thus

```text
pi_u(v) -> v
```

and `v ->` the other root.

## 2. The load-bearing row equation

Equality in the fixed-target packing bound says

\[
  T_u\setminus C_v=\{\pi_u(v)\}
  \qquad (Z[v,u]=1).
\]

The union is disjoint, so its indicator-vector form is

\[
  \boxed{
  A_u+M_u=e_v+A_v+e_{\pi_u(v)}
  }
  \qquad (Z[v,u]=1),                                  \tag{2}
\]

where `e_x` is the unit row vector at `x`.  Equivalently,

\[
  A_v-A_u=M_u-e_v-e_{\pi_u(v)}.                       \tag{3}
\]

This is stronger than the scalar row and column sums.  It says that every
unreachable incidence is an exact equality between two 19-coordinate rows,
not merely a cardinality constraint.

## 3. Target sets are injective

**Lemma 1.**  If `u!=w`, then `T_u!=T_w`.

**Proof.**  Suppose `T_u=T_w=T`.  Since `u notin T_u`, equality gives
`u notin T_w`.  For distinct vertices this means `u in N-(w)`, hence
`u -> w`.  Symmetrically, `w notin T_u` gives `w -> u`, a forbidden digon.
Therefore the target sets are distinct.  `square`

This elementary injectivity makes repeated root pairs impossible.

## 4. The root triples form a linear `19_3` configuration

**Lemma 2.**  For distinct targets `u,w`,

\[
  |R_u\cap R_w|\leq1.                                 \tag{4}
\]

**Proof.**  Suppose two roots `a,b` lie in both triples.  There is no missing
pair inside a root triple, so the fixed orientation contains one of `a -> b`
and `b -> a`; assume `a -> b`.  In both directed root triangles, `a` is then
the unique in-neighbour of `b`.  Equation (2) applied to source `b` gives

\[
  T_u=C_b\cup\{a\}=T_w,
\]

contradicting Lemma 1.  `square`

Consequences:

1. The 19 triples `R_u` form a 3-uniform, 3-regular, linear hypergraph on 19
   points: a combinatorial `19_3` configuration.
2. Every pair of distinct root triples intersects in at most one vertex, and
   every pair of root vertices occurs in at most one triple.
3. No fixed missing-cycle edge occurs in a root triple.
4. The three predecessors `pi_u(v)` obtained from the three targets
   `u in W_v` of a fixed source `v` are distinct.

Define a directed graph `Q` by

```text
Q[p,v]=1 iff p=pi_u(v) for the unique target u containing that root edge.
```

Linearity makes this definition unambiguous.  Each root triple contributes
its three directed-cycle arcs, and each vertex belongs to three triples.
Thus `Q` is 3-out-regular and 3-in-regular and is the edge-disjoint union of
19 directed triangles.  It is a spanning subdigraph of `A` with 57 arcs.

The point-pair Gram matrix has the exact form

\[
  \boxed{ZZ^{\mathsf T}=3I+Q+Q^{\mathsf T}}.          \tag{5}
\]

Indeed, an off-diagonal entry counts root triples containing that pair; it is
zero or one by Lemma 2, and a covered pair receives exactly one direction in
`Q`.  Similarly, `Z^T Z` has diagonal three and off-diagonal entries
only zero or one.

## 5. Global matrix identity

Fix a target `u` and sum (2) over its three roots.  The left side becomes
`3(A_u+M_u)`.  On the right,

- the unit vectors `e_v` sum to the indicator of `R_u`;
- the adjacency rows sum to row `u` of `Z^T A`; and
- the map `v -> pi_u(v)` is a cyclic predecessor permutation of `R_u`, so the three
  predecessor unit vectors give a second indicator of `R_u`.

Doing this for all targets yields

\[
  Z^{\mathsf T}A+2Z^{\mathsf T}=3(A+M),
\]

or

\[
  \boxed{Z^{\mathsf T}(A+2I)=3(A+M).}                 \tag{6}
\]

Every entry of (6) has a direct set interpretation: for target `u`, the
three roots send zero arcs outside `T_u`, one arc into each root, and three
arcs into every vertex of `T_u minus R_u`.

## 6. A modulo-3 rank obstruction

Reduce (6) modulo 3.  Since `2=-1` in `F_3`,

\[
  Z^{\mathsf T}(A-I)=0.                               \tag{7}
\]

**Lemma 3.**  Every candidate unreachable matrix satisfies

\[
  \boxed{\operatorname{rank}_{\mathbb F_3}(Z)\leq17.} \tag{8}
\]

**Proof.**  Each row of `Z^T` has coordinate sum three, hence its
row space lies in

\[
  H=\{y\in\mathbb F_3^{19}:y\mathbf1=0\},
\]

which has dimension 18.  If `rank_3(Z)=18`, that row space equals `H`, and
(7) says

\[
  yA=y\qquad\hbox{for every }y\in H.                 \tag{9}
\]

Column regularity in (1) gives

\[
  \mathbf1^{\mathsf T}A=8\mathbf1^{\mathsf T}
  =2\mathbf1^{\mathsf T}\quad\hbox{in }\mathbb F_3.
\]

Because `19=1` in `F_3`, the row vector
`e_i^T-1^T` belongs to `H`.  Substitution in (9)
gives

\[
  e_i^{\mathsf T}A=e_i^{\mathsf T}+\mathbf1^{\mathsf T}.
\]

Its `i`th coordinate is two, contradicting the zero diagonal of `A`.
Therefore rank 18 is impossible.  `square`

This gives several exact certificate checks:

- every `18 by 18` minor of `Z` is divisible by three;
- besides the all-ones vector, `Z` has a second independent right-kernel
  vector over `F_3`; and
- `Z^T` has a second independent kernel vector as well.

For the latter colouring, every root triple has colour sum zero.  Thus each
triple is either monochromatic or contains the three colours `0,1,2`.

## 7. All circulant unreachable relations are excluded

**Corollary 4.**  No 3-regular circulant matrix `Z` can extend to an
orientation satisfying the equality cell, even if `A` itself is not assumed
circulant.

**Proof.**  A circulant `Z` with row support consisting of three distinct
offsets has representer

\[
  f(x)=x^a+x^b+x^c
\]

over `F_3[x]/(x^{19}-1)`.  Since `f(1)=3=0`, it shares the factor `x-1`.
Moreover,

\[
  x^{19}-1=(x-1)\Phi_{19}(x).
\]

The order of 3 modulo 19 is 18 (`3^9=-1 mod 19`), so `Phi_19` is
irreducible over `F_3`.  The three-term polynomial `f` is not a scalar
multiple of `Phi_19=1+x+...+x^18`.  Hence

\[
  \gcd(f,x^{19}-1)=x-1,
\]

and the circulant has nullity one and rank 18 over `F_3`.  This contradicts
Lemma 3.  `square`

The obstruction is stronger than testing circulant orientations: it rules
out a translation-invariant unreachable relation even under a completely
non-translation-invariant orientation.

### Falsified coarse construction

For example, the cyclic blocks

\[
  R_u=u+\{2,4,9\}
\]

form a valid coarse `19_3` configuration.  Their pair differences are
`+/-2,+/-5,+/-7`, so the blocks are linear and contain no fixed missing
pair; they also avoid the diagonal.  Orienting every block as

\[
  u+2\to u+4\to u+9\to u+2
\]

gives the required edge-disjoint directed root triangles.  The corresponding
rows of `Z` have offsets `{10,15,17}`.  Exact elimination over `F_3` gives

```text
n=19, row_offsets=(10,15,17), rank_mod_3=18, nullity=1.
```

Thus this explicit incidence-and-triangle seed cannot satisfy (6) and cannot
extend to an orientation `A`.  This was one 19-by-19 rank calibration, not a
search over graphs.

## 8. Cycle-potential identity

Equation (3) treats the rows of `A` as a potential on the directed relation
`Z`.  Let

```text
v_0 ->_Z v_1 ->_Z ... ->_Z v_(k-1) ->_Z v_0
```

be a simple directed cycle, put `S={v_0,...,v_(k-1)}`, and write

```text
p_i = pi_(v_(i+1))(v_i).
```

Summing (3) around the cycle cancels all adjacency rows and gives the exact
integer multiset equation

\[
  \boxed{
  \sum_i e_{p_i}=(M-I)\mathbf1_S.
  }                                                     \tag{10}
\]

At coordinate `x`, the right side equals

\[
  |\{x-1,x+1\}\cap S|-\mathbf1_S(x).                 \tag{11}
\]

The left side is nonnegative.  Therefore every vertex in `S` has at least
one fixed-cycle neighbour in `S`.  Equivalently, the vertex set of every
directed cycle of `Z` is a union of cyclic runs, each of length at least two.

Equation (10) retains multiplicities.  It is an exact local certificate: the
predecessors decorating the cycle edges must realize the multiset on its
right side, while each `p_i` must differ from the source and target and must
not be a fixed missing neighbour of its source.

## 9. The unreachable digraph has no digons

**Lemma 5.**  There are no distinct `i,j` with both `Z[i,j]=1` and
`Z[j,i]=1`.

**Proof.**  Apply (10) to a directed 2-cycle.  Its two selected vertices must
be adjacent on the fixed cycle; relabel them `i,i+1`.  The predecessor
multiset is

\[
  \{i-1,i+2\}.                                        \tag{12}
\]

For the incidence `i ->_Z i+1`, the predecessor cannot be `i-1`, which is
missing-adjacent to source `i`.  Hence it is `i+2`; the other predecessor is
`i-1`.  Equation (2) now gives

\[
\begin{aligned}
 T_{i+1}
   &=C_i\cup\{i+2\}\\
   &=\{i\}\cup O(i)\cup\{i+2\}.
\end{aligned}
\]

But also

\[
 T_{i+1}=O(i+1)\cup\{i,i+2\}.
\]

The two displayed exceptional vertices are absent from both outneighbour
sets for the forced missing/predecessor reasons, so

\[
  O(i)=O(i+1).                                         \tag{13}

\]

The two sources consequently have identical direct and literal two-step
reachability status for every target outside `{i,i+1}`.  Their unreachable
rows agree on those 17 coordinates.  Each row has three ones; one is the
opposite member of the assumed digon and the diagonal is zero.  Hence there
are exactly two further targets `u` for which

\[
  Z[i,u]=Z[i+1,u]=1.
\]

Then `R_u` contains the fixed missing pair `{i,i+1}`, contradicting the
proved root-triangle property.  `square`

Thus `Z` is itself an oriented graph: its three outneighbours and three
inneighbours are six distinct vertices.

## 10. The unreachable digraph has no directed triangle

**Lemma 6.**  `Z` has no directed 3-cycle.

**Proof.**  By (11), three vertices supporting a directed cycle must be three
consecutive fixed-cycle vertices, say

\[
  S=\{i,i+1,i+2\}.

\]

Equation (10) makes their predecessor multiset

\[
  \{i-1,i+1,i+3\}.                                    \tag{14}

\]

There are two cyclic orientations on these three vertices.

For

```text
i ->_Z i+1 ->_Z i+2 ->_Z i,
```

the first edge must use predecessor `i+3`: `i-1` is missing from source `i`
and `i+1` is the target.  The second edge must then use `i-1`, because the
other remaining value `i+1` is its source.  The last edge is forced to use
`i+1`, which is missing from its source `i+2`, a contradiction.

For the reverse orientation

```text
i ->_Z i+2 ->_Z i+1 ->_Z i,
```

the first edge again must use `i+3`, since both `i-1` and `i+1` are missing
from source `i`.  The second edge must use `i-1`, since `i+1` is its target.
The last predecessor is then `i+1`, equal to its source, again impossible.
Therefore neither orientation exists.  `square`

Combining the diagonal-zero ledger with Lemmas 5--6, `Z` is a 3-in-regular,
3-out-regular oriented graph of directed girth at least four.  This does not
conflict with the directed triangles in `Q`: `Q` records predecessor arcs
inside root fibres, whereas `Z` records source-to-unreachable-target pairs.

## 11. Exact remaining obstruction

The fixed cell is not yet contradicted.  Any surviving candidate must now
simultaneously provide:

1. a diagonal-zero `19 by 19` binary matrix `Z` with every row and column sum
   three;
2. a linear `19_3` root configuration avoiding every edge of the fixed
   `C_19`;
3. a directed-triangle decomposition `Q` satisfying (5);
4. `rank over F_3 of Z <= 17` and hence nonconstant left and right ternary kernel
   colourings;
5. no digon and no directed triangle in the directed relation `Z`;
6. a predecessor decoration satisfying the cycle-potential equation (10) on
   every directed cycle; and
7. an 8-regular orientation matrix `A` satisfying the full row equations (2),
   equivalently the matrix identity (6).

The exact missing implication is either a proof that no such noncirculant
rank-deficient decorated `19_3` configuration exists, or an explicit one that
reconstructs a valid `A`.  The present arguments do not supply either.  No
larger order, alternative 2-factor, generator inspection, or production
solve follows from this note.
