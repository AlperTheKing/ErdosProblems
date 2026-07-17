# C60: the C56 duals are contracted integer flows

## Verdict

The useful rule is global rather than bounded-local.  After contracting the
least generated set, an ordinary integer max flow produces a C56 dual using
only two kinds of internal arcs:

1. unlimited unary factor descents; and
2. unit-capacity seed-2 ascents.

This gives a canonical reverse-flow construction and an exact cut theorem.
It is sufficient for the splitless-closed boundary inequality whenever the
flow value reaches the number of hard holes.

The construction was checked at **every cutoff `2 <= X <= 2000`**.  At every
cutoff its exact flow lower bound equals the objective of a newly generated,
integer-verified C56 dual.  The same equality was independently checked by a
sparse integer max-flow implementation against the saved C56 duals at

```text
X = 5000, 10000, 20000, 50000, 100000.
```

No cutoff failed the required flow inequality.  This is still a finite
certificate family, not a proof for arbitrary `X`.

## 1. Contracted network

Fix `X`.  Let

\[
V_X=\{n\in[2,X]: n\not\equiv1\pmod3\}.
\]

For `n in V_X`, let `P(n)` be its admissible distinct factor pairs
`n+1=ab`.  Let `G_X` be the least subset of `V_X` containing `2,3` and
closed under these pairs.  Since `ab-1>a,b`, it is computed in increasing
order and agrees with the restriction of the infinite generated set.

Put

\[
M_X=V_X\setminus G_X,
\]

let `K_X` be the hard-shaped members of `M_X`, and let `E_X` be the
structural splitless nonseeds in `M_X`.

Build a capacitated directed network `N_X` with source `s`, sink `z`, and
one vertex for each member of `M_X`.

### Source arcs

For every hard hole `h in K_X`, add

\[
s\longrightarrow h \quad\hbox{with capacity }1.
\tag{S1}
\]

For every splitless node `e in E_X`, add

\[
s\longrightarrow e \quad\hbox{with capacity }\mathsf{Inf}.
\tag{S2}
\]

Here `Inf` is one plus the sum of all finite capacities, so no minimum cut
uses an `Inf` arc.

### Unary factor arcs

If `n in M_X` has a factorization

\[
n=gp-1,
\qquad g\in G_X,\quad p\in M_X,
\]

add

\[
n\longrightarrow p \quad\hbox{with capacity }\mathsf{Inf}.
\tag{U}
\]

Pairs with two hole endpoints are deliberately omitted.

### Seed arcs

For every `m in M_X` with `c=2m-1<=X`, add the unit arc

\[
m\longrightarrow
\begin{cases}
c,&c\in M_X,\\
z,&c\in G_X.
\end{cases}
\tag{D}
\]

Write `kappa_X` for the integral max-flow/min-cut value of `N_X`.

## 2. Exact flow lemma

### Lemma C60.1 (contracted-flow lower bound)

For the C56 continuous LP at cutoff `X`, let `Phi_X` denote its objective

\[
\Phi_X(t,q)=\sum_{h\text{ hard}}t_h+\sum_c q_c.
\]

Then every feasible point satisfies

\[
\boxed{
\Phi_X(t,q)\ge |G_X\cap\mathrm{Hard}_X|+\kappa_X.
}
\tag{1}
\]

Consequently,

\[
\boxed{
\kappa_X\ge |K_X|
\quad\Longrightarrow\quad
H_T(X)\le Q_T(X)
}
\tag{2}
\]

for every splitless-free forward-closed Boolean set `T` in the C56 class.

### Proof

Set `x_n=1-t_n`.  First, `t_g=1` for every `g in G_X`: this is true for
the seeds, and if `g=ab-1` with `t_a=t_b=1`, the closure row gives
`2-t_g<=1`, hence `t_g=1`.

Thus every unary arc (U), coming from `n=gp-1`, gives

\[
x_n\le x_p.
\tag{3}
\]

Every splitless node has `x_e=1`.  Every seed row gives

\[
q_{2m-1}\ge
x_m-x_{2m-1},
\tag{4}
\]

where the terminal value is interpreted as zero when `2m-1 in G_X`.

For `0<u<1`, define the threshold set

\[
S_u=\{m\in M_X:x_m>u\}.
\]

It contains every splitless node.  By (3), it is closed across every unary
arc, so the corresponding `s-z` cut uses no infinite arc.  Its capacity is

\[
|K_X\setminus S_u|
+
|\{m\to c\text{ a seed arc}:m\in S_u,\ c\notin S_u\}|.
\tag{5}
\]

The min-cut theorem bounds (5) below by `kappa_X`.  Integrating over
`0<u<1`, the first term becomes

\[
\sum_{h\in K_X}(1-x_h)=\sum_{h\in K_X}t_h,
\]

and the second becomes

\[
\sum_{m}(x_m-x_{2m-1})_+\le\sum_m q_{2m-1}
\]

by (4).  This proves

\[
\sum_{h\in K_X}t_h+\sum q\ge\kappa_X.
\]

Every generated hard value contributes exactly one to the objective, which
gives (1).  If `kappa_X>=|K_X|`, then

\[
\Phi_X\ge |G_X\cap\mathrm{Hard}_X|+|K_X|
=|\mathrm{Hard}_X|.
\]

For Boolean membership this is exactly `Q_T(X)>=H_T(X)`.  QED.

## 3. Integer dual construction

Because all capacities are integral, an integral max flow decomposes into
source-to-sink paths.

* A path beginning at a hard node transports that hard defect.
* A path beginning at a splitless node transports one unit of the fixed
  identity `x_e=1`; it may pay any hard defect through `x_h<=1`.
* Unary arcs may be reused with arbitrary multiplicity.  Their flow values
  are the C56 closure-row multipliers.
* Seed arcs have capacity one.  Their used-flow indicators are the C56
  `q_ge_difference` multipliers.

Generated factors on unary arcs have zero defect.  Expanding the recursive
proofs that their defects vanish lifts the contracted flow to the full C56
dual.  This explains the observed dual pattern:

1. every active boundary multiplier is `1`;
2. every active closure row is complementary at the least-set primal point:
   a generated output uses two generated factors, while a hole output uses
   exactly one generated and one hole factor;
3. closure multipliers can be large because many paths share the same
   generated proof tree.

This is a concrete reverse-flow construction.  It is not a local matching
inside a canonical factor component, consistent with the C51 obstruction.

## 4. Exact computation

### Every cutoff through 2000

For each of the 1999 cutoffs `2,...,2000`:

1. C56 was solved anew by HiGHS;
2. every nonzero dual marginal rounded to an integer within `1e-7`;
3. `C56_dual_cert.verify_one` checked signs, every stationarity coordinate,
   and the objective using Python integers;
4. a separate incremental integer max-flow implementation computed
   `kappa_X`; and
5. the exact identity

\[
\boxed{
\text{C56 dual objective}
=|G_X\cap\mathrm{Hard}_X|+\kappa_X
}
\tag{6}
\]

held at every cutoff.

The minimum of `kappa_X-|K_X|` was zero.  At `X=2000`,

```text
hard holes       97
generated hard   50
splitless       298
kappa_X           97
C56 objective    147
```

Two complete executions, one with `python` and one with `python -O`, produced
byte-identical JSON.

### Independent large replay

`C60_large_flow.py` uses `scipy.sparse.csgraph.maximum_flow` on an integer
sparse capacity matrix, independently of the custom incremental flow code.

| X | hard holes | generated hard | exact flow | reserve | predicted/saved C56 objective |
|---:|---:|---:|---:|---:|---:|
| 5,000 | 253 | 157 | 274 | 21 | 431 |
| 10,000 | 518 | 360 | 560 | 42 | 920 |
| 20,000 | 1,063 | 801 | 1,208 | 145 | 2,009 |
| 50,000 | 2,625 | 2,330 | 3,135 | 510 | 5,465 |
| 100,000 | 5,108 | 5,186 | 6,409 | 1,301 | 11,595 |

Every predicted objective equals the saved exact C56 dual objective.

## 5. What is and is not incremental

The network itself is incremental: increasing `X` only adds vertices, arcs,
and source capacity.  Standard residual augmentation therefore gives an
exact recurrence.  It is global and sometimes reroutes old flow.

For the deterministic breadth-first recurrence in `C60_dual_patterns.py`,
the first reroute is at `X=377`:

```text
s -> 144 -> 287 -> 32 -> 95 -> 189 -> z
     hard   seed    unary  reverse(unary 95->32)  seed  seed-to-377
```

Thus that canonical incremental flow cannot be updated merely by appending
one untouched forward path.  The longest augmenting path through `2000`
appears at `X=1689` and has nine arcs:

```text
s -> 398 -> 795 -> 1589 -> 530 -> 1059 -> 212 -> 423 -> 845 -> z.
```

The statement here is about this deterministic recurrence; it does not prove
that every possible choice of earlier max flow must reroute.

## 6. Minimal obstructions to raw/local dual templates

The exact C56 duals selected independently at adjacent cutoffs are not an
append-only family.

1. **First boundary deletion:** `328 -> 329` removes
   `q_ge_difference_21`, while both exact objectives remain `18`.
2. **First old selector switch:** `634 -> 635` changes the row for output
   `188` from `closure_188_9_21` to `closure_188_3_63`.
3. **First multi-selector output:** at `X=1017`, both closure rows for output
   `188` occur simultaneously with multiplier one.  This persists through
   `X=1022`.
4. **Unbounded observed multiplicity:** the largest closure multiplier is
   `403` through `X=2000`; in the saved `X=100000` exact dual,
   `closure_5_2_3` has multiplier `43371`.
5. **Expanded-dual nonlocality:** the update `1988 -> 1989` changes an old
   coefficient at label `2`, a backreach of `1987`.

Items 1-3 are exact minimal falsifiers to the corresponding rules for the
solver-generated dual sequence.  They do not exclude a different globally
chosen dual basis.  The contracted flow is the basis-independent object.

## 7. Remaining proof target

The C56 frontier can now be stated without floating-point LP language:

> Prove `kappa_X >= |K_X|` for every `X`, where `kappa_X` is the max-flow
> value of the explicit arithmetic network `N_X` above.

Equivalently, every finite cut containing all splitless roots and closed
under unary generated-factor descent must have at least as many outgoing
seed arcs as the hard holes it contains.

This cut theorem is stronger than the original Boolean closure gate because
it omits all two-hole factor constraints.  The exact equality (6) through
`100000` says those omitted constraints have not affected the optimum in any
tested instance.  An asymptotic proof of the cut theorem is still missing.

## 8. Reproduction

~~~powershell
python problems/424/fanout/wave5/C60_dual_patterns.py `
  --max-limit 2000 --workers 32 --all-lp `
  --output problems/424/fanout/wave5/C60_dual_patterns_2000.json

python -O problems/424/fanout/wave5/C60_dual_patterns.py `
  --max-limit 2000 --workers 32 --all-lp `
  --output problems/424/fanout/wave5/C60_dual_patterns_2000_replay.json

python problems/424/fanout/wave5/C60_large_flow.py `
  --limits 5000 10000 20000 50000 100000 `
  --output problems/424/fanout/wave5/C60_large_flow_100k.json

python problems/424/fanout/wave5/C60_extract_obstructions.py `
  --patterns problems/424/fanout/wave5/C60_dual_patterns_2000.json `
  --output problems/424/fanout/wave5/C60_obstructions.json
~~~

~~~text
C60_dual_patterns_2000.json
49E1112F3E3C8D9D40BAA5E2F123C8513C5FB7027E0B652C841A1D37A8E0CDCC

C60_dual_patterns_2000_replay.json
49E1112F3E3C8D9D40BAA5E2F123C8513C5FB7027E0B652C841A1D37A8E0CDCC

C60_large_flow_100k.json
BF34772D1C146D3526DB8BC55ACD1E702AD6C77F755E4B76C7C451D34FFEEC67

C60_obstructions.json
21294C24395D0D6B3D7C0209C04C4D555B88DBE5A11C9F82F144CD2514395E76
~~~
