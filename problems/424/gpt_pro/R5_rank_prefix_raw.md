# GPT-Pro R5: shell identity and forward-closure obstruction

## Verdict

The response does not prove the requested rank-prefix inequality, the earlier
image inequality `(I)`, an image counterexample `T = F(S)`, or the one-step
preservation theorem. It gives an exact shell identity for arbitrary
forward-closed sets and a finite example showing that forward closure alone
does not imply the required inequality.

## Exact shell identity

Let `T` be any forward-closed subset of

\[
\mathcal A=\{n\ge 2:n\not\equiv 1\pmod 3\}
\]

containing `2,3`. Put

\[
h(n)=\mathbf 1_{\{n\notin T\}},\qquad
Y=\left\lfloor\frac{X+1}{2}\right\rfloor,
\qquad U(m)=2m-1.
\]

Since `m in T` implies `U(m) in T`, one has
`h(U(m)) <= h(m)`. Consequently,

\[
Q_T(X)=
\sum_{\substack{m\in\mathcal A\\m\le Y}}
\bigl(h(m)-h(U(m))\bigr).                              \tag{1}
\]

The map `m -> U(m)` is a bijection from
`A intersect [2,Y]` onto the odd elements of `A intersect [3,X]`. Hence

\[
Q_T(X)=
\sum_{\substack{m\in\mathcal A\\m\le Y}}h(m)
-
\sum_{\substack{n\in\mathcal A\\n\le X\\n\text{ odd}}}h(n).
\]

Subtracting this from the hard-hole count and cancelling the lower-half odd
and hard terms gives

\[
\begin{aligned}
H_T(X)-Q_T(X)
={}&\#\{n\in(Y,X]:n\text{ odd},\ n\in\mathcal A\setminus T\}\\
&+\#\{n\in(Y,X]:n\text{ hard-shaped},\ n\notin T\}\\
&-\#\{n\le Y:n\text{ even and nonhard},\ n\in\mathcal A\setminus T\}.
                                                               \tag{2}
\end{aligned}
\]

There is an equivalent chain form. For every even `r <= X`, there is a
unique `k=k_X(r)>=0` such that

\[
W_X(r):=1+2^k(r-1)\in(Y,X].                            \tag{3}
\]

The `U`-chain rooted at `r` contributes as follows:

- if `r` is hard-shaped, it contributes `+1` exactly when `W_X(r) notin T`;
- if `r` is nonhard, it contributes `-1` exactly when
  `r <= Y`, `r notin T`, and `W_X(r) in T`;
- otherwise it contributes zero.

Therefore

\[
\begin{aligned}
H_T(X)-Q_T(X)
={}&\#\{r\le X:r\text{ even and hard},\ W_X(r)\notin T\}\\
&-\#\{r\le Y:r\text{ even and nonhard},\ r\notin T,\ W_X(r)\in T\}.
                                                               \tag{4}
\end{aligned}
\]

For an image set `T=F(S)`, the earlier target `(I)` is exactly the assertion
that the second set in (4) always has cardinality at least that of the first.
The response supplies no capacity map or prefix majorization proving this.

## Forward closure alone fails

Define

\[
I=\{6,8,11,15,29,54,57,74\},\qquad T_0=\mathcal A\setminus I.
\]

Then `T_0` is forward closed. Every admissible distinct factorization of
`n+1`, for `n in I`, contains another member of `I`:

| `n` | admissible distinct factorizations of `n+1` |
|---:|:---|
| 6 | none |
| 8 | none; `9=3^2` uses equal factors |
| 11 | `12=2*6` |
| 15 | `16=2*8` |
| 29 | `30=2*15=5*6` |
| 54 | `55=5*11` |
| 57 | `58=2*29` |
| 74 | `75=5*15` |

The alternative `75=3*25` is inadmissible because `25 notin A`. Hence
`F(T_0) subset T_0`.

At `X=74`, both `54` and `74` are hard-shaped, so `H_{T_0}(74)=2`.
The holes at most `37` are `6,8,11,15,29`; their `U`-children are
`11,15,21,29,57`. Exactly one, `21=U(11)`, belongs to `T_0`. Thus

\[
Q_{T_0}(74)=1<2=H_{T_0}(74).                            \tag{5}
\]

This is not an image counterexample. Although `12 in T_0`, the number
`13=12+1` has no admissible factorization, so `12 notin F(S)` for every `S`.
Therefore `T_0` cannot equal `F(S)`.

## Remaining point

The image condition would have to convert the unavoidable absence of every
splitless nonseed element into the negative prefix surplus in (4). The
response does not prove that conversion; asserting it without an explicit
capacity argument would merely restate `(I)`.
