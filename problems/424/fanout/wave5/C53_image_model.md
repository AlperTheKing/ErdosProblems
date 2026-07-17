# C53: exact descending-image abstract model

## Verdict

The image/rank-prefix bridge does **not** follow from exact descending-image
dynamics, ordered distinct-parent multiplication, parity, residues modulo
`9`, exact seed-3 availability, or the canonical cap-two construction.

There is an exact 21-vertex abstract model at rank cutoff `d=2` with

\[
H_{\le2}=2,\qquad Q_{\le2}=Q^{(2)}_{\le2}=0.
\]

It is smallest in this axiom class. CP-SAT proves every rank cutoff
`d=0,...,19` infeasible at size 20 for both additive-one and cap-two. A
top-vertex extension preserves any smaller countermodel, so size-20
infeasibility excludes every smaller size.

This is **not** a counterexample in the integer set `G`. Exact propagation of
the equations `v_c+1=v_a v_b` makes the witness inconsistent. The first
machine-reported obstruction is `v_4=58/5`; an explicit integral collision
contradiction is given below. Thus the result is a precise obstruction:
these image-prefix axioms still omit global arithmetic compatibility of the
actual multiplication table.

## 1. Exact model

Let `V={0,...,N-1}` in coordinate order, with seeds `0,1` representing
`2,3`, and let `infinity=N`. For every unordered pair of distinct vertices
`a<b`, the model has one value

\[
\mu(a,b)\in\{b+1,\ldots,N\}.
\]

A value below `N` is the abstract output `ab-1`; `N` means that the output
is beyond the modeled prefix. The following constraints are imposed.

1. `mu` is strictly increasing in either parent while the larger product is
   finite; equality is allowed only at the common overflow value.
2. Every finite output has the exact product parity and residue modulo `9`.
   Vertex residues lie in `{0,2,3,5,6,8}`.
3. `mu(0,1)` is finite. Every nonseed odd vertex has exactly one seed-2
   predecessor.
4. Every reducible even vertex in residue `5` or `8 mod 9` has exactly its
   seed-3 factorization. Reducible even vertices in residues
   `0,2,3,6 mod 9` are hard-shaped. This includes the full mod-9 distinction
   that rules out treating `9q-1` as hard.
5. Starting with `S_0=V`, every stage is an exact biconditional, not a Horn
   relaxation:

\[
S_{t+1}=\{0,1\}\cup
\{\mu(a,b)<N:a,b\in S_t\}.
\]

6. The fixed point, death ranks, hard events, terminal seed-2 targets,
   canonical roots, and first two targets of each root are all derived from
   this table. No hard, target, rank, or cap-two label is selectable.

All parent pairs use `a<b`; equal inputs never occur.

## 2. Smallest falsifier

For the additive-one witness, the even vertices are

```text
0,3,4,8,16,17,18,19,20
```

and the residues modulo `9`, in vertex order, are

```text
2,3,5,6,8,0,2,6,5,8,3,2,0,6,5,3,8,5,8,0,2.
```

The complete finite part of `mu` is below. Every unlisted distinct pair
overflows.

```text
0*1->2   0*2->5   0*3->6   0*4->7   1*2->8
0*5->9   1*3->9   0*6->10  0*7->11  2*3->11
0*8->12  0*9->13  0*10->14 1*4->14  0*11->15
2*4->15  1*5->16  1*6->17  1*7->18  2*5->18
2*6->19  2*7->20
```

Independent replay gives the only changing stages:

```text
S0 = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20}
S1 = {0,1,2,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20}
S2 = {0,1,2,5,8,9,10,11,12,13,14,15,16,17,18,19,20}
S3 = {0,1,2,5,8,9,12,13,14,15,16,18}
S4 = {0,1,2,5,8,9,12,13,16,18} = G_abs.
```

The holes and ranks are

```text
rank 0: 3,4
rank 1: 6,7
rank 2: 10,11,17,19,20
rank 3: 14,15
```

