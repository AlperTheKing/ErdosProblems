# Wave 3: global C5 stability versus the balanced-deficiency rotor

## Verdict

There is a clean global stability theorem on the entire `C5`-homomorphic
region.  It is quantitative at the additive, rather than graphon, scale and
handles nonuniform blow-ups, disconnected unions, and one-vertex gluings.  Its
zero-deficit case gives a uniform conclusion useful at the live wall:

> **No checked balanced-deficiency rotor whose production graph admits a
> homomorphism to `C5` exists, for any window `t`.**

The proof uses the rotor's global equality `N = 5t`, `|M| = t^2` and its tiny
complete-row support `|F*| = t^2 - 1`.  A `C5` homomorphism would force the
graph to be the complete balanced blow-up `C5[t]`; every maximum cut of that
graph has all `4t^2` blue edges in `F*`, a contradiction.

This does **not** close the wall.  The production hypotheses currently do not
force a `C5` homomorphism, or even a bounded-exception aligned `C5` core.  In
fact, generic near-extremal stability cannot supply such a core: a balanced
blow-up with one perfect matching deleted has normalized extremal deficit
tending to zero but needs at least `t/2` vertex deletions to expose an aligned
complete `C5` core.  Thus a useful next lemma must exploit the rotor circuit
and neutral-transport data, not extremal deficit alone.

## 1. The live delta=0 wall, precisely

There are two different deficits in this discussion; conflating them hides the
actual gap.

1. The extremal deficit is

   ```text
   D_ext(G) = N^2 - 25 beta(G),
   beta(G) = e(G) - maxcut(G).
   ```

2. For a row choice `omega`, the collision defect is

   ```text
   Delta_col(omega) = |collision obligations| - nu(omega),
   ```

   where `nu(omega)` is the maximum coherent source matching size.

In the pure length-five FullBank reduction, `CompleteShortestRowDB` lists every
bad edge exactly once and lists every literal length-four blue path between its
endpoints.  The canonical selector minimizes `(Delta_col,rowCode)`.  The
identity `Delta_col = 0` is exactly the existence of a total coherent collision
assignment; the compiled downstream adapters turn such an assignment, with
the door/vertex-slack/prune sources, into the graph-derived FullBank microflow
and hence the FullBank package.  Abstract package algebra is not the live gap.

If the minimum collision defect is positive, the local attachment theorem and
the exact transport identity

```text
Delta_col(omega') - Delta_col(omega)
  = born + brokenLive - deadUnmatched - reoptimizedGain
```

reduce a sink neutral class to a nontrivial cycle of equal-defect detours.  The
production interface `CheckedBalancedDeficiencyRotor` packages this survivor.
Writing its window as `t`, its relevant global fields are

```text
N = 5t,
|M| = bads.length = t^2,
F* = union of every edge in every complete shortest row,
|F*| = t^2 - 1,
rotorLength >= 2,
```

together with a checked maximum cut, triangle-freeness, complete rows, balanced
transport ledgers, and a fully covered degree-`t` profile owner on every rotor
transition.  Since the database covers every bad edge and the displayed cut is
maximum,

```text
beta(G) = |M| = t^2,
D_ext(G) = (5t)^2 - 25t^2 = 0,
Gamma = 25|M| = N^2.
```

The live wall is therefore:

> Exclude a positive-collision-defect checked rotor with `D_ext = 0` and
> `|F*| = t^2 - 1`, or construct an augmentation from it.

The `t=3` and `t=4` windows are already closed by the incidence and
enumeration-backed mechanisms recorded in the registry.  R51 makes `t=5` a
finite production-extension catalogue problem and leaves `t >= 6` without a
uniform closer.  A global stability argument must use the displayed equality
and the support deficit; proving only an abstract scalar Hall inequality would
return to a dead route.

## 2. Quantified C5-template stability lemma

Here is the promised explicit stability statement.  It is global: no
connectedness assumption is made, so disconnected components and blocks glued
at cut vertices are included whenever the whole graph maps to `C5`.

### Lemma (additive C5-template stability)

Let `G` be a finite graph on `N > 0` vertices and let

```text
phi : V(G) -> Z/5Z
```

be a graph homomorphism to `C5`.  Put

```text
A_i = phi^(-1)(i),
n_i = |A_i|,
e_i = e_G(A_i,A_(i+1)),
b   = beta(G),
D   = N^2 - 25b,
q   = N/5,
a   = sqrt(b),
h   = q - a.
```

Indices are modulo five.  Then:

1. `D >= 0`.
2. For every `i`,

   ```text
   q - 6h <= n_i <= q + 4h,
   |n_i-q| <= 6h <= 6D/(5N).
   ```

