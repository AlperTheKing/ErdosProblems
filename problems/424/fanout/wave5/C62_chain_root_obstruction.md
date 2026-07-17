# C62: exact obstruction to chain-local root transport

## Verdict

The seed-2 chain identity does not admit a source-local injection, even if
the local reachability relation is closed under every admissible
factorization met anywhere on the missing part of a seed-2 chain.

At `X=74` there is a genuine infinite forward-closed, splitless-free set
`T` for which

\[
 H_T(74)=Q_T(74)=2,
\]

but the two unhealed hard roots have only one reachable healed nonhard root.
The second unit of credit is supplied by an arithmetically unrelated
splitless bank.  Thus neither direct missing-factor descent nor its full
chain-local transitive closure can prove SCB by an injection or unit
discharge.

This is an obstruction to the requested proof mechanism, not a
counterexample to SCB.  Exact min-cut probes still give nonnegative SCB
margins through `X=1,000,000`.

## 1. Full chain-local descent

Write

\[
 U(n)=2n-1.
\]

For an allowed integer `q`, let `root(q)` be the unique even integer obtained
by repeatedly replacing an odd value `z` by `(z+1)/2`.  Thus `q` lies on
the seed-2 chain rooted at `root(q)`.

Fix a forward-closed set `T` and a cutoff `X`.  For an even root `r` outside
`T`, inspect the initial segment

\[
 r,U(r),U^2(r),\ldots
\]

through `X`, stopping just before its first member of `T`, if one occurs.
For every inspected value `n` and every admissible factorization

\[
 n+1=ab,
\]

draw an edge from `r` to `root(q)` for each endpoint
`q in {a,b}` outside `T`.  Let `Reach_X(r)` be the transitive closure of
these edges.

This is deliberately stronger than direct hard-factor descent.  It includes:

1. every missing endpoint of every factorization of the hard root;
2. the deterministic seed-3 descent of a nonhard nonsplitless root;
3. every unary implication having a present cofactor;
4. every such implication at every later missing point on a seed-2 chain.

A nonhard root `r` is healed when `r` is outside `T` but the top
`W_X(r)` of its seed-2 chain in `(floor((X+1)/2),X]` belongs to `T`.

## 2. Obstruction lemma

**Lemma (chain-local Hall obstruction).**  There is an infinite set `T`
satisfying all SCB hypotheses and a cutoff `X=74` such that the unhealed
hard roots are

\[
 \{54,74\},
\]

the healed nonhard roots are

\[
 \{6,18\},
\]

and

\[
 Reach_{74}(54)\cap\{6,18\}
 =Reach_{74}(74)\cap\{6,18\}=\{6\}.             \tag{1}
\]

Consequently the chain-local reachability graph has the Hall-deficient set

\[
 \{54,74\}\longrightarrow\{6\}.                 \tag{2}
\]

In particular, no injection from unhealed hard roots to healed nonhard
roots can be required to follow full chain-local descent.

### Proof

Let `T` be the least forward-closed subset of the allowed integers containing

\[
 S=\{2,3,21,32,35,62,63,68\}.                    \tag{3}
\]

Every nonseed in `S` has an admissible factorization:

\[
22=2\cdot11,\quad33=3\cdot11,\quad36=3\cdot12,
\quad63=3\cdot21,\quad64=2\cdot32,\quad69=3\cdot23.
\]

Every later element of `T` is, by definition, the output of an admissible
factorization.  Hence no structural splitless nonseed belongs to `T`.
The set contains `2,3` and is forward closed, so it satisfies all SCB
hypotheses.

Direct closure of (3) gives

\[
\begin{split}
T\cap[2,74]=\{&2,3,5,9,14,17,21,26,27,32,33,35,41,44,50,51,\\
               &53,62,63,65,68,69\}.             \tag{4}
\end{split}
\]

For completeness, all products of two distinct members of (4) that do not
exceed `75` are exhausted by

\[
\begin{array}{c|l}
2 & 3,5,9,14,17,21,26,27,32,33,35\\
3 & 5,9,14,17,21\\
5 & 9,14.
\end{array}
\]

