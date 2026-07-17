# C91: common healed-bank reduction

## Verdict

Fix a cutoff `X`.  Let `A_H(X)` be the number of hard seed-2 roots whose
literal chain top through `X` is still a hole.  Let `D(X)` be the size of the
universal common bank in the exact C87 Horn graph: the target roots `r` for
which, for every hard root `h` and every forward-closed set `T` containing
`G`,

`top_X(h) notin F(T)` implies
`r notin F(T)` and `top_X(r) in F(T)`.

Grounded structural splitless roots are automatic members of this bank.
The definition also retains any factorable target satisfying the same exact
Horn implication, rather than assuming such targets never occur.

The following arithmetic estimate is sufficient for the density theorem:

\[
  A_H(X)\le cD(X)+o(X)\qquad\text{for some fixed }c<4/3.       \tag{CB}
\]

Indeed, `(CB)` implies the uniform C67 cut estimate

\[
  H(S)\le cQ(S)+o(X)
\]

for every Boolean-realizable source side.  C67 then gives `M(X)=o(X)` and
generated-set density `2/3`.  In particular, either

\[
  4D(X)>3A_H(X)\quad(A_H(X)>0)                               \tag{CB4}
\]

or the stronger candidate

\[
  6D(X)\ge5A_H(X)                                           \tag{CB6}
\]

would close Erdős Problem 424.

No proof of `(CB)`, `(CB4)`, or `(CB6)` is claimed here.  Exact computation
finds no failure of `(CB6)` at any of the 878 hard-root event cutoffs through
`10000`; equality occurs at `X=186` and `X=204`.  This is finite evidence.

## Lemma C91.1 (every common-bank root is a boundary)

Let `S` be a Boolean-realizable C67 source side and suppose `U_H(S)>0`.
Then every root counted by `D(X)` is a healed root of `S` and hence
contributes one distinct seed boundary to `Q(S)`.  Consequently

\[
  Q(S)\ge B_H(S)+D(X).                                      \tag{1}
\]

### Proof

Write `T` for the forward-closed set whose one-step image has complement
`S`.  Choose any unhealed hard root `h`; then `top_X(h) notin F(T)`.  The
defining C87 implication now gives, simultaneously for every common-bank root
`r`,

`r notin F(T)` and `top_X(r) in F(T)`.

Along the literal chain from `r` to its top there is therefore a first seed
edge leaving the source side.  Distinct roots have disjoint seed-2 chains, so
these are `D(X)` distinct boundaries.  Every healed hard root supplies one
further boundary on a hard chain, disjoint from every nonhard target chain.
This proves (1).

## Lemma C91.2 (conditional contraction)

Assume `(CB)` for some fixed `1<=c<4/3`.  Then, uniformly over all
Boolean-realizable source sides,

\[
  H(S)\le cQ(S)+o(X).                                      \tag{2}
\]

### Proof

If `U_H(S)=0`, the C67 identity gives `H(S)=B_H(S)<=Q(S)`.
Otherwise Lemma C91.1 applies.  Since every unhealed hard root is counted by
`A_H(X)`,

\[
\begin{aligned}
H(S)&=U_H(S)+B_H(S)\\
    &\le A_H(X)+B_H(S)\\
    &\le cD(X)+B_H(S)+o(X)\\
    &\le c\bigl(D(X)+B_H(S)\bigr)+o(X)\\
    &\le cQ(S)+o(X).
\end{aligned}
\]

The last two inequalities use `c>=1` and (1).  C67.2 then yields

\[
 M(X)\le cM(\lfloor(X+1)/2\rfloor)
        +M(\lfloor(X+1)/3\rfloor)+o(X).
\]

Its normalized coefficient is `c/2+1/3<1`, so `M(X)=o(X)`.

## Exact finite gate

`C91_common_bank_scan.py` reconstructs the C87 Horn model at every hard-root
event cutoff supplied by the C71 gate and counts the intersection of all hard
adjacency lists.  By the proved C87 Horn characterization, this is exactly
`D(X)`.  In particular, every grounded structural splitless root is included
because its factor condition is vacuous.

For the 878 cutoffs through `10000`:

* `(CB4)` has zero failures;
* `(CB6)` has zero failures;
* the minimum ratio is `D/A_H=5/6` at `X=186` and `X=204`;
* at `X=10000`, `A_H=391` and `D=374`.

The exact scan artifact is `C91_common_bank_10000.json`.  These rows neither
prove the all-`X` inequality nor replace its missing arithmetic mechanism.
