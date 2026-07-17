# GPT-Pro R7: top-strip perturbation theorem

## Verdict returned by GPT-Pro

GPT-Pro did not obtain a proof of the splitless-closed boundary theorem
`(SCB)`, nor an explicit forward-closed splitless-free counterexample.  It
gave the following exact perturbation theorem and upper-shell identity.

## Top-strip perturbation theorem

Let `G` be the least closure, fix `X`, and put

\[
Y=\left\lfloor\frac{X+1}{2}\right\rfloor.
\]

Define `B_X` to be the set of integers `m` satisfying

\[
\frac{X+1}{3}<m\le \frac{X+1}{2},                       \tag{1}
\]

such that `m` is allowed, even, reducible and nonhard-shaped, and

\[
m\notin G,\qquad 2m-1\in G.                              \tag{2}
\]

For any `C subset B_X`, let `T_C` be the least forward-closed subset of the
allowed integers containing `G union C`.  Then `T_C` contains `2,3`, excludes
every splitless nonseed, and

\[
T_C\cap[1,X]=(G\cap[1,X])\cup C.                         \tag{3}
\]

Moreover,

\[
H_{T_C}(X)=H_G(X),                                       \tag{4}
\]

and

\[
Q_{T_C}(X)=Q_G(X)-|C|.                                  \tag{5}
\]

Consequently,

\[
H_{T_C}(X)-Q_{T_C}(X)=H_G(X)-Q_G(X)+|C|.                \tag{6}
\]

In particular, an explicit counterexample to `(SCB)` follows from any `X`
for which

\[
|B_X|>Q_G(X)-H_G(X).                                     \tag{7}
\]

### Proof

Every member of `B_X` is nonsplitless.  Every element introduced while
closing `G union C` is of the form `ab-1` with `2<=a<b` allowed, so closure
cannot introduce a splitless nonseed.

Suppose a new element at most `X` is produced using `m in C`.  If the other
input is `2`, the output `2m-1` is already in `G`.  If the other input is at
least `3`, (1) gives `3m-1>X`.  An element produced above `X` cannot later
produce an element at most `X`, because `ab-1>=b`.  This proves (3).

Every `m in C` is nonhard-shaped, proving (4).  Before adjoining `m`, the
edge `m -> 2m-1` contributes one to `Q_G(X)`; afterward it does not.  Since
`m` is even, it is not itself a seed-2 child.  By (3), no other membership
through `X` changes.  The effects are independent, proving (5) and (6).

## Exact upper-shell identity

Put `t_n=1_{n in T}` and let `H_X` denote all hard-shaped integers through
`X`.  Define

\[
P_X=\{n:\ Y<n\le X,\ n\text{ allowed and odd}\}
 \cup \{n\in H_X:\ Y<n\le X\},
\]

and

\[
N_X=\{n:\ n\le Y,\ n\text{ allowed, even and nonhard-shaped}\}.
\]

Then

\[
Q_T(X)-H_T(X)=\sum_{p\in P_X}t_p-
               \sum_{r\in N_X}t_r-|H_X|.               \tag{8}
\]

Equivalently, write `U^k(r)=1+2^k(r-1)`.  For every even `r<=X`, let
`W_X(r)` be the unique `U^k(r)` in `(Y,X]`.  Telescoping the seed-2 boundary
along each `U`-chain gives

\[
Q_T(X)-H_T(X)
=\sum_{\substack{r\le X\\r\text{ hard}}}(t_{W_X(r)}-1)
 +\sum_{\substack{r\le Y\\r\text{ even, nonhard}}}
   (t_{W_X(r)}-t_r).                                    \tag{9}
\]

Thus `(SCB)` is equivalent to the upper-shell inequality

\[
\sum_{p\in P_X}t_p\ge |H_X|+\sum_{r\in N_X}t_r.         \tag{10}
\]

GPT-Pro did not prove (10); it explicitly noted that presenting the
remaining reachability-capacity inequality as a theorem would only restate
the unresolved part of `(SCB)`.

## Codex audit status

The formulas above were transcribed from the completed rendered response.
`R7_top_strip_audit.py` is the independent exact gate for (3)--(10) and the
decisive counterexample condition (7).  The audit checked every cutoff through
`10^6`, found zero shell-identity failures, and explicitly rebuilt the
perturbed closure at eight cutoffs.  No counterexample condition occurred.
At `X=10^6`,

\[
|B_X|=741,qquad Q_G(X)=67537,qquad H_G(X)=45583,
\]

so the remaining margin is `21213`.  Thus R7 supplies a valid perturbation
family but does not falsify `(SCB)` on this range.

```text
E376265635601F1C4648C8E125707A77C7C778DEFFCD5DC0EFCAB95885A2B6CC  R7_top_strip_audit.py
9104D317DD1A9AA26F088A90891335A063C13F454F1AD16DCBF87EEE7710CFD7  R7_top_strip_audit_1e6.json
```
