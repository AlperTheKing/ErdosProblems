# C73: persistent hard tails are equivalent to hard-hole sparsity

## Statement

Let `H(X)` count hard holes through `X`, using the definitions in C67, and
let `A_H(X)` count hard roots whose literal seed-2 chain remains missing up
to `X`. Then, for every integer `X>=2`,

\[
 H(X)-H\!\left(\left\lfloor{X+1\over2}\right\rfloor\right)
 \le A_H(X)\le H(X).                                  \tag{1}
\]

Consequently,

\[
 A_H(X)=o(X)\quad\Longleftrightarrow\quad H(X)=o(X). \tag{2}
\]

Thus the cut-independent C67 tail-bank target

\[
 A_H(X)\le E(X)-E(\lfloor X/2\rfloor)+o(X)
\]

is asymptotically equivalent to proving that all hard holes have density
zero, because C13 already proves `E(X)=o(X)`. The zero-error finite inequality
remains stronger, but its `o(X)` version is not a shortcut around hard-hole
sparsity.

## Proof

The upper bound in (1) is immediate: every chain counted by `A_H(X)` has a
distinct hard root at most `X`.

For the lower bound, let `r` be a hard hole with

\[
 \left\lfloor{X+1\over2}\right\rfloor<r\le X.
\]

Then `2r-1>X`. Hence the only member of the literal seed-2 chain rooted at
`r` that is at most `X` is `r` itself. Since `r` is a hole, this root is
counted by `A_H(X)`. Distinct roots give distinct chains, proving (1).

If `H(X)=o(X)`, the upper bound in (1) gives `A_H(X)=o(X)`. Conversely,
suppose `A_H(X)=o(X)`. Put `Y_0=X` and

\[
 Y_{j+1}=\left\lfloor{Y_j+1\over2}\right\rfloor.
\]

Applying the lower bound in (1) at `Y_j` and telescoping gives

\[
 H(X)\le \sum_{j:Y_j\ge Y_*} A_H(Y_j)+O(H(Y_*))
\]

for every fixed threshold `Y_*`. Given `epsilon>0`, choose `Y_*` so that
`A_H(Y)<=epsilon Y` for every `Y>=Y_*`. Since
`sum_j Y_j<=2X+O(log X)`, we obtain

\[
 H(X)\le 2\epsilon X+o(X)+O(H(Y_*)).
\]

Letting `epsilon` tend to zero proves `H(X)=o(X)`. This proves (2).

## Exact audit

`C73_tail_bank_equivalence.py` reconstructs the C67 arithmetic data and
checks both inequalities in (1) at every cutoff through a requested bound.
It is only a regression check; the proof above is unconditional.
