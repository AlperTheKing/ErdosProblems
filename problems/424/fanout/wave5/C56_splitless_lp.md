# C56: splitless-closed LP certificates

## Verdict

Let

\[
{\cal A}=\{n\ge 2:n\not\equiv1\pmod 3\}.
\]

For a cutoff `X`, consider every set `T subset A cap [2,X]` which contains
`2,3`, excludes every structural splitless nonseed, and is forward closed:

\[
a,b\in T,\quad a<b,\quad ab-1\le X
\quad\Longrightarrow\quad ab-1\in T.                 \tag{1}
\]

Write `H_T(X)` for the number of hard-shaped integers outside `T` and
`Q_T(X)` for the number of seed-2 boundary edges

\[
m\notin T,\qquad 2m-1\in T,\qquad 2m-1\le X.          \tag{2}
\]

The uniform statement

\[
H_T(X)\le Q_T(X)                                      \tag{SCB}
\]

has exact integer dual certificates for

\[
X\in\{54,100,200,500,1000,2000,5000,10000,20000,
50000,100000\}.                                       \tag{3}
\]

This is finite evidence and a discovery mechanism, not an asymptotic proof.
It is stronger than the image-set gate at each listed cutoff because it uses
only forward closure and exclusion of splitless nonseeds.

## LP formulation

Use membership variables `0 <= t_n <= 1`.  Fix `t_2=t_3=1`, and fix
`t_n=0` for every structural splitless nonseed.  For every admissible
distinct factorization `n+1=ab`, impose

\[
t_a+t_b-t_n\le1.                                     \tag{4}
\]

For every seed-2 edge introduce `0 <= q_(2m-1) <= 1` and impose the convex
hull of `q=(1-t_m)t_(2m-1)`.  Only its lower face is needed by the returned
duals:

\[
t_{2m-1}-t_m-q_{2m-1}\le0.                            \tag{5}
\]

Minimize

\[
\sum_{n\ {m hard}}t_n+\sum_m q_{2m-1}.              \tag{6}
\]

For Boolean membership, (6) equals `#hard - H_T(X) + Q_T(X)`.  A lower
bound by `#hard` is therefore exactly (SCB).  Since the dual certificate is
valid for the continuous relaxation, it proves the Boolean statement too.

## Exact results

HiGHS was used only to discover dual multipliers.  Every nonzero multiplier
rounded to an integer within `1e-7`.  The saved certificate was then checked
with Python integers: multiplier signs, every dual stationarity coordinate,
and the dual objective.

| X | hard | exact dual objective | margin |
|---:|---:|---:|---:|
| 54 | 1 | 1 | 0 |
| 100 | 3 | 4 | 1 |
| 200 | 8 | 8 | 0 |
| 500 | 27 | 33 | 6 |
| 1000 | 66 | 69 | 3 |
| 2000 | 147 | 147 | 0 |
| 5000 | 410 | 431 | 21 |
| 10000 | 878 | 920 | 42 |
| 20000 | 1864 | 2009 | 145 |
| 50000 | 4955 | 5465 | 510 |
| 100000 | 10294 | 11595 | 1301 |

The optimizer's primal solutions were integral at all eleven cutoffs.  This
integrality is not used for certification.  The exact duals use closure
rows, the lower boundary rows (5), and fixed/box bounds.  Thus the open
uniform theorem is an integer cut/flow statement hidden in (4)-(5), rather
than a factor-component Hall matching.

## Local mechanisms ruled out

C51 gives a Hall obstruction inside the genuine image `T=S_3=F(S_2)`.  At
`X=318`, allowing every arrived boundary in every canonical component of
every missing factor endpoint gives only

\[
\{54,74,186,318\}\longrightarrow\{41,57,63\}.        \tag{7}
\]

Thus any proof of (SCB) must move capacity between unrelated components.
The exact two-step birth-exit lemma still holds, but boundary `41` is used by
`7043` critical endpoints through `10^6`, so availability is not capacity.

A second exact test tried to pair hard holes with earlier boundaries sharing
a generated cofactor.  Through `10^6`, only `29582` of `45583` hard holes
were covered; `16001` were unmatched.  This simple cofactor transport is
therefore insufficient.

## Reproduction

Generate the dual certificates:

~~~powershell
python problems/424/compute/wave5/C56_dual_cert.py `
  --limits 54 100 200 500 1000 2000 5000 10000 `
  --generate problems/424/compute/wave5/C56_dual_cert.json `
  --summary problems/424/compute/wave5/C56_dual_cert_verify.json
~~~

Replay only the integer verifier:

~~~powershell
python -O problems/424/compute/wave5/C56_dual_cert.py `
  --verify problems/424/compute/wave5/C56_dual_cert.json `
  --summary problems/424/compute/wave5/C56_dual_cert_replay.json
~~~

The verifier uses explicit exceptions rather than `assert`, so `-O` does not
disable any check.

~~~text
C56_dual_cert.py
C0FB818E2EAC7F069DE4E8A4650E19A2F388FB391551607A7EE94EA71582E7DF

C56_dual_cert.json
C2B2AEFEC0BBF2141B023FA79AD76AD374E0E6A089FD0103AD2FB57475DCA38B

C56_dual_cert_replay.json
93FEB486B9E5CC7E423E8F12E12A07A170C051C7CDEDFC995034169F14557953

C56_dual_cert_100k.json
B5C89069C01715ED688670733C52F5731BCE4B6E59BB0ADF5EF7AE0938327BCA

C56_dual_cert_100k_replay.json
B0293CFD3E1305C26606A9A373F87471D1BA5E047D2271156FE79CDD407A22B6
~~~

## Frontier

Construct the dual multipliers for arbitrary `X`, or equivalently prove the
splitless-closed boundary theorem (SCB) by a global cut/flow or telescoping
argument.  C51 proves that a source-to-local-component injection cannot be
that argument.
