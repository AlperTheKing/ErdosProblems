# P89: ordered phase count and the range-vacuity obstruction

## Verdict

The proposed inequality

\[
                         T_F\le C_S                                      \tag{1}
\]

is not proved or disproved here.  The P83/P87 six-hole stencil does not by
itself supply the required global charge.  It factors exactly into phase
holes already attached to the three supporting folds, together with one
shared-triple residual.  The latter is absent for every ordered triple of
marks, whether or not it extends to a loose triangle.

More sharply, there is an infinite endpoint-normalized Sidon family with
positive defect and the literal hole for which every stencil entry of every
loose triangle lies below `min(B)`.  On the same family all
`binom(p+1,3)` possible P83 shared triples pass the residual-hole test.
Consequently the six P87 nonmembership statements cannot create a power
saving by counting occupied hole slots or by deleting shared-triple
candidates.  A proof of (1) must instead use a global correlation among the
three arm maps, and any fold charge must be allowed to leave the three
supporting folds, as P95 requires.

## 1. Fold-local phase factorization

Write `H=h-1`.  For a canonical fold

\[
 F=(l,m,q,r),\qquad l\le m<q\le r,\qquad l+m+h=q+r,       \tag{2}
\]

define its lower and upper residuals

\[
 L(F)=q-l-m-b,\qquad U(F)=r-l-m-b=h-b-q.                 \tag{3}
\]

The literal hole gives `L(F),U(F) notin B`.  The endpoint order gives the
more precise range

\[
                    1-b\le L(F),U(F)\le H-b.             \tag{4}
\]

Indeed, `r<=H` in (2) gives `q>=l+m+1`, and the same inequality holds for
`r`; the upper bounds follow from `q,r<=H`.

Now use the P83 normal form

\[
\begin{array}{lll}
F_0=(a,c,u+R,s),&F_Z=(a,c+Z,u,s+R+Z),
&F_X=(a+X,c,u,s+R+X),                                  \tag{5}
\end{array}
\]

and put

\[
              \tau=u-a-c-b,\qquad \lambda=h-b-u.        \tag{6}
\]

### Lemma P89.1 (the stencil has only one non-fold slot)

The P87 stencil is exactly

\[
\begin{array}{c|cc}
 &L&U\\ \hline
F_0&\tau+R&\lambda-R\\
F_Z&\tau-Z&\lambda\\
F_X&\tau-X&\lambda
\end{array}                                             \tag{7}
\]

together with the single residual `tau`.  Thus the six displayed P87
values are

\[
 \{\tau,L(F_X),L(F_Z),L(F_0),U(F_Z)=U(F_X),U(F_0)\}.     \tag{8}
\]

Moreover, `tau notin B` holds for every `a,c,u in B`, since otherwise

\[
                        a+c+\tau+b=u                    \tag{9}
\]

would violate the literal hole.  It does not use any arm or fold equation.

**Proof.**  Substitution of (5) into (3) gives (7).  Equation (9) proves
the last assertion.  QED.

The order and Sidon conditions do give one genuine local refinement.

### Lemma P89.2 (four distinct lower residuals)

For every loose triangle,

\[
                  \tau,\ \tau-X,\ \tau-Z,\ \tau+R       \tag{10}
\]

are pairwise distinct.  The last three lie in `[1-b,H-b]`.

**Proof.**  P83 gives `X,Z,R!=0`, so `tau` differs from the other three.
If `X=Z`, then `x+c=a+z`; Sidon uniqueness and the orders `x<=c` and
`a<=z` force `x=a,c=z`, or `x=z,c=a`.  Either alternative gives `X=Z=0`.
If `R=-X`, then `r+x=u+a`; the orders `r,u>c>=a,x` and Sidon uniqueness
force `r=u,x=a`, again impossible.  The case `R=-Z` follows identically
from `r+z=u+c`.  Hence (10) is pairwise distinct.  Its range assertion is
(4).  QED.

This distinctness still supplies only three distinct ambient holes plus
the unrestricted residual `tau`; the next construction shows that all of
them may occupy an interval containing no marks at all.

## 2. Infinite range-vacuity family

### Proposition P89.3 (the full stencil can be vacuous)

Let `A subseteq [0,W]` be an endpoint-normalized integer Sidon set of order
`p`, and suppose

\[
                           W\le p^2-p.                  \tag{11}
\]

Set

\[
 \gamma=\lfloor W/2\rfloor+1,\quad B=A+\gamma,
 \quad H=W+\gamma,\quad h=H+1,\quad b=1.               \tag{12}
\]

Then `B` is endpoint-normalized and Sidon, its defect satisfies

\[
 \delta={3p^2-p+2\over2}-h\ge p-1>0,                  \tag{13}
\]

and the literal hole holds.  For every ordered shared triple
`a<=c<u` in `B`,

\[
                  u-a-c-1<\gamma=\min B.               \tag{14}
\]

For every actual loose triangle, all six P87 stencil values are also
strictly below `min(B)`.

**Proof.**  Translation preserves Sidonicity and gives `max(B)=H`.
Since `H=W+floor(W/2)+1`, (11) gives

\[
 \delta={3p^2-p\over2}-H
 \ge {3p^2-p\over2}-{3(p^2-p)\over2}-1=p-1.            \tag{15}
\]

Also `3 gamma+1>W+gamma=H`; hence every member of `3B+1` is above
`max(B)`, proving the literal hole.

For any three marks, the left side of (14) is at most

\[
 H-2\gamma-1=W-\gamma-1<\gamma.                        \tag{16}
\]

Every fold residual in (3) has the form `q-l-m-1` with `q<=H` and
`l,m>=gamma`, so the same bound (16) applies.  Lemma P89.1 now places all
six stencil entries below `min(B)`.  QED.

Singer perfect difference sets supply (11) for infinitely many orders.
For a prime power `q`, take a Singer difference set of size `p=q+1` in
`Z_(q^2+q+1)`, lift its residues to integers, and translate its minimum to
zero.  Uniqueness of nonzero modular differences implies
diagonal-inclusive integer Sidonicity, and its width is at most

\[
             q^2+q=p^2-p.                              \tag{17}
\]

Thus Proposition P89.3 is an infinite obstruction, not a finite model.
The number of triples `a<=c<u` is exactly

\[
 \sum_{j=0}^{p-1}(j+1)(p-1-j)={p+1\choose3}.           \tag{18}

Every one satisfies the only non-fold exclusion `tau notin B` by the
strict range inequality (14).

## 3. Consequence for C84

The factorization (7) does not disprove (1), and Proposition P89.3 does not
assert that its translated Singer rows have cubic `T_F`.  It gives the
precise obstruction to the requested ordered-hole count: on an infinite
family satisfying every frontier hypothesis, the literal-hole information
in P87 removes no candidate by occupancy.  An ordered count retaining only
the shared triple and these exclusions therefore stops at

\[
                         T_F\le {p+1\choose3},          \tag{19}
\]

even after all six phase exclusions and positive defect are imposed.

Any proof of C84 must establish a new global statement about simultaneous
compatibility of the three unique Sidon arms.  A charge to the three
supporting folds is impossible by P95's exact Hall witness, so such a
statement must use non-support folds or another global resource.  No such
charge is claimed here.

## 4. Exact audit

Run

```powershell
python -B problems/864/compute/p89/verify_ordered_phase_obstruction.py
```

The checker verifies (7)--(10) on all 25 P75 triangles.  It also translates
the P80 ruler by `gamma=320` and obtains exactly

\[
 (p,h,\delta,C_S,T_F)=(29,960,288,14,2),               \tag{20}
\]

with all `4060=binom(30,3)` shared triples satisfying (14); the largest
stencil entry on its two actual loose triangles is `103<320=min(B)`.
