# Independent referee report on the cycle-19 algebraic lemmas

## Scope and evidence

This audit starts from the raw definitions of an 8-outregular orientation of
`K_19-C_19` and a binary unreachable matrix `Z` with all row and column sums
three.  It does not inspect or solve any CNF and does not recommend adding any
of the audited lemmas as production constraints.

Audited source:

```
CYCLE19_ALGEBRAIC_AUDIT.md
SHA-256 46A4D14EE31D59E9374E8E9CB592456A30DB5FD54F33585466160252D660E5D4
```

Overall verdict: **ACCEPT**.  Every stated load-bearing lemma follows from the
frozen equality-cell hypotheses.  No counterexample was found in the exact
finite checks described below.

## 1. Equality fibre and row equation — ACCEPT

For `Z[v,u]=1`, equality in the target packing count gives

```
C_v subset T_u,
|C_v|=9,
|T_u|=10.
```

The three roots at `u` form a directed triangle.  A root `v` points to its
out-neighbour in that triangle and not to its unique in-neighbour
`pi_u(v)`.  All seven non-root elements of `T_u` lie in `O(v)`.  Hence the
single element of `T_u minus C_v` is exactly `pi_u(v)`.

The indicator of `T_u=O(u) union {u-1,u+1}` is `A_u+M_u`; the union is
disjoint.  The indicator of `C_v` is `e_v+A_v`; this union is also disjoint.
Therefore

\[
 A_u+M_u=e_v+A_v+e_{\pi_u(v)},
\]

and rearrangement gives equation (3).  There is no hidden orientation or
multiset assumption in this conversion.

An exact local enumeration of all eight tournaments on a labelled root
triple confirms that the required singleton complement at every root occurs
only for the two directed-cycle orientations.  Transitive root triples have
root outdegrees `0,1,2` and cannot give three 9-element source sets.

## 2. Target-set injectivity — ACCEPT

If `T_u=T_w` for distinct targets, then `u notin T_w`.  The partition of the
vertices other than `w` into out-neighbours, in-neighbours, and fixed missing
neighbours forces `u->w`.  Interchanging `u,w` forces `w->u`, a digon.

Counterexample search: every oriented/missing simple graph through order five
was enumerated, with each unordered pair independently in one of the states
`missing`, `left->right`, or `right->left`.  Across

```
3 + 27 + 729 + 59049 = 59808 graphs
```

no two distinct vertices had equal sets `O(u) union M(u)`.  This is a finite
stress check; the partition argument is the proof.

## 3. Linear `19_3` configuration — ACCEPT

Suppose two target fibres share distinct roots `a,b`.  They cannot be a fixed
missing pair.  If `a->b`, then `a` is the unique in-neighbour of `b` in each
directed root triangle.  The accepted row equation gives

```
T_u = C_b union {a} = T_w,
```

contradicting target-set injectivity.  Thus two fibres intersect in at most
one root.

All listed consequences are valid:

- every root pair occurs in at most one fibre;
- the three predecessors assigned to a fixed source are distinct;
- the predecessor digraph `Q` is unambiguous;
- each of the three fibres containing a vertex contributes one incoming and
  one outgoing `Q` arc at that vertex; and
- the 19 directed root triangles are edge-disjoint and give 57 arcs.

For the Gram identity, `(ZZ^T)[a,b]` counts target fibres containing both
roots.  Its diagonal is three and, by linearity, an off-diagonal entry is zero
or one.  A covered pair has exactly one orientation in `Q`.  Hence

\[
 ZZ^{\mathsf T}=3I+Q+Q^{\mathsf T}.
\]

As a concrete incidence check, the 19 cyclic blocks
`u+{2,4,9}` have row and column sums three, maximum pairwise block
intersection one, and no fixed missing-cycle pair.  Orienting them
`u+2 -> u+4 -> u+9 -> u+2` gives an integer Gram matrix exactly equal to
`3I+Q+Q^T`.

