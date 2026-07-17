# C50: active seed-3 frontier charge

## Verdict

No injective or absolute finite-multiplicity charge of the C46 active
frontier to a proved `o(X)` set is obtained.

There is an exact obstruction.  If `R_3(X)` is the number of C46 chain
starts and `A(X)` is the number still active at `X`, then for every `X`,

\[
 R_3(X)-R_3\!\left(\left\lfloor{X+1\over3}\right\rfloor\right)
 \le A(X)\le R_3(X).                                      \tag{1}
\]

Consequently

\[
                         A(X)=o(X)
 \quad\Longleftrightarrow\quad R_3(X)=o(X).               \tag{2}
\]

Thus the active frontier is not a smaller residual class created by the
transport.  Fresh starts in the top third of the current prefix have not
had enough coordinate range to terminate, and already force (1).

Every integer cutoff through `10^7` was audited on the least grounded set,
with distinct generating inputs enforced by `2<=a<b`.  The strongest
splitless scalar inequality surviving the audit is

\[
 R_3(X)\le E\!\left(\left\lfloor{X+1\over9}\right\rfloor\right)
 \qquad(53\le X\le10^7).                                  \tag{3}
\]

Equation (3) is finite data, not a theorem.  The direct component-root,
least-blocker, immediate-`Q`, and bounded-dilation realizations of such a
charge all have exact falsifiers below.  No claim of `A(X)=o(X)`, (3), or a
C16 contraction is made.

## 1. Exact setup

Use C46's generated-state map

\[
 F(x)=\begin{cases}
 3x-1,&x\text{ odd},\\
 3x/2,&x\text{ even and }3x/2\in G.
 \end{cases}
\]

A start is `s=3q-1 in G`, where `q` is an odd hole.  If an even chain
state `x` has the hole `y=3x/2`, the chain terminates at

\[
 c=3x-1=2y-1\in G,                                        \tag{4}
\]

which is a healed seed-2 target.  Let `tau(s)=c`, or `infinity` if the
chain never terminates.  Then the C46 quantities are exactly

\[
 R_3(X)=\#\{s:s\le X\},\qquad
 T(X)=\#\{s:\tau(s)\le X\},
\]

\[
 A(X)=\#\{s:s\le X<\tau(s)\},\qquad R_3(X)=T(X)+A(X).     \tag{5}
\]

The strict-input rule is preserved in (4): every state used here exceeds
`3`, so its generating pair is the distinct pair `(3,x)`.

## 2. Fresh-frontier theorem

**Theorem 1.**  Equations (1) and (2) hold for the actual least grounded
set `G`.

**Proof.**  Chain states strictly increase.  If a chain starting at `s`
terminates, its final even state `x` satisfies `x>=s`, so (4) gives

\[
                         \tau(s)=3x-1\ge3s-1.             \tag{6}
\]

The same inequality is automatic when `tau(s)=infinity`.  Hence every
start

\[
 \left\lfloor{X+1\over3}\right\rfloor<s\le X
\]

is active at `X`.  Counting these starts proves the lower bound in (1),
and `A(X)<=R_3(X)` proves the upper bound.

One direction of (2) follows immediately from the upper bound.  Conversely,
suppose `A(X)=o(X)` and put

\[
 D(X)=R_3(X)-R_3\!\left(\left\lfloor{X+1\over3}\right\rfloor\right).
\]

Then `0<=D(X)<=A(X)=o(X)`.  Starting from `X_0=X`, iterate
`X_(j+1)=floor((X_j+1)/3)`.  Telescoping gives

\[
 R_3(X)=\sum_{j\ge0}D(X_j),
\]

with only finitely many nonzero terms.  For any `epsilon>0`, the terms with
`X_j` above a fixed threshold sum to at most

\[
 \epsilon\sum_{j\ge0}X_j\le(3/2)\epsilon X+O(\epsilon\log X),
\]

and the remaining tail is bounded independently of `X`.  Therefore
`R_3(X)=o(X)`.  QED.

**Corollary 2.**  For fixed positive constants `c,C`, a bound

\[
                         A(X)\le C E(cX)                  \tag{7}
\]

