# C68: minimum-cut lattice versus the C66 rank profile

## Verdict

The proposed argument splits into a true statement and a false implication.

1. **True.**  For every C60 network, the residual source shore of any maximum
   flow is the unique inclusion-minimal minimum source shore.  It contains
   every splitless hole and is closed under every infinite unary arc.
2. **False.**  Minimum-cut lattice structure does not imply `C66-RANK`.
   Deleting a rank-violating prefix has the wrong capacity sign, and even when
   that deletion is exactly closed under all infinite unary arcs it can be
   strictly more expensive.

An exact three-hole C60-shaped network below is the smallest nondegenerate
counterexample to the lattice-only implication.  It has positive max-flow,
a nontrivial infinite unary arc, an inclusion-minimal residual shore, and

\[
  h_1=4<5=e_1,
\]

so coordinatewise rank dominance fails.  The only natural prefix deletion is
unary-closed but raises the cut capacity by exactly one.

This abstract witness is **not** an arithmetic network `N_X`: its mandatory
source node is an abstract analogue of a splitless hole.  Therefore it does
not refute `C66-RANK` for the actual Erdős 424 networks.  Exact enumeration of
all arithmetic minimum shores at every cutoff `2 <= X <= 200`, plus all
`221184` minimum shores at `X=300`, found no rank failure.  The arithmetic
rank statement remains open; it cannot be obtained from the cut lattice
alone.

## 1. The inclusion-minimal shore theorem

Let `F` be the sum of all finite capacities in `N_X`, and let every nominally
infinite capacity be

\[
 I=F+1.
\]

There is a cut of capacity at most `F`: put every hole on the source side.
All splitless and unary arcs are then internal, so only finite seed arcs can
leave.  Hence the minimum cut value `kappa` satisfies

\[
 \kappa\le F<I. \tag{1}
\]

Fix an integral maximum flow `f`, and let `R_f` be its residual graph.  Put

\[
 S_0=\{v:v\text{ is residual-reachable from }s\}.
\]

No residual arc leaves `S_0`, by definition.  The standard cut-flow identity,
written without suppressing reverse residual arcs, is

\[
 c(U)-|f|
 =\sum_{u\in U,v\notin U}(c_{uv}-f_{uv})
  +\sum_{u\notin U,v\in U}f_{uv}. \tag{2}
\]

Both sums are nonnegative.  Thus `S_0` is a minimum source shore.  Conversely,
if `U` is any minimum source shore, equality in (2) says that no positive
residual arc leaves `U`.  Since `s in U`, every vertex reachable from `s` in
`R_f` lies in `U`.  Therefore

\[
 \boxed{S_0=\bigcap\{U:U\text{ is a minimum source shore}\}.} \tag{3}
\]

In particular, `S_0` is the unique inclusion-minimal minimum shore.  This is
stronger and more precise than saying merely that minimum cuts form a lattice.

### Infinite-arc closure is explicit

Every flow on one arc has magnitude at most `|f|=kappa<=F`.  Hence an arc of
capacity `I=F+1` retains positive forward residual capacity.  It follows that:

* for every splitless hole `e`, the arc `s -> e` forces `e in S_0`;
* for every unary arc `n -> p`, if `n in S_0`, then `p in S_0`.

The same closure holds for every minimum shore directly from (1): crossing
one `I`-arc would already cost more than the minimum.  Thus no generic
max-flow slogan is being used in place of the required unary-closure check.

## 2. Exact cost of a whole-chain prefix toggle

Partition a source shore `S` into seed chains under `D(m)=2m-1`.  Let `R` be
a union of complete chains.  Suppose that `S\R` remains a valid shore: it
contains all mandatory splitless vertices and is closed under every unary
arc.  Write `HE(R), HT(R), NE(R), NT(R)` for the hard/nonhard and
exiting/truncated chain counts in `R`.

Moving `R` to the sink side cuts one new hard source arc for every hard chain,
and removes one outgoing seed arc for every exiting chain.  No seed arc runs
between distinct seed chains.  Hence

\[
\begin{aligned}
 c(S\setminus R)-c(S)
 &=HE(R)+HT(R)-HE(R)-NE(R)\\
 &=\boxed{HT(R)-NE(R)}. \tag{4}
\end{aligned}
\]

For the root prefix `R_t` consisting of chains rooted at most `t`, a violation
of `C66-RANK` is exactly

\[
 HT(R_t)>NE(R_t).
\]

Equation (4) then says that the proposed deletion is **capacity-increasing**,
not capacity-nonincreasing.  Thus the claimed exchange has its sign reversed.

There is a second obstruction.  To make a raw deletion unary-closed one must
replace it by its reverse-unary saturation

\[
 \operatorname{Sat}(R)=R\cup
 \{n\in S:\exists(n\to p)\text{ unary with }p\in\operatorname{Sat}(R)\}.
 \tag{5}
\]

Then `S\Sat(R)` is unary-closed.  But if `Sat(R)` contains a splitless vertex,
the modification cuts an `I`-capacity source arc and is inadmissible.  Also,
`Sat(R)` need not remain a union of complete seed chains, so (4) cannot be
silently reused after saturation.

## 3. Smallest nondegenerate lattice counterexample

Take cutoff label `X=9`, source `s=10`, sink `z=11`, and hole vertices

\[
 \{4,5,7\}.
\]

Mark `4` hard and `5` mandatory.  Let `I=4` and use these arcs:

| arc | capacity | type |
|---|---:|---|
| `s -> 4` | 1 | hard source |
| `s -> 5` | 4 | mandatory source |
| `4 -> 7` | 1 | internal seed |
| `5 -> z` | 1 | exiting seed |
| `7 -> 4` | 4 | unary (`7=2*4-1`) |

The maximum flow has value one, along `s -> 5 -> z`.  Its residual source
shore is exactly

\[
 S_0=\{4,5,7\}.
\]

Every infinite unary arc is internal.  Direct enumeration of all `2^3`
possible shores shows that `S_0` is the unique minimum shore, of capacity
one.

The seed chains are

\[
 4\to7\quad\text{(hard, truncated)},
 \qquad
 5\to z\quad\text{(nonhard, exiting)}.
\]

Thus the sorted profiles are `HT=[4]` and `NE=[5]`, violating
`e_1<=h_1`.

Delete the violating hard prefix `R={4,7}`.  This deletion is already closed
under the infinite unary arc `7 -> 4`; its reverse-unary saturation is still
`{4,7}`, and it does not remove the mandatory node `5`.  Nevertheless the new
shore `{5}` has capacity two (`s -> 4` and `5 -> z`), so

\[
 c(S_0\setminus R)-c(S_0)=1. \tag{6}
\]

This is precisely (4), with `HT(R)=1` and `NE(R)=0`.

The example is minimal among positive-flow C60-shaped witnesses respecting
the numerical seed map, with an even hard root and a nontrivial unary arc.
With only two hole vertices, the hard truncated chain would have one vertex,
so `D(h)>X`; an exiting root `e>h` would require `D(e)<=X`, contradicting the
strict increase of `D`.  Three vertices therefore are necessary, and the
displayed example attains three.

## 4. Exact arithmetic audit

`C68_mincut_lattice.py` reconstructs each arithmetic C60 network from the
number-theoretic definitions.  SciPy supplies an integral maximum flow, but
all accepted statements are recomputed with Python integers:

* residual reachability and SCC condensation;
* direct cut capacity from the original capacity dictionary;
* containment of every splitless root;
* closure under every infinite unary selector;
* the seed-chain profile and coordinatewise rank test;
* reverse-unary saturation and the exact capacity of every proposed prefix
  deletion.

At every cutoff `2 <= X <= 200`, every residual-SCC-closed minimum shore was
enumerated.  The totals are:

```text
cutoffs                              199
distinct minimum shores          98,881
rank failures                         0
canonical/intersection failures       0
```

At `X=300`, all `221184` minimum shores were enumerated separately, again
with zero rank failures.  This is consistent with the canonical checks in
C66 through `X=100000`, but remains finite evidence.

For the canonical shores through `X=200`, the checker tested all `4353`
low-root prefix deletions.  Reverse-unary saturation was exact in every case,
but every prefix hit a mandatory splitless vertex, so none was a valid finite
shore modification.  The first raw strictly saving prefix occurs at

```text
X = 41, threshold = 6, raw delta = -1,
raw nodes = 1, saturated nodes = 2,
saturation hits a splitless vertex.
```

Thus the actual arithmetic data give no counterexample to `C66-RANK`, while
also giving no instance in which the proposed low-prefix deletion can be
used.

## 5. Consequence for the proof frontier

The residual lattice proves only inclusion-minimality and exact infinite-arc
closure.  It carries no root order, and the natural prefix exchange has the
opposite sign.  Therefore `C66-RANK`, if true for the arithmetic networks,
requires an additional number-theoretic mechanism coupling different seed
chains.  A valid next lemma must use generated-factor arithmetic or a global
bank; it cannot be a consequence of minimum-cut lattice theory alone.

## Reproduction

```powershell
$limits = 2..200
python -O problems/424/fanout/wave5/C68_mincut_lattice.py `
  --limits $limits --enumeration-cap 22 `
  --output problems/424/fanout/wave5/C68_mincut_lattice.json
```

The `X=300` exhaustive run is:

```powershell
python problems/424/fanout/wave5/C68_mincut_lattice.py `
  --limits 300 --enumeration-cap 19 `
  --output problems/424/fanout/wave5/C68_mincut_lattice_300.json
```

Normal and `python -O` executions of the full `2..200` audit produced
byte-identical output.

```text
C68_mincut_lattice.py
6EB89410C8AC0DFF65716B77942EC8895CB00EB23BDB1BFF53AA0185D9374624

C68_mincut_lattice.json
83B535434CB975147097A39B98D59F7EE3E5B1F7D251F3716C987251E9071FC1

C68_mincut_lattice_300.json
F71C68B6F9C3C148894B3AA58BFDA34C8B08EDFF0273DA3A28B5D2C90D644E8F
```