## 4. Global matrix identity — ACCEPT

For a fixed target `u`, summing the row equation over its three roots gives:

- `3(A_u+M_u)` on the left;
- row `u` of `Z^T A` from the three adjacency rows;
- row `u` of `Z^T` from the three source unit vectors; and
- a second copy of that row because the predecessor map is a permutation of
  the directed root triangle.

This proves, coordinate by coordinate,

\[
 Z^{\mathsf T}A+2Z^{\mathsf T}=3(A+M),
 \qquad
 Z^{\mathsf T}(A+2I)=3(A+M).
\]

The set interpretation is also correct.  The three roots send no arc outside
`T_u`, exactly one arc into each member of `R_u`, and three arcs into each of
the seven members of `T_u minus R_u`.

## 5. The `F_3` rank lemma — ACCEPT

Modulo three, the matrix identity becomes

\[
 Z^{\mathsf T}(A-I)=0.
\]

Every row of `Z^T` has sum three, so its row space lies in the 18-dimensional
hyperplane `H={y:y*1=0}`.  If `rank_3(Z)=18`, that row space equals `H`, and
therefore `yA=y` for every `y in H`.

Both congruences used next are load-bearing and correct:

```
19 = 1 mod 3,
8  = 2 mod 3.
```

Thus `e_i^T-1^T` lies in `H`, while column regularity gives
`1^T A=2*1^T`.  Substitution yields

\[
 e_i^{\mathsf T}A=e_i^{\mathsf T}+\mathbf1^{\mathsf T}.
\]

At coordinate `i` the right side is two but the left side is the zero
diagonal entry `A[i,i]`.  Hence rank 18 is impossible and
`rank_3(Z)<=17`.

The kernel consequences are accurate: nullity is at least two on both sides,
the all-ones vector supplies one kernel direction, and a second left-kernel
colouring has colour sum zero on each root triple.  Three elements of `F_3`
sum to zero exactly when they are monochromatic or are a permutation of
`0,1,2`.

## 6. Circulant corollary — ACCEPT

For a binary 3-regular circulant, the representer is a sum of three distinct
monomials.  It vanishes at one over `F_3`, so `x-1` divides it.  The command

```
python -c "import sympy as s; ... s.n_order(3,19); s.factor(s.cyclotomic_poly(19,x),modulus=3)"
```

returned

```
ord_19(3)=18, 3^9 mod 19=18,
Phi_19 unchanged of degree 18 over F_3.
```

Thus `Phi_19` is irreducible over `F_3`.  A three-term binary polynomial is
not a scalar multiple of the 19-term `Phi_19`, so its gcd with
`x^19-1` is exactly `x-1`.  The standard circulant rank formula therefore
gives rank 18.

An independent Gaussian-elimination check enumerated all
`binom(19,3)=969` distinct three-offset supports.  The exact rank histogram
over `F_3` was

```
{18: 969}.
```

This includes the note's row support `(10,15,17)`, whose rank is 18.  The
cyclic seed is consequently excluded by the accepted rank lemma even when
the prospective orientation `A` is noncirculant.

## 7. Cycle-potential identity — ACCEPT

On a simple directed `Z` cycle, equation (3) is applied with source `v_i`
and target `v_(i+1)`.  Summing cancels every adjacency row.  The targets are a
permutation of the cycle vertex set `S`, and `M` is symmetric, so the
remaining equality is exactly

\[
 \sum_i e_{p_i}=(M-I)\mathbf1_S.
\]

At coordinate `x`, the right side is the number of fixed-cycle neighbours of
`x` in `S`, minus `1_S(x)`.  Since the left side is a nonnegative integer
multiset, every selected vertex has a selected fixed-cycle neighbour.  This
is equivalent to saying that all cyclic runs in `S` have length at least two.

