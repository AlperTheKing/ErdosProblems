# C116: structural power proof lane

## DIRECT ROUTE

1. **Exact final deliverable.** Prove constants `A>0`, `B`, and
   `alpha>1/(2 log 2)` such that every hard even hole `h` satisfies
   `s(h) >= A d(h)^alpha-B`; give a rigorous counterfamily; or prove a
   strictly weaker estimate that closes C99 through C112.1.
2. **Current frontier lemma.** Put `p_k=11^(2k+1)`.  Prove or refute the two
   literal state claims

   \[
      p_k\notin G\quad(k\ge0),\qquad
      \mathcal P(\sigma(p_k))\ne\varnothing\quad(k\ge1). \tag{IV}
   \]

   The exceptional root `sigma(p_0)=6` is structural splitless.
3. **Logical bridge.** For `h_m=11^(2m)-1`, the admissible pairs are exactly
   `(11^i,11^(2m-i))` with odd `i<m`, so `d(h_m)=floor(m/2)`.  Under (IV)
   every pair is blocked, exactly the pair with `i=1` is structural, and
   hence `h_m` is hard with `s(h_m)=1`.  As `m` tends to infinity this
   contradicts `s(h)>=A*d(h)^alpha-B` for every `A>0`, finite `B`, and every
   `alpha>0`, in particular every exponent requested in item 1.
4. **Next falsifiable action.** Factor `sigma(p_k)+1` and recursively classify
   every `p_k` representable below `2^64`; emit all factor pairs, root states,
   and the first failure of either claim in (IV) before proof effort.
5. **Exit condition.** Kill this family at the first generated `p_k` or first
   splitless root with `k>=1`.  If the exact prefix survives, prove (IV) by
   explicit factor identities and a closure induction; do not replace it by
   another asymptotic model.  Exit the lane only with item 1's deliverable.

## 1. Literal definitions

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\}
\]

and let `G` be the least subset of `A` containing `2,3` and satisfying

\[
 a,b\in G,\quad a<b \quad\Longrightarrow\quad ab-1\in G.
\]

For an allowed integer `h`, its literal admissible factor-pair set is

\[
 \mathcal P(h)=\{(a,b):2\le a<b,\ a,b\in\mathcal A,\ ab=h+1\},
 \qquad d(h)=|\mathcal P(h)|.                          \tag{1}
\]

A **hard even hole** is an even `h in A\G` with `P(h)` nonempty which is
not seed-3 easy: it is not the case that `3|(h+1)`, `(h+1)/3 in A`, and
`(h+1)/3 != 3`.  Equivalently, it is an actual missing member of one of the
two hard arithmetic shapes in C96.2.

Every endpoint of a pair in `P(h)` is odd.  A pair is blocked because at
least one endpoint `p` is missing from `G`.  For such an odd endpoint define
its literal seed-2 root by

\[
 \sigma(p)=1+{p-1\over2^{v_2(p-1)}}.                  \tag{2}
\]

Thus `sigma(p)` is even and, for the integer `j=v_2(p-1)>=1`,

\[
                 p=2^j(\sigma(p)-1)+1.                \tag{3}
\]

The root is **structural splitless** precisely when
`P(sigma(p))` is empty.  Since generation propagates upward along the
seed-2 chain, a missing `p` cannot have a generated root.

A pair in `P(h)` is **structural** when at least one of its missing endpoints
has structural splitless seed-2 root.  The number of such pairs is `s(h)`.
Define the two endpoint sets

\[
\begin{aligned}
 E_0(h)&=\{p:p\text{ is a missing endpoint of a pair in }\mathcal P(h),
                 \ \mathcal P(\sigma(p))=\varnothing\},\\
 E_1(h)&=\{p:p\text{ is a missing endpoint of a pair in }\mathcal P(h),
                 \ \mathcal P(\sigma(p))\ne\varnothing\}.
\end{aligned}                                         \tag{4}
\]

These are sets of literal factor endpoints, not sets of roots; different
endpoints on one seed chain remain different elements.

## 2. Dead endpoint-imbalance branch

The endpoint imbalance (I) is not a restatement of the desired power bound:
it compares the two root types on all missing factor endpoints, including
both endpoints of a doubly blocked pair.  Its elementary bridge is:

