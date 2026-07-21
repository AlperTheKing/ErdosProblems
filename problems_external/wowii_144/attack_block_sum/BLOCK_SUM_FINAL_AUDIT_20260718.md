# W144 1-sum / block-center final audit

Date: 2026-07-18.

## Status

This note does **not** prove W144 and does not prove that a minimal
counterexample is 2-connected.  It proves the exact metric and induced-tree
formulas for a 1-sum, proves two rooted induced-tree lower bounds, reduces the
entire separable case to one explicit cut-rooted inequality, verifies that
inequality exhaustively through order 13, and records the first exact failures
of two proposed shortcuts.  The proof attempt stops at the first unsupported
inference.

## 1. Notation and exact direct bridge

Let `G=G_1 vee_v G_2`, where `G_1,G_2` are connected induced subgraphs,
`V(G_1) intersect V(G_2)={v}`, and there are no edges between the two
exclusive sides.  Write

```text
tau(H)   = maximum order of an induced tree of H,
rho(H,v) = maximum order of an induced tree of H containing v,
a_i      = ecc_{G_i}(v).
```

The registered 1-sum bridge is the exact identity

```text
tau(G)=max(tau(G_1),tau(G_2),rho(G_1,v)+rho(G_2,v)-1).   (1.1)
```

Indeed, rooted induced trees on the two sides glue at `v` to an induced tree.
Conversely, an induced tree meeting both exclusive sides must contain `v`,
and its intersection with each side is a rooted induced tree.  A tree meeting
only one side has order at most the corresponding `tau(G_i)`.  This proves
(1.1).

Consequently the exact load-bearing inequality for the rooted gluing branch is

```text
rho(G_1,v)+rho(G_2,v)-1 >= girth(G)-1+eta(G).             (1.2)
```

If (1.2) holds for one cut decomposition, its glued tree proves W144.

## 2. Exact distance, eccentricity, center, and eta formulas

For `x in V(G_i)`, with `{i,j}={1,2}`, every path from `x` to the exclusive
part of the other side uses `v`.  Hence

```text
ecc_G(x)=F_i(x):=max(ecc_{G_i}(x), d_{G_i}(x,v)+a_j).     (2.1)
```

Thus

```text
rad(G)=r:=min {F_i(x): i in {1,2}, x in V(G_i)},          (2.2)
C_i^*  :={x in V(G_i): F_i(x)=r},
C(G)   =C_1^* union C_2^*.                                (2.3)
```

Put `b_i=d_{G_i}(v,C_i^*)`, with distance to the empty set interpreted as
infinity.  For `x in V(G_i)`,

```text
d_G(x,C(G))
 =min(d_{G_i}(x,C_i^*), d_{G_i}(x,v)+b_j).                (2.4)
```

Taking the maximum of (2.4) on the two sides is an exact formula for `eta(G)`.
Also, with infinity used for an acyclic side,

```text
girth(G)=min(girth(G_1),girth(G_2)).                      (2.5)
```

The center cannot have an exclusive vertex on both sides.  Otherwise choose
central `c_i in V(G_i)-{v}` and put `p=d(c_1,v)>0`,
`q=d(c_2,v)>0`.  If the common central eccentricity is `r`, then for every
`y in V(G_1)`,

```text
q+d(v,y)=d(c_2,y)<=r,
```

so `a_1<=r-q<r`; symmetrically `a_2<r`.  But then
`ecc_G(v)=max(a_1,a_2)<r`, contradicting the definition of the radius.
Therefore the center is contained in one side (possibly together with `v`),
or it is exactly `{v}`.  This is the precise block-center dichotomy used by
(2.4); it does not by itself control eta strongly enough for (1.2).

## 3. Two proved rooted induced-tree bounds

### Lemma 3.1 (rooted geodesic)

For every connected graph `H` and root `v`,

```text
rho(H,v)>=ecc_H(v)+1.                                    (3.1)
```