Exact subset check: all `2^19=524288` subsets of the fixed cycle were
enumerated.  Nonnegativity of `(M-I)1_S` was equivalent to the absence of an
isolated selected vertex for every subset.  There were 43,721 qualifying
subsets; exactly 19 had size two and exactly 19 had size three.

The stated decoration restrictions are valid.  A predecessor is another
root in the target fibre, so it differs from source and target, and linearity
plus the root-triangle property prevents it from being a fixed missing
neighbour of the source.

## 8. No-digon lemma — ACCEPT

For a directed 2-cycle in `Z`, the potential sign condition forces its two
vertices to be adjacent on the fixed cycle.  With vertices `i,i+1`, the
potential multiset is exactly `{i-1,i+2}`.  The predecessor on
`i ->_Z i+1` cannot be the missing neighbour `i-1`, so it is `i+2`; the other
predecessor is `i-1`.

The row equation then gives

```
T_(i+1) = C_i union {i+2}
        = O(i+1) union {i,i+2}.
```

Neither exceptional element belongs to either outneighbour set: `i` is a
loop/missing exception as appropriate, `i+2` points to `i`, and both are the
fixed missing neighbours of `i+1`.  Removing the same two exceptional
elements proves `O(i)=O(i+1)`.

Equal first outneighbourhoods give identical literal two-step reachability.
Outside `{i,i+1}`, the two unreachable rows therefore agree.  Each has two
remaining ones there, so a common target fibre contains the fixed missing
pair `{i,i+1}`, contradicting the accepted root-triangle property.

Adversarial local check: for each of the 19 adjacent pairs, the potential
multiset and source/target/missing exclusions alone admit exactly one
predecessor assignment.  Thus the potential identity alone does **not** prove
this lemma.  The additional row-equation and linearity steps above are
necessary and were checked separately; with them the contradiction is valid.

## 9. No-directed-triangle lemma — ACCEPT

A three-element subset of a 19-cycle with no isolated selected vertex must be
three consecutive vertices.  For `S={i,i+1,i+2}`, the potential multiset is

```
{i-1, i+1, i+3}.
```

There are exactly two cyclic orientations.  In the forward orientation, the
first two predecessor choices are forced to `i+3` and `i-1`, leaving the
missing neighbour `i+1` for source `i+2`.  In the reverse orientation the
first two choices are again `i+3` and `i-1`, leaving `i+1`, now equal to the
last source.  Both are impossible.

All 19 translations and both cyclic orientations were enumerated, including
all permutations of the required predecessor multiset.  The assignment
histogram was

```
{0 valid assignments: 38 cases}.
```

Therefore `Z` has no loops, digons, or directed triangles and is a
3-in-regular, 3-out-regular oriented graph of directed girth at least four.

## 10. Reproducibility summary

The finite checks used a deterministic inline Python program invoked as

```
<PowerShell literal here-string> | python -
```

with ordinary integer matrices and explicit Gaussian elimination modulo
three.  Its combined output was

```
target injectivity: 59808 graphs, no counterexample
all circulant supports: rank histogram {18:969}
cyclic 19_3 seed: row/column sums 3, linear, Gram identity true, rank 18
cycle subsets: 524288 checked, sign equivalence true
size-2 qualifying supports: 19
size-3 qualifying supports: 19
directed-triangle predecessor assignments: 0 in all 38 cases
adjacent-digon local predecessor assignments: exactly 1 in all 19 cases
```

No computation assumed the existence of an orientation satisfying the full
cell.  These checks test the individual algebraic implications and proposed
countermodels only.

## Final decision

All six named lemmas, the row equation, the Gram identity, the global matrix
identity, the rank and circulant consequences, and the cycle-potential
corollaries are **ACCEPTED** under the frozen `K_19-C_19` equality-cell
hypotheses.  The note correctly stops short of closing the cell.  These
results remain referee-checked necessary conditions, not production CNF
constraints and not an SSNC result.