3. If

   ```text
   K = sum_i (n_i n_(i+1) - e_i)
   ```

   is the number of cyclic template edges missing from `G`, then

   ```text
   0 <= K <= D.
   ```

4. If `N = 5t`, then on the same vertex set `G` is at symmetric edge-edit
   distance at most `4D` from some complete balanced blow-up `C5[t]`.
5. Equality `D = 0` holds if and only if `N = 5t` and `G` is a complete
   balanced blow-up `C5[t]` (up to rotating or reflecting the five classes).

### Proof

Deleting all edges between `A_i` and `A_(i+1)` leaves a graph mapping to the
path obtained by deleting one edge of `C5`, hence leaves a bipartite graph.
Therefore

```text
b <= e_i <= n_i n_(i+1)                         (1)
```

for all `i`.  Multiplying the five upper product inequalities gives

```text
b^5 <= product_i(n_i n_(i+1))
    = (product_i n_i)^2
    <= (N/5)^10,
```

where the last step is AM-GM.  Thus `b <= N^2/25`, proving `D >= 0` and
`h >= 0`.

Set

```text
s_i = n_i+n_(i+1),
r_i = s_i-2a.
```

By (1) and AM-GM, `r_i >= 0`.  Also

```text
sum_i r_i = 2N-10a = 10h.                       (2)
```

The odd cyclic system `s_i=n_i+n_(i+1)` is invertible, with

```text
2n_i = s_i-s_(i+1)+s_(i+2)-s_(i+3)+s_(i+4).
```

Substituting `s_j=2a+r_j` and using (2), the alternating `r`-sum lies between
`-10h` and `10h`.  Hence

```text
a-5h <= n_i <= a+5h,
q-6h <= n_i <= q+4h.
```

Moreover

```text
h = (q^2-b)/(q+a) = D/(25(q+a)) <= D/(5N),      (3)
```

which proves the stated class-size bound.

For the missing edges, (1) gives

```text
K <= sum_i (n_i n_(i+1)-b).
```

Since `n_i n_(i+1) <= s_i^2/4`,

```text
n_i n_(i+1)-b <= a r_i + r_i^2/4.
```

Using `sum r_i=10h` and `sum r_i^2 <= (sum r_i)^2`,

```text
K <= 10ah+25h^2
  <= 50ah+25h^2
   = 25((a+h)^2-a^2)
   = D.                                          (4)
```

Now assume `N=5t`.  The number of vertices that must be moved between the five
classes to make every class have size `t` is

```text
r = (1/2) sum_i |n_i-t| <= 3D/N                 (5)
```

by (3).  First add the `K <= D` missing cyclic edges.  Moving one vertex to a
new template class changes at most `N-1` template adjacencies, so changing the
resulting complete nonuniform template to a balanced one costs at most `rN`.
Equations (4)-(5) give total edit distance at most `D+3D=4D`.

Finally, if `D=0`, then `h=0`, all `n_i=N/5`, and (4) gives `K=0`; hence every
cyclic pair is complete.  Conversely a complete balanced blow-up has
`beta=t^2` and `D=0`.  This proves all claims.  As an arithmetic sanity check,
the class-size and missing-product inequalities were also cleared to integer
comparisons and evaluated over all 324,631 nonnegative integer five-tuples with
`N <= 30`; there were no failures.

## 3. Uniform exclusion of C5-homomorphic rotors

### Corollary

No `CheckedBalancedDeficiencyRotor` has a production graph admitting a graph
homomorphism to `C5`.

### Proof

Let the rotor window be `t`.  Completeness and no-duplication of the database
identify its `t^2` listed atoms with all bad edges of the checked maximum cut.
Thus `beta(G)=t^2`, while `N=5t`; the stability lemma has `D=0` and forces

```text
G = C5[t]
```

as a complete balanced blow-up.

It remains to account for a possible maximum cut that splits a blow-up class.
For a cut of `C5[t]`, let

```text
z_i = (# plus vertices in A_i) - (# minus vertices in A_i),
-t <= z_i <= t.
```

The number of bad edges is

```text
(5t^2 + sum_i z_i z_(i+1))/2.
```

The minimum of the cyclic bilinear form on `[-t,t]^5` is `-3t^2`.  One quick
proof is to normalize by `t` and regard the five coordinates as means of
independent signs: every sign assignment on an odd 5-cycle has at least one
same-sign edge, so its cyclic sum is at least `-3`; taking expectations gives
the bound.  Equality forces the product distribution to be supported on the
ground states with exactly one same-sign edge.  That ground-state set contains
no two-dimensional product subcube: adjacent variable coordinates are
impossible because one would need the other variable sign to be opposite to a
fixed neighbor for both of its values; if the variables are at distance two,
each has two fixed opposite-sign neighbors, while the remaining fixed edge is
same-sign, forcing three same-sign edges.  Consequently, after rotation and
global sign reversal, every maximum cut has the form

```text
(z_0,z_1,z_2,z_3,z_4) = (x,t,-t,t,-t),
```

with `-t <= x <= t`: four classes are unsplit and at most one class is split.

If no class is split, one complete cyclic block is bad and the other four are
blue.  Every blue edge lies on a length-four path around those four blocks
closing an edge of the bad block.  If `A_0` is split, the two partial bad
rectangles are `A_0^+-A_1` and `A_0^--A_4`; the two complementary partial blue
rectangles and the three full blue rectangles again each lie on such a path.
Triangle-freeness excludes a length-two blue path between a bad pair, so these
are shortest rows.  Database row-completeness therefore puts **every** blue
edge in `F*`.  Hence

```text
|F*| = blueCount = 5t^2-t^2 = 4t^2.
```

The rotor circuit field instead says `|F*|=t^2-1`, impossible for every
positive `t`.

This is a uniform proof, not a rooted-`t5` enumeration.

## 4. Exact conversion from an aligned core to a finite window

The useful quantitative notion is not unspecified edit closeness.  It is an
aligned complete core for the **same maximum cut and complete row database**.

### Lemma (core-to-window conversion)

Let a rotor have window `t`.  Suppose there are disjoint sets
`X_0,...,X_4`, each of size at least `t-K`, such that all five cyclic pairs are
complete and the rotor cut leaves `X_0-X_1` bad and the other four cyclic pairs
blue.  Assume `0 <= K < t`.  Then

```text
t <= 2K-1.                                       (6)
```

Indeed, every edge in the four blue core blocks is on a length-four core path
closing an `X_0-X_1` bad edge.  Complete rows therefore give

```text
t^2-1 = |F*| >= 4(t-K)^2.                        (7)
```

If `t >= 2K`, the right side of (7) is at least `t^2`, a contradiction.  This
proves (6).

There is also an exact edit version.  Suppose the rotor cut is already the
aligned template cut and the production graph differs from that balanced
template in at most `E` edges.  Delete all endpoints of the discrepant edges.
At most `2E` vertices are deleted, so the remaining aligned core has each
class of size at least `t-2E`.  Taking `K=2E` in (6) yields

```text
t <= 4E-1.                                       (8)
```

Equations (7)-(8) are the exact step that turns a sufficiently strong
stability conclusion into a finite catalogue:

```text
aligned vertex error K  ->  only t <= 2K-1,
aligned edit error E    ->  only t <= 4E-1.
```

For example, `K <= 2` would bypass every `t >= 4` catalogue.  `K <= 3` would
reduce the infinite problem to `t=4,5`, so the R51 `t=5` bundle would remain
the last catalogue.  A fixed `K` of any size turns all larger windows into the
support-count contradiction (7).

## 5. Required guardrails and a concrete obstruction

### 5.1 Nonuniform complete blow-ups

For a complete blow-up `C5[n_0,...,n_4]`, multilinearity of cut cost lets a
minimum cut be chosen class-constant, and

```text
beta = min_i n_i n_(i+1).
```

The recurring family

```text
(n_0,...,n_4) = (k+1,k,k+1,k,k+1)
```

has

```text
N = 5k+3,
beta = k(k+1),
D_ext = N^2-25beta = 5k+9 = N+6.
```

Thus `D_ext/N^2 -> 0`, but the blow-up is never balanced.  At fixed order
`N=5t`, the family `(t+1,t,t,t,t-1)` has

```text
beta=t^2-t,
D_ext=25t=5N.
```

Any proposed stability statement that silently upgrades `o(N^2)` deficit to
exact balance is false.  The additive class-size estimate in Section 2 has the
correct scale on both families.

### 5.2 Deleted-matching obstruction to a bounded vertex core

Let `H_t` be `C5[t]` with a perfect matching of `t` edges deleted from one
cyclic block.  Edge bipartization is 1-Lipschitz under edge deletion, while the
cut leaving the deficient block bad is explicit, so

```text
beta(H_t) = t^2-t,
D_ext(H_t) = 25t = 5N.
```

The graph is connected, `C5`-homomorphic, and all bad edges in that displayed
cut still have length-five rows through the other four complete blocks.
Nevertheless, an aligned complete core with at least `t-K` vertices in each
class must cover every missing matching pair by deleting one endpoint.  At
most `2K` endpoints are deleted from the two affected classes, so

```text
2K >= t.
```

Hence `K >= ceil(t/2)` even though `D_ext/N = 5` is constant and
`D_ext/N^2 -> 0`.  In particular, there is no universal implication