Their outputs are respectively

\[
\begin{array}{l}
5,9,17,27,33,41,51,53,63,65,69,\\
14,26,41,50,62,\\
44,69,
\end{array}
\]

all in (4).  This proves both inclusion directions in (4).

The even allowed values at most `74` are the residues `0,2 mod 6`.
For residue `0 mod 6`, checking `n+1` leaves only
`55=5*11`, hence the only hard value is `54`.  For residue `2 mod 6`, the
seed-3 factorization applies whenever its cofactor is allowed; the only
remaining reducible case is

\[
75=5\cdot15,
\]

because the alternative cofactor in `75=3*25` is forbidden.  Hence the hard
shapes through `74` are exactly `54,74`, and (4) shows both are outside
`T`.  Since both exceed `floor(75/2)=37`, their chain tops are themselves,
so they are unhealed.

The holes at most `37` are

\[
6,8,11,12,15,18,20,23,24,29,30,36.
\]

Their seed-2 children are

\[
11,15,21,23,29,35,39,45,47,57,59,71.
\]

Only `21` and `35` lie in (4).  Thus the boundary parents are `11,18`, so
`Q_T(74)=2`.  In root coordinates these are the healed splitless roots
`6` and `18`.  Therefore `H_T(74)=Q_T(74)=2`.

It remains to compute the full descent closure.  The missing chain segments
and their admissible factorizations are:

\[
\begin{array}{c|c|c}
\text{root}&\text{missing chain segment}&\text{factorizations beyond the seed-2 edge}\\
54&54&55=5\cdot11\\
74&74&75=5\cdot15\\
8&8,15,29,57&30=5\cdot6\\
6&6,11&\text{none}.
\end{array}
\]

Here `root(11)=6` and `root(15)=8`.  Thus

\[
 Reach_{74}(54)=\{54,6\},\qquad
 Reach_{74}(74)=\{74,8,6\}.                     \tag{5}
\]

Intersecting (5) with the healed-root set `{6,18}` proves (1), and (2)
follows.  QED.

## 3. Consequence for the proof frontier

The exact shell identity is still valid:

\[
H_T(X)-Q_T(X)
=\#\{\text{unhealed hard roots}\}
-\#\{\text{healed nonhard roots}\}.
\]

The lemma proves that the required comparison cannot be obtained by sending
each hard unit down all arithmetic factor descents available in its own
seed-2 component.  At `X=74`, the second credit is the unrelated bank rooted
at `18`.  A valid proof must therefore establish a global bank inequality or
permit transfers through present-side arithmetic; source-local descent is
insufficient even after transitive closure.

The stronger statement SCB itself was not falsified.  The exact contracted
min-cut values at larger cutoffs are:

| X | hard-hole demand | exact flow | reserve |
|---:|---:|---:|---:|
| 200,000 | 9,937 | 12,967 | 3,030 |
| 500,000 | 23,768 | 32,457 | 8,689 |
| 1,000,000 | 45,583 | 64,649 | 19,066 |

These are finite checks only.

## 4. Reproduction

The obstruction uses no optimizer and replays under `python -O`:

```powershell
python -O problems/424/fanout/wave5/C62_exact_obstruction.py
```

The larger finite probes are reproduced by:

```powershell
python problems/424/fanout/wave5/C60_large_flow.py `
  --limits 200000 500000 1000000 `
  --output problems/424/fanout/wave5/C62_large_flow_probe.json
```

SHA-256:

```text
C62_exact_obstruction.py
C9C8AE672A174589A5D3D83B23D2DDF3A051078044897BB58B6259EC92DAE55D

C62_exact_obstruction.json
91DEC8FF75691D3A60385BC70BCB22BAD77A1B5302C6F42E33DCBF52EF3619C3

C62_chain_probe.py
58F7C6B8E6E6F12472D5532FE70ED581F92E2378C45BAA12A6D94EEBA9BCD485

C62_large_flow_probe.json
9BF69FEDD80586DF0E8E9CC3F40620031937FDE0725B0720FA073E7CF2D93EA0
```