Choose a vertex farthest from `v`.  A shortest path to it is induced, since a
chord would shorten the path, and has `ecc_H(v)+1` vertices.

### Lemma 3.2 (rooted shortest-cycle tree)

Let `H` be connected of girth `g>=5`, let `K` be a shortest cycle, and put
`h=d_H(v,V(K))`.  Then

```text
rho(H,v)>=g-1+h,                                         (3.2)
```

and in particular `rho(H,v)>=g-1` for every root `v`.

**Proof.**  A shortest cycle is chordless.  Take a shortest `v`--`K` path
`P`, ending at `u in K`.  No vertex of `P-u` has a neighbor on `K` other than
the next endpoint incidence: an earlier incidence shortens the distance to
`K`, while two incidences at the last outside vertex make, with the shorter
arc of `K`, a cycle shorter than `g` (for `g>=5`).  Choose `z in K-{u}`.
Then `P union (K-z)` is induced, connected, and acyclic, contains `v`, and
has `h+g-1` vertices.  QED.

If `G_1` contains a global shortest cycle `K`, (3.1)--(3.2) and a farthest
rooted geodesic in `G_2` give the unconditional bound

```text
rho(G_1,v)+rho(G_2,v)-1
 >= max(a_1+1,g-1+d(v,K))+a_2.                            (3.3)
```

## 4. Reduction to one cut-rooted theorem

Let `v` be a cut vertex and let `Q_1,...,Q_s` be the components of `G-v`.
Put `H_j=G[Q_j union {v}]`.  Rooted induced trees in distinct branches have
no cross-edge and therefore glue independently.  Conversely, every rooted
induced tree restricts to one in each branch.  Hence

```text
rho(G,v)=1+sum_j (rho(H_j,v)-1).                          (4.1)
```

In particular, for **every** partition of the components into a 1-sum,

```text
rho(G_1,v)+rho(G_2,v)-1=rho(G,v).                         (4.2)
```

Thus the whole separable case reduces exactly to the following statement.

> **CUT-ROOTED W144.**  If `G` is connected and cyclic, has girth at least
> five, and `v` is a cut vertex, then
> `rho(G,v)>=girth(G)-1+eta(G)`.

CUT-ROOTED W144 immediately proves W144 for every non-2-connected graph via
(1.1).  Therefore it would prove that a vertex-minimal counterexample is
2-connected.  This is a genuine rooted strengthening only at cut vertices,
not at arbitrary roots.

## 5. Exact finite audit

`audit_block_sum.py` uses `geng -ctfq`, filters by exact girth, recomputes the
full center and eta, and computes each rooted induced-tree number by exhaustive
vertex-subset enumeration.  Every articulation and every elementary
component-versus-rest split was checked.  By (4.2), these values also cover
all groupings at the same articulation.

```text
order                 5    6    7    8     9      10      11       12        13
cut graphs             0    1    5   19    78     318    1,404    6,850    37,672
elementary splits      0    1   10   50   259   1,170    5,582   27,268   145,365
```

Totals:

```text
46,347 cut graphs,
179,705 elementary cut splits,
0 failures of rho(G,v)>=girth(G)-1+eta(G).
```

This is finite evidence, not a proof.  The first twenty equality splits,
including `g,eta,a_1,a_2,rho_1,rho_2`, side types, center location, the
nearest shortest cycle, and the deficit of (3.3), are recorded in
`tight_splits_first20.json`.

## 6. The elementary rooted bounds do not close the theorem

The first failure of (3.3) to reach the W144 target is

```text
graph6: F?bao
edges: 04,05,15,16,25,36,46.
```

This is a 5-cycle with one leaf at each of two cycle vertices.  It has

```text
girth(G)=5, eta(G)=2, C(G)={1}, target=6, tau(G)=6.
```

At the split `v=5`, with side 2 equal to the edge `{2,5}`, the exact data are

```text
a_1=3, a_2=1, d(v,K)=0,
rho(G_1,v)=5, rho(G_2,v)=2.
```