```text
K <= C D_ext/N
```

from extremal deficit alone.  This is a concrete obstruction to obtaining the
finite bound (6) from ordinary stability.  The rotor's additional fact
`|F*|=t^2-1` is indispensable.

### 5.3 Glued-block guardrail

Let `W_k` be the one-vertex sum of `C5[k]` and a single `C5`.  Bipartization is
additive under a one-vertex sum: optimal cuts of the two blocks can be globally
flipped to agree at the shared vertex, and every cut restricts to cuts of the
two blocks.  Therefore

```text
N(W_k) = 5k+4,
beta(W_k) = k^2+1,
D_ext(W_k) = 40k-9 = 8N-41.
```

With compatible canonical cuts, `W_k` is triangle-free, its blue graph is
connected, and every bad edge still has a length-five row in its own block.
Yet it has a persistent glued island.  Thus neither graph connectedness nor
blue connectedness licenses a componentwise inequality or the deletion of a
row-visible attached block.  In the stability lemma, the absent cross-block
template edges are correctly charged to `K`; they cannot be declared free.

These three families prove the obstruction claimed in the verdict: graphon
closeness or `o(N^2)` edit distance has no exact finite-window consequence.
One needs exact equality rigidity, or a rotor-specific aligned-core theorem
that consumes the circuit/transport hypotheses.

## 6. Exact finite gate for the missing extraction statement

For a fixed checked production extension `(G,c,bads)` define `q*(G,c)` to be
the largest `q` for which there is an aligned complete `C5` core with five
classes of size at least `q`.  This number has an exact 0-1 PB/SAT gate.

Use variables `x[v,i]` for `v in V(G)`, `i in Z/5Z`, and a fixed side pattern

```text
side(0),...,side(4) = (0,0,1,0,1).
```

For a proposed core size `q`, impose:

```text
sum_i x[v,i] <= 1                                      for every v;
x[v,i] = 0 if c(v) != side(i);
sum_v x[v,i] >= q                                      for every i;
x[u,i] + x[v,j] <= 1                                   for every missing edge uv
                                                        and j-i equal to +/-1;
x[u,i] + x[v,j] <= 1                                   for every actual edge uv
                                                        with j-i not equal to +/-1.
```

The fourth family is imposed for both orientations of each unordered pair; it
says every selected cyclic pair is complete.  The fifth says the selected
induced graph has no off-template edge.  Repeat the gate over the ten dihedral
relabelings (and the globally complemented cut pattern).  All constraints are
integral and finite.  PB UNSAT at `q=t-K` in every relabeling is an exact
certificate that `q*(G,c) <= t-K-1`; a DRAT/LRAT or cutting-planes proof can be
replayed without floating point.

There is a cheaper first gate: require every vertex to receive exactly one of
five labels and retain only the edge-adjacency clauses.  SAT is a production
`C5` homomorphism, which Section 3 rules out uniformly.  UNSAT sends the entry
to the genuinely non-`C5` residual.

This gate must run on the **full production extension**, not merely on the
rooted support circuit.  An intrinsic rooted entry can acquire outside vertices
and edges that change both homomorphism and core feasibility; applying the gate
before R51's extension layer would repeat the intrinsic/production scope error
that R51 explicitly guards against.

## 7. Effect on the t>=5 catalogue

The proved result gives a real, but limited, reduction:

* Every production extension admitting a `C5` homomorphism is excluded for all
  `t` by one global proof.  Such entries need no rooted-`t5` certificate.
* The result does not exclude non-`C5`-homomorphic extensions.  No current
  theorem turns the rotor hypotheses into a homomorphism or a fixed-`K` aligned
  core, and Section 5 proves that extremal deficit alone cannot do so.
* Therefore the present `t=5` catalogue is not bypassed in full.  Adding the
  exact homomorphism/core gate can prune it, but its non-`C5` entries still need
  the production extension UNSAT certificates specified by R51.
* A future rotor-specific core theorem with `K=3` would close every `t>=6`
  window by (6), leaving only the current `t=4,5` work.  With `K<=2`, it would
  bypass the `t>=5` catalogue entirely.

The sharp frontier is thus not another scalar Hall, Schur, Neumann, spectral,
or local-SOS inequality.  It is the following global extraction question:

> Does `D_ext=0`, complete length-five rows, the transversal circuit
> `|F*|=t^2-1`, and a saturated balanced neutral rotor force either a global
> `C5` homomorphism or an aligned complete `C5` core with a fixed number of
> exceptional vertices?

Section 3 settles the homomorphic outcome; Section 4 converts the core outcome
to an exact finite bound; Section 5 shows why the circuit/rotor hypotheses must
do the remaining work.