* every nonstructural pair contributes a distinct endpoint to `E_1(h)`, so
  `d(h)-s(h)<=|E_1(h)|`;
* every endpoint in `E_0(h)` lies in a structural pair, and one pair has at
  most two endpoints, so `|E_0(h)|<=2s(h)`.

Combining these inequalities with (I) would give the former bound
`s(h)>=d(h)/3-8/3`.  The invariant is exactly false.  Put

\[
 N=3\cdot13\cdot43\cdot557\cdot5087=4,751,710,743,
 \qquad h=N-1.
\]

The independent recursive replay proves that `h` is hard and has

\[
 (d(h),s(h),|E_0(h)|,|E_1(h)|)=(8,0,0,9).
\]

Thus `|E_1(h)|=9>|E_0(h)|+8`.  Normal and optimized replay artifacts are
byte-identical with SHA-256

```text
13E3A9D899FE35BCD4C06AB8A8D0309B6D209387974CE0935B63099E26D306DE
```

This kills (I), but it does not kill (P): here `3s=d-8=0`.

## 3. Canonical-blocker invariant

For `(a,b) in P(h)`, with `a<b`, define

\[
 \kappa_h(a,b)=
 \begin{cases}
 a,&a\notin G,\\
 b,&a\in G.
 \end{cases}                                          \tag{5}
\]

The second case is well defined because hardness forbids both endpoints
from lying in `G`.  Let

\[
 t(h)=\#\{(a,b)\in\mathcal P(h):
          \mathcal P(\sigma(\kappa_h(a,b)))=\varnothing\}. \tag{6}
\]

This chooses exactly one literal blocker from every pair.  A pair counted
by `t(h)` is counted by `s(h)`, hence `t(h)<=s(h)`.  The new candidate (II)
therefore has the direct bridge displayed at the top.  It is strictly
stronger than (P), not an equivalent rewrite: at `h=1,035,904,700` the
accepted sparse row has `s(h)=1` but `t(h)=0`.

## 4. Prefix-balance frontier

Write the pairs in their unique increasing-lower-endpoint order

\[
 (a_1,b_1),\ldots,(a_d,b_d),\qquad a_1<\cdots<a_d.
\]

For each index put `epsilon_i=1` when the canonical blocker
`kappa_h(a_i,b_i)` has structural splitless seed-2 root, and put
`epsilon_i=-1` otherwise.  Then

\[
 \sum_{i=1}^k\epsilon_i=2t_k(h)-k.                    \tag{7}
\]

The proposed combinatorial invariant is that every initial segment has at
most eight more reducible than structural canonical blockers, equivalently
(III).  This is a strictly stronger, falsifiable lemma rather than a rewrite
of (II): only its terminal case is (II).  A proof would amount to matching
every reducible canonical blocker after an exceptional set of size at most
eight to a distinct earlier structural canonical blocker.

## 5. Dead prefix-balance branch

The normal and optimized Python classifiers agree through `10^7`, the
independent recursive replay is tight at product `4,751,710,743`, and the
C++ stream finds no failure among all `106,360,959` hard holes through
`4,000,000,000`.  The minimum prefix slack is zero.

This finite result does not supply the promised matching.  If a reducible
canonical blocker has root `r` and `r+1=uv`, then

\[
             p=2^j(r-1)+1=2^j(uv-2)+1.
\]

Neither `u` nor `v` need divide `h+1`, so root factorization gives no map to
another factor pair of the source.  Thus the branch is closed as

```text
DEAD: reformulation maze - no bridge from root factors to source divisors.
```

The finite prefix invariant is not asserted as a lemma and is not used
below.

## 6. Direct odd-power construction

For `m>=2`, put

\[
                         h_m=11^{2m}-1.               \tag{8}
\]

Since `11=-1 (mod 3)`, an admissible proper factor pair of `h_m+1` must
split the exponent as `(i,2m-i)` with both exponents odd.  Taking the lower
endpoint gives the literal list

\[
 \mathcal P(h_m)=
 \{(11^i,11^{2m-i}):1\le i<m,\ i\text{ odd}\},       \tag{9}
\]

and therefore `d(h_m)=floor(m/2)`.  This is already an unbounded exact
factor-pair count.  The only remaining work is the pair of closure/root
claims (IV), whose bridge to a counterfamily is stated in the direct route.