The proved lower bound (3.3) gives only

```text
max(3+1,5-1+0)+1=5<6,
```

whereas the exact rooted sum is `5+2-1=6`.  The missing one vertex is the
second off-cycle leaf retained while a cycle vertex is broken.  Thus root
eccentricity plus distance to a shortest cycle does not measure the required
rooted off-cycle capacity.

The proposed cleaner center inequality

```text
eta(G_1 vee_v G_2)
 <= max(eta(G_1), d_{G_1}(v,K)+ecc_{G_2}(v))              (6.1)
```

is false on the same split:

```text
2 > max(1,0+1)=1.
```

Hence (6.1) cannot combine local W144 with Lemma 3.2 to prove 1-sum closure.

## 7. Exterior end-block phi deletion is false

Put `phi(H)=girth(H)+eta(H)`.  The weaker selection rule "delete a non-cut
vertex in an end block outside the center block without decreasing phi" is
false.

The first exact failure is again `F?bao`.  Its exterior end blocks are the
bridges `{2,5}` and `{3,6}`.  Deleting either non-cut leaf preserves girth 5
but changes eta from 2 to 1, so `phi` drops from 7 to 6.

The first multicyclic failure is

```text
graph6: G?`e_w
edges: 04,06,15,16,25,36,37,47,57.
```

It has cycle rank 2, girth 5, center `{7}`, eta 2, and sole exterior end block
`{2,5}`.  Deleting its non-cut vertex 2 leaves a connected cyclic graph with
center `{3,6,7}`, girth 5, eta 1, and again changes `phi` from 7 to 6.
Therefore an end-block deletion induction cannot supply the registered
nondecreasing-phi step.

## 8. First unsupported inference and stop

The exact formulas (1.1), (2.1)--(2.5), and (4.1) and the rooted lower bounds
(3.1)--(3.2) are proved.  What remains unsupported is precisely

```text
rho(G,v)>=girth(G)-1+eta(G) for a cut vertex v.           (8.1)
```

The tight family `F?bao` shows that (8.1) cannot be derived from only a root
geodesic and a broken shortest cycle; an additional rooted off-cycle capacity
term is load-bearing.  Introducing that term without an independent theorem
would restate the global induced-tree capacity problem.  Accordingly this
audit records (8.1) as the exact frontier and opens no hierarchy of surrogate
block parameters.

## 9. Reproduction

From the repository root:

```text
python -m py_compile problems_external/wowii_144/attack_block_sum/test_block_sum_bound.py problems_external/wowii_144/attack_block_sum/audit_block_sum.py problems_external/wowii_144/attack_block_sum/collect_tight_splits.py
python problems_external/wowii_144/attack_block_sum/audit_block_sum.py --min-n 5 --max-n 13
python problems_external/wowii_144/attack_block_sum/collect_tight_splits.py
```

Audit file SHA-256 values:

```text
audit_block_sum.py
49AA4CC2EC0DECAF0E63DCFECC0212294438AAA4EB51BADC095CF3499808D9F2

block_sum_audit_results.json
D50C9BDDA258D096C8ED851A2017AB803BE4455B3D2FBACD142BE0995E14E664

collect_tight_splits.py
731ED32E7638107A233BC4CCD58BECA162F303F3E8053AB54B538DD6FCD67BB7

tight_splits_first20.json
8CD58B4BD89494D6BD169958298432FF01BB098F36FCCFCB769967FF26B72119
```

Independent small-order verification:

```text
verify_block_sum_records.py
6E64E6513E8EE0C8AF3F5D0CEE3ACB9FC276A298A54D6BD2F6EFB66A31FDED06

block_sum_record_verification.json
D731B30E3427B4944B908B0E6BDFB3C613360A793E4750BFEB24D065B518A3FB
```

It independently checks (1.1)--(2.3), both rooted lower bounds on the graph
atlas cut cases of girth at least five, and every stated invariant of `F?bao`
and ``G?`e_w``; its result is `PASS`.