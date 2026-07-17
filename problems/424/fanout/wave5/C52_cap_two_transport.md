# C52: unranked cap-two global transport

## Verdict

No proof and no actual-`G` counterexample was obtained for

\[
                   H(X)\le Q^{(2)}(X)+1.                 \tag{CT2}
\]

Here `Q^(2)` retains only the first two healed seed-2 exits, ordered by
child coordinate, in each canonical C39 component.  An independent exact
least-grounded scan through `10^7` found the stronger finite inequality

\[
                         H(X)\le Q^{(2)}(X)              \tag{1}
\]

at every cutoff.  This agrees with C43 and is finite evidence only.

There are two exact falsifiers to weaker proof premises.

1. Forward closure, the real arithmetic factor table, and every canonical
   forest constraint do not imply (CT2).  The first exact closed-superset
   countermodel is at `X=144`, with `H=4`, `Q^(2)=2`.
2. Requiring grounded factor support for every generated structural root is
   still insufficient.  The first exact countermodel is at `X=1710`, with
   `H=81`, `Q^(2)=79`.  Six unsupported generated seed-3 children collapse
   six actual first/second seed-2 exits without creating seed-2 credit.

Thus a tree, Euler-tour, laminar-Hall, or component-merger proof cannot use
canonical parenthood plus root grounding only.  It must recursively trace
support for every generated seed-3 boundary and must transport capacity
between components unrelated to all factor endpoints of the current hard
source.  C51 independently proves the latter requirement inside the genuine
image `S_3` at `X=318`.

The smallest surviving global statement found here is the universal
one-step image gate

\[
 H_{F(S)}(X)\le Q^{(2)}_{F(S)}(X)                       \tag{UI2}
\]

for every forward-closed `S`.  Exact CP-SAT optimization found no failure at
any of the `410` hard-shape cutoffs through `5000`; the maximum objective was
zero.  No proof of (UI2) is supplied, and (UI2) is theorem-strength because
`G=F(G)`.

## 1. Definitions

Let

\[
 {cal A}=\{n\ge2:n\not\equiv1\pmod3\},
\]

and let `G` be the least subset of `A` containing `2,3` and closed under

\[
                  (a,b)\longmapsto ab-1,
             \qquad 2\le a<b.                           \tag{2}
\]

The strict inequality in (2) is enforced in every computation below.
Write `M=A\G`.  A hard hole is a reducible even hole without a usable
distinct seed-3 factorization, as in C31.

For a hole `n`, the canonical C39 parent is

\[
 \pi(n)=(n+1)/2\quad(n\text{ odd}),                     \tag{3}
\]

or

\[
 \pi(n)=(n+1)/3\quad(n\text{ seed-3-easy even}).        \tag{4}
\]

Splitless and hard holes are roots.  C39 proves that (3)-(4) give a forest.
A healed seed-2 exit is an edge

\[
                 q\in M,\qquad 2q-1\in G,               \tag{5}
\]

recorded at child coordinate `2q-1`.  In each canonical component `C`, list
these child coordinates as

\[
                         e_{C,1}<e_{C,2}<\cdots .        \tag{6}
\]

Then

\[
 Q^{(2)}(X)=\sum_C\min\bigl(2,\#\{i:e_{C,i}\le X\}\bigr). \tag{7}
\]

If the hard coordinates are `h_1<h_2<...` and the retained exits pooled
over all components are `t_1<t_2<...`, then parity prevents ties and

\[
 (CT2)\text{ at every cutoff}
 \quad\Longleftrightarrow\quad
 t_{j-1}<h_j\quad(j\ge2).                               \tag{8}
\]

Indeed, at `h_j` the inequality asks for at least `j-1` arrived retained
exits.  Between hard events its left-minus-right side cannot increase.
`C52_exact_cap_two.py` checks both the scalar form and (8).

## 2. Exact least-grounded computation

The standalone checker reconstructs `G` in increasing order.  For every
allowed `n`, it factors `n+1` exactly and tests only pairs `2<=a<b`; hence
membership below the cutoff is independent of all larger integers.  Hole
roots and exit ordinals are then computed without importing a C39/C43
artifact.

| limit | `|G|` | `H` | all exits | cap one | `Q^(2)` | terminal `H-Q^(2)` |
|---:|---:|---:|---:|---:|---:|---:|
| `10^5` | `39,843` | `5,108` | `6,783` | `6,055` | `6,515` | `-1,407` |
| `10^6` | `457,599` | `45,583` | `67,537` | `62,972` | `66,238` | `-20,655` |
| `10^7` | `4,952,270` | `392,961` | `637,270` | `613,207` | `632,880` | `-239,919` |

At every cutoff through `10^7`, the maximum of `H-Q^(2)` is zero, attained
on the empty initial prefix; there is no order-statistic failure in (8).
The run has zero canonical-decomposition failures.  A separate literal
fixed-point iteration through `5000` has zero membership mismatches.

The `10^7` member bitmap, including zero entries at disallowed coordinates,
has SHA-256

~~~text
7F5F29E1D5733D623C514C98C183796C3AB15A99D9AD9E5F0C9FF6EA627D85A0
~~~

Cap two is not cosmetic.  Keeping only the first exit per component first
violates even additive one at

\[
             X=1014,\qquad H(X)=43,\qquad Q^{(1)}(X)=41. \tag{9}
\]

The maximum cap-one excess through `10^7` is `18`, first attained at
`X=6192`.  Equation (9) is an actual-`G` falsifier to the unranked cap-one
replacement, not to (CT2).

## 3. First closure-only countermodel

Let `S` range over every subset of the allowed prefix which contains `2,3`
and obeys all exact forward-closure clauses

\[
                    a,b\in S\Longrightarrow ab-1\in S
                    \quad(2\le a<b).                    \tag{10}
\]

Canonical roots are arithmetic: repeated application of (3)-(4) does not
depend on the membership labels.  Clause (10) guarantees that the holes of
`S` are parent-closed.  Therefore hard holes and first-two exits are exact
Boolean functions of `S`.

Every output in (10) is larger than both parents.  Hence any feasible prefix
extends to an infinite forward-closed allowed set by taking its forward
closure above the cutoff; the finite model has no hidden boundary premise.

`C52_closed_countermodel.py` maximizes `H_S-Q_S^(2)` by CP-SAT.  The first
countermodel is `X=144`.  A stable single-worker optimum has member set

~~~text
2,3,5,9,14,17,18,20,26,27,30,32,33,35,39,41,44,48,50,51,
53,59,63,65,66,68,69,72,77,80,81,84,87,89,95,98,99,101,
104,105,116,117,122,125,129,131,134,135,137,143.
~~~

Its four hard holes and their complete admissible pairs are

\[
 55=5\cdot11,\quad 75=5\cdot15,\quad
 115=5\cdot23,\quad145=5\cdot29,                       \tag{11}
\]

so the hard coordinates are `54,74,114,144`.  The only seed-2 exits are

\[
 41=2\cdot21-1\quad(\text{root }6),\qquad
 89=2\cdot45-1\quad(\text{root }12).                   \tag{12}
\]

Thus

\[
                         H_S(144)-Q_S^{(2)}(144)=4-2=2. \tag{13}
\]

The solver proves `OPTIMAL` with objective and best bound both `2`.  An
independent replay finds zero violations among all `117` closure clauses
and zero canonical hole-parent failures.  The unsupported members are

~~~text
18,20,30,32,48,66,68,72.
~~~

In particular, unsupported declarations at roots `18` and `20` erase the
actual exits `69` and `77` while preserving every forward implication.

The exact optima at all hard-shape events through `144` are

| cutoff | `54` | `74` | `84` | `114` | `144` |
|---:|---:|---:|---:|---:|---:|
| max `H-Q^(2)` | `0` | `1` | `1` | `1` | `2` |

The objective can increase only when a hard-shaped coordinate is inserted,
so `144` is the first cutoff, not merely the first tested endpoint.
This is not an actual-`G` counterexample: unsupported members are forbidden
by least grounded generation.  It proves exactly that forward closure plus
the real canonical forest cannot establish (CT2).

## 4. Root grounding still fails

Strengthen (10) by requiring every generated structural root to have an
actual factor witness in `S`.  This removes the `144` model.  It still does
not imply (CT2).

The same exact optimizer checked all `123` hard-shape cutoffs through
`1710`.  Every cutoff through `1694` has optimum at most one, while at
`1710` it proves

\[
                         H_S=81,\qquad Q_S^{(2)}=79.     \tag{14}
\]

The certificate has `521` members, `619` holes, `2326` closure clauses,
`380` root-support clauses, and zero closure or canonical-parent failures.
Its `40` unsupported members are all nonroots.

The loss relative to the actual prefix is localized exactly.  The actual
least set has `(H,Q^(2))=(81,83)` at `1710`.  Six canonical components lose
one retained exit each in the root-grounded model:

| root | actual retained exits | model retained exits | unsupported T3 promotion |
|---:|:---|:---|:---|
| `8` | `449,1349` | `449` | `338=3*113-1`, `1349=T2^2(338)` |
| `36` | `1121,1689` | `1121` | `212=3*71-1`, `1689=T2^3(212)` |
| `48` | `377,1133` | `377` | `284=3*95-1`, `1133=T2^2(284)` |
| `72` | `1707` | none | `854=3*285-1`, `1707=T2(854)` |
| `96` | `761,1143` | `761` | `572=3*191-1`, `1143=T2(572)` |
| `114` | `905,1359` | `905` | `680=3*227-1`, `1359=T2(680)` |

Here `T2(x)=2x-1`.  Each displayed even T3 child is declared generated
without a factor witness.  Forward closure then generates its T2 tail,
turning the actual boundary parent into a member and deleting the displayed
exit.  This creates no seed-2 boundary at the T3 jump.  Two extra model
components, roots `398` and `426`, contribute exits `1589` and `851`, so the
net change is `-6+2=-4`, from actual `83` to model `79`.

This is the precise obstruction to root-level Euler or merger accounting:
an ungrounded T3 transition can remove an entire T2-exit-bearing branch
without paying the statistic being counted.  Grounding only the component
root cannot see it.

## 5. Even-support reduction

The T3 obstruction disappears under the following intermediate premise.
Let `S` satisfy (10), and assume every even `n in S\{2}` has an admissible
factor witness in `S`.

### Lemma 1

Every unsupported nonseed member of `S` is an odd seed-2 boundary child.

### Proof

The premise excludes unsupported even members.  Let an odd `u>3` belong to
`S` without a factor witness, and put `p=(u+1)/2`.  The parent `p` is allowed
and `2<p<u`.  If `p` belonged to `S`, the distinct pair `(2,p)` would support
`u`, a contradiction.  Hence `p` is a hole while `u=2p-1` is a member, so
`u` is a seed-2 boundary child. QED.

By strong induction, every member of such an `S` is derivable from `2,3`
and these unsupported odd boundary children: even members use their assumed
witness, supported odd members use their seed-2 parent, and the remaining
odd members are the boundary axioms in Lemma 1.

This reduction does not prove (CT2).  A component may contain more than two
such boundary axioms, while `Q^(2)` discards all but two; no deletion or
normalization argument was found that preserves hard demand.  Exact fixed-
endpoint optimization under even support gives

| `X` | `1710` | `5000` | `10^4` | `5*10^4` | `10^5` |
|---:|---:|---:|---:|---:|---:|
| max `H-Q^(2)` | `-2` | `-24` | `-37` | `-504` | `-1348` |

All five values are proved optimal, but they are endpoint computations and
cannot be extrapolated.

## 6. Surviving image gate

For a forward-closed `S`, define its exact Horn image

\[
 F(S)=\{2,3\}\cup\{ab-1:2\le a<b,\ a,b\in S\}.         \tag{15}
\]

The least set satisfies `G=F(G)`.  Consequently (UI2) would imply the
strict form (1), and hence (CT2).

`C52_image_countermodel.py` represents source membership, every closure
clause, and the biconditional defining image membership.  It then derives
hard holes, canonical roots, all exits, and first-two selection in `F(S)`.
For every hard-shape cutoff through `5000`, it maximizes

\[
                         H_{F(S)}-Q^{(2)}_{F(S)}.        \tag{16}
\]

All `410` models are `OPTIMAL`.  The maximum is zero, first at `X=54`; no
additive-one failure exists in that finite search.  Every emitted model is
replayed for source closure, exact image equivalence, and image closure.

C51 supplies a complementary exact fact for the genuine descending images:
even allowing every arrived exit in every missing-factor component, the
hard set `{54,74,186,318}` has only the neighborhood `{41,57,63}` in `S_3`.
Thus an image proof cannot be a factor-component matching.  The C52 image
search says only that the fully global scalar inequality survives through
`5000`; it supplies no transport map.

## 7. Precise obstruction

The computations and Lemma 1 leave a three-part requirement.

1. **Recursive T3 grounding.**  The first-two statistic is blind to a
   generated T3 boundary.  Its factor derivation must be followed until it
   either produces T2 credit or reaches already controlled grounded data.
2. **Cross-component capacity.**  C43 at `114` and C51 at `318` show that
   credits from all factor-endpoint components can be insufficient.  The
   transport must reach unrelated splitless and hard-root components.
3. **Cap-two stability.**  Once transport enters another component, it must
   prove that using only its first two exits survives alternating rerouting.
   Later exits cannot simply be deleted because they may support even nodes
   and thereby change hard demand.

A component Euler characteristic fails item 2.  Root-grounded forest
induction fails item 1 by the exact `1710` model.  Complete chronological
Hall edges satisfy all three by definition, but their Hall condition is
exactly (CT2), so that is a reformulation rather than a proof.

The rigorous C52 output is therefore the two exact countermodels, Lemma 1,
and the surviving universal-image falsifier gate.  The actual cap-two
transport theorem remains open.

## 8. Reproduction

From the repository root:

~~~powershell
python problems/424/fanout/wave5/C52_exact_cap_two.py `
  --limit 10000000 --verify-limit 5000

python problems/424/fanout/wave5/C52_closed_countermodel.py `
  --limit 144 --workers 1 --time-limit 300 --support none

python problems/424/fanout/wave5/C52_closed_countermodel.py `
  --limit 1710 --workers 1 --time-limit 300 --support roots

python problems/424/fanout/wave5/C52_image_countermodel.py `
  --limit 5000 --workers 16 --time-limit 300 --scan-hard-cutoffs
~~~

SHA-256:

~~~text
C52_exact_cap_two.py       9627209CDFCB96FDA24733C635C7396B20EF257DF4D0BA6CF5B74138041AF1AF
C52_closed_countermodel.py 5DEB0BD624017B87B68CB763D5F003A5D332F7188EB2CE6823946B4C2A001564
C52_image_countermodel.py  1692DB4F4BBF967BC3FB9E04B8C64E38E4EE71271CE2246F5F22D3AFC9266DF5
~~~