would prove `R_3(X)=o(X)`, since C13 proves `E(cX)=o(X)`.  Thus (7) is a
new global theorem about all generated T3 exits, not a boundary estimate
that follows from C46's transport.

Likewise, because the C46 terminal targets form a subset of `Q`, a charge
to unused same-cutoff targets would require

\[
 A(X)\le Q(X)-T(X)
 \quad\Longleftrightarrow\quad R_3(X)\le Q(X).            \tag{8}
\]

The transport identity cancels out of (8).  Such a charge is exactly the
global T3-exit versus T2-exit comparison that still needs proof.

## 3. Strongest unconditional transport bound

**Lemma 3 (frontier annulus).**  Every active chain at `X` has a unique
frontier state in

\[
                         G\cap(X/3,X],                    \tag{9}
\]

and distinct active chains have distinct frontier states.  Consequently

\[
                         A(X)\le|G\cap(X/3,X]|.           \tag{10}
\]

**Proof.**  Follow an active chain until its last state `x<=X`.  If `x` is
odd, the next state `3x-1` exceeds `X`, so `x>(X+1)/3`.  If `x` is even and
`3x/2` is a generated state beyond `X`, then `x>2X/3`.  In the remaining
even case, `3x/2` is a hole and the terminal child `3x-1` exceeds `X`, again
giving `x>(X+1)/3`.  C46 Lemma 3 makes the chains vertex-disjoint, proving
injectivity.  QED.

The set in (9) is not known to be `o(X)` and is the wrong type of target for
C16.  At `X=10^7`, all `46,287` frontier states were distinct; the smallest
was `3,333,344`.

## 4. Every-cutoff audit

The audit reconstructs `G` in increasing order from all admissible divisor
pairs, traces every chain, and sweeps every cutoff rather than only the
displayed checkpoints.

| `X` | `R_3` | `T` | `A` | fresh starts in top third | `E(floor((X+1)/9))` | `E(floor((X+1)/27))` | `Q` |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `10^2` | 1 | 0 | 1 | 1 | 2 | 0 | 3 |
| `10^3` | 9 | 1 | 8 | 7 | 22 | 8 | 46 |
| `10^4` | 138 | 29 | 109 | 98 | 173 | 63 | 593 |
| `10^5` | 1,231 | 346 | 885 | 794 | 1,481 | 530 | 6,783 |
| `10^6` | 9,351 | 2,545 | 6,806 | 5,741 | 13,191 | 4,628 | 67,537 |
| `10^7` | 63,699 | 17,412 | 46,287 | 38,080 | 120,256 | 41,788 | 637,270 |

The `10^4`, `10^5`, and `10^6` rows reproduce C46 exactly.  There were no
chain-state collisions and all terminal children were distinct.

| candidate | exact result for all cutoffs through `10^7` |
|---|---|
| `A(X)<=E(floor((X+1)/3))` | no failure |
| `R_3(X)<=E(floor((X+1)/3))` | no failure |
| `A(X)<=E(floor((X+1)/9))` | first failure `X=44`, last `X=52`; then no failure |
| `R_3(X)<=E(floor((X+1)/9))` | first failure `X=44`, last `X=52`; then no failure |
| `A(X)<=E(floor((X+1)/27))` | first failure `X=44`; at `10^7`, `46287>41788` |
| `R_3(X)<=E(floor((X+1)/27))` | first failure `X=44`; at `10^7`, `63699>41788` |
| `A(X)<=Q(X)-T(X)` | no failure; equivalent to `R_3(X)<=Q(X)` |
| fresh-start lower bound (1) | no failure |

At the first splitless-scale failure, `X=44`, the counts are

\[
 A=R_3=1,qquad E(\lfloor45/9\rfloor)
 =E(\lfloor45/27\rfloor)=0.                               \tag{11}
\]

For the `/27` active inequality the maximum excess is `4,799` at
`X=6,362,504`, where `(A,E_27)=(31,880,27,081)`.  For the corresponding
`R_3` inequality the maximum excess is `21,914` at `X=9,999,464`, where
`(R_3,E_27)=(63,699,41,785)`.

## 5. Exact charge falsifiers

### Immediate healed target

The first start is

\[
 q=15,\qquad s=3q-1=44.
\]

