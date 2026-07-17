# GPT-Pro CX-R6 prompt: splitless-closed boundary theorem

Let

\[
\mathcal A=\{n\ge2:n\not\equiv1\pmod3\}.
\]

For `n in A`, call a factorization `n+1=ab` admissible when
`2<=a<b` and `a,b in A`. Call `n` splitless when it has no admissible
factorization. Call `n` hard-shaped when it is even, has an admissible
factorization, and has no admissible seed-3 factorization; explicitly,
either `3` does not divide `n+1`, or `(n+1)/3` is not in `A`, or
`(n+1)/3=3`.

Let `T subset A` contain `2,3`, be forward closed

\[
a,b\in T,\ a<b\quad\Longrightarrow\quad ab-1\in T,
\]

and exclude every splitless nonseed. For an integer cutoff `X`, define

\[
H_T(X)=\#\{n\le X:n\text{ hard-shaped},\ n\notin T\},
\]

\[
Q_T(X)=\#\{m:2m-1\le X,\ m\notin T,\ 2m-1\in T\}.
\]

Please prove or refute the uniform statement

\[
\boxed{H_T(X)\le Q_T(X)\quad\text{for every such }T\text{ and every }X.}
\tag{SCB}
\]

This is stronger than the original image-set lemma and would settle the
current density problem: the least closure `G` is such a `T`, C13 proves the
splitless count is `o(X)`, and C16 shows `(SCB)` implies
`|G cap [1,X]|=(2/3)X+o(X)`.

Exact evidence is unusually rigid. CP-SAT has no Boolean counterexample
through `X=100000`. More importantly, the full LP relaxation also proves
`(SCB)` and returns an integral optimum at

```text
X       54  100  200  500  1000  2000  5000  10000
H-shapes 1    3    8   27    66   147   410    878
LP min   1    4    8   33    69   147   431    920
```

Here membership variables `t_n in [0,1]` satisfy

\[
t_{ab-1}\ge t_a+t_b-1,
\]

splitless variables are fixed to zero, `t_2=t_3=1`, and boundary variables
satisfy only the convex-hull constraints for
`q_{2m-1}=(1-t_m)t_{2m-1}`. The objective is

\[
\sum_{n\text{ hard}}t_n+\sum q_{2m-1};
\]

`(SCB)` is equivalent to this being at least the number of hard-shaped
integers. HiGHS dual optima use only closure inequalities,
`q_{2m-1} >= t_{2m-1}-t_m`, and fixed bounds, with integral multipliers.

One interpretation is a directed cut/path theorem. A closure implication
using a guaranteed member `g` gives a free directed edge
`p -> gp-1`; a seed-2 edge `p -> 2p-1` is charged when membership changes
from zero to one. Splitless vertices are fixed zero and the least closure is
fixed one. A uniform integral dual or red-edge-disjoint path packing would
prove `(SCB)`.

Do one concrete thing: give a complete proof of `(SCB)`, preferably by an
explicit cut/flow, telescoping, or induction invariant that produces the
LP dual for arbitrary `X`; or give an explicit finite forward-closed,
splitless-free `T` and cutoff `X` with `H_T(X)>Q_T(X)`. Do not return a
restatement as Hall's theorem, an unproved matching claim, finite evidence,
or a proof that assumes `T` is the least closure. Preserve `a<b` throughout.