Vertices `19,20` are the two hard rank-two events, using pairs `(2,6)` and
`(2,7)`. There is no terminal seed-2 target in the prefix, hence

\[
H_{\le2}-Q_{\le2}=H_{\le2}-Q^{(2)}_{\le2}=2.
\]

The separately optimized cap-two instance also first occurs at size 21 and
rank 2. The additive-one witness above already falsifies cap-two because
`Q^(2)<=Q`.

## 3. Minimality certificate

For each objective, the final run contains 23 exact solver statuses:

```text
size 20, d=0,...,19: 20 INFEASIBLE
size 21, d=0,1:       2 INFEASIBLE
size 21, d=2:         1 OPTIMAL witness
```

The additive-one run used 725,699 branches and 108,940 conflicts in
137.660 solver-seconds. The cap-two run used 713,354 branches and 107,622
conflicts in 143.850 solver-seconds.

To exclude unsearched smaller sizes, extend any size-`n` model to size
`n+1` as follows. Replace every old overflow `n` by `n+1`; add vertex `n`
as an even, residue-zero, splitless vertex; and send every pair incident to
it to overflow. All old finite products, stages, ranks, roots, and event
counts remain unchanged. The new point is a rank-zero nonhard hole with no
target. Thus every smaller violation would extend to size 20, contradicting
the all-rank size-20 infeasibility certificates.

## 4. Why this is not an integer falsifier

Suppose the abstract vertices had increasing integer values `v_i`, with
`v_0=2`, `v_1=3`, and every finite edge satisfying

\[
v_c=v_av_b-1.
\]

The displayed table forces

```text
v2=5, v5=9, v9=17, v3=6, v6=11, v10=21, v14=41, v4=14,
v11=29, v15=57.
```

But edge `2*4->15` then requires

\[
v_{15}=5\cdot14-1=69,
\]

contradicting `v15=57`. Equivalently, propagating from `v15=57` through
that edge gives the machine certificate `v4=(57+1)/5=58/5`.

Therefore the abstract table is not realizable by integer multiplication.
The missing bridge is now precise: any proof of additive one or cap-two must
use arithmetic compatibility beyond exact images, order, parity, mod `9`,
and seed-chain structure. In particular it must exclude incompatible global
product collisions such as the one above; generic descending-image or
forward-closure arguments cannot do so.

## 5. Actual-prefix verification

The same independent replay was instantiated with every allowed integer in
the indicated real prefix and with the literal product `ab-1`. Its fixed
point was checked against a separate increasing least-closure recursion.

| integer cutoff | vertices | generated | holes | max `H-Q` | max `H-Q2` |
|---:|---:|---:|---:|---:|---:|
| 74  | 49  | 16  | 33  | 0  | 0  |
| 186 | 124 | 40  | 84  | 0  | 0  |
| 362 | 241 | 78  | 163 | 1  | 1  |
| 500 | 333 | 119 | 214 | -3 | -3 |

At `(X,d)=(362,2)` the replay gives exactly 11 hard values and 10 target
children, reproducing the known tight additive constant. Every validation
uses distinct inputs only. No actual-prefix counterexample is claimed.

## 6. Reproduction

From the repository root:

```powershell
python problems/424/fanout/wave5/C53_image_model.py `
  --min-size 20 --max-size 21 `
  --actual-limits 74 186 362 500 `
  --output problems/424/fanout/wave5/C53_image_model.json
```

The run used OR-Tools `9.14.6206`, one CP-SAT worker, random seed `42453`,
and no solver time limit. `UNKNOWN` is never classified as infeasible.

```text
C53_image_model.py   A76B243C535244E7DEBCB173D20EC8D704D19E6D9C9655D3128ACB376E940617
C53_image_model.json 27671130A644742D37718ED4B2271FBBF7B82023610FF409864EB6A09809CAF6
```