Its immediate seed-2 candidate is `2q-1=29`, which is a hole.  Its C46
chain instead terminates at the unrelated target `131`, so at cutoff `44`
the only available same-prefix `Q` credit is necessarily nonlocal.

### Canonical component root

Capacity one first fails at `X=404`.  The two active starts

\[
 134=3\cdot45-1,qquad404=3\cdot135-1
\]

have the same splitless canonical root `12`; their terminal children are
`1805` and `1211`, both beyond `404`.  By `X=48,698`, canonical root `8`
has active multiplicity `10`, with starts

```text
4058, 12176, 18404, 24494, 36764,
36800, 48464, 48554, 48680, 48698.
```

The root map also fails to land in the splitless set.  At `X=2078`, the
active start has source parent `693` and canonical path

\[
                         693\longmapsto347\longmapsto174.
\]

The root `174` is reducible (`175=5*35`) and has no canonical seed parent,
so it is hard, not splitless.  This chain terminates only at `6233`.

### Recursive blocker leaf

As a deterministic all-the-way descent diagnostic, repeatedly choose the
least missing endpoint among all admissible splits until reaching a
splitless hole.  This map first collides at `X=404` on leaf `8`.  At
`X=9,999,212`, leaf `6` has `26,523` simultaneously active preimages.
This rules out every capacity at most `26,522` for this deterministic map.
The finite fiber does not rule out a larger capacity or a different global
matching.

### Fixed-dilation future target

For the candidate `tau(s)<=C s`, the exact first failures among starts in
increasing order are:

| integer `C` | first failing start | exact terminal child |
|---:|---:|---:|
| 3 | 134 | 1,805 |
| 9 | 134 | 1,805 |
| 27 | 494 | 29,993 |
| 81 | 1,934 | 2,378,831 |
| 243 | 1,934 | 2,378,831 |
| 729 | 1,934 | 2,378,831 |
| 1,230 | 1,934 | 2,378,831 |
| 1,845 | 6,836 | 12,613,991 |

The following exact generated chain starts at `6836`:

```text
6836, 10254, 15381, 46142, 69213,
207638, 311457, 934370, 1401555, 4204664.
```

At the final even state,

\[
 y={3\cdot4204664\over2}=6306996
\]

is a hole, so the exact terminal target is

\[
 c=3\cdot4204664-1=12613991=2y-1.                         \tag{12}
\]

But

\[
                         1845\cdot6836=12612420<c.        \tag{13}
\]

Therefore every integer fixed-dilation assertion `tau(s)<=C s` with
`C<=1845` is false for the actual set.  The audit does not rule out a larger
constant.  Even such a larger-dilation map would place credit after the
source cutoff and would not by itself give a same-prefix C16 charge.

## 6. Precise obstruction

The C46 chain transport pays old starts when they terminate, but a positive
fraction of the observed frontier consists of starts born in the current
top third: `38,080` of `46,287` active chains at `10^7`.  Theorem 1 makes
this structural rather than empirical.  Any proof that charges `A(X)` to
`E(cX)` with absolute multiplicity would already prove the full new
statement `R_3(X)=o(X)`.  Any proof that charges it to unused same-cutoff
targets would already prove the global comparison `R_3(X)<=Q(X)`.

Neither conclusion follows from injectivity of `F`.  The only automatic
injection is Lemma 3 into a linear-size generated annulus.  The natural
routes from a start to a splitless root, an obstruction leaf, its immediate
T2 child, or its own bounded-dilation terminal are falsified above.

Thus `R_3=T+A` does not supply an `o(X)` error for C16.  The surviving
inequality (3) is the exact remaining scalar gate in this lane; proving it
requires a genuinely global comparison between T3 exits and splitless
holes, not further iteration of the C46 chain.

## 7. Reproduction

From the repository root:

```powershell
python problems/424/fanout/wave5/C50_active_frontier_audit.py --limit 10000000
```

The full run took `31.43` seconds.  The script prints its JSON certificate
to stdout and creates no data file.

```text
C50_active_frontier_audit.py
SHA-256 0D7168E3B048DA9BB9D906BEB0CC6E191C7104F7851BB2BE7180A0464E8D3467
```
