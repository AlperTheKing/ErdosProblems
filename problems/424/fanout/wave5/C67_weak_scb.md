# C67: weak seed-chain cut bound

## Verdict

The full sharp C60 cut theorem is stronger than the density argument needs.
For Boolean-realizable C60 cuts there is an exact seed-chain identity

\[
 H(S)-Q(S)=U_H(S)-B_E(S)-B_3(S),                    \tag{1}
\]

where `U_H` counts source-side hard roots whose seed-2 chain has no boundary,
and `B_E,B_3` count boundaries on splitless-root and seed-3-root chains.
Consequently the following uniform asymptotic statement is sufficient:

\[
 \boxed{\sup_S\{U_H(S)-U_E(S)\}=o(X).}              \tag{WRC}
\]

Here the supremum is over the Boolean-realizable C60 source sides at cutoff
`X`, and `U_E` is the analogous number of unhealed splitless-root chains.
Since the total number `E(X)` of structural splitless holes is `o(X)`, WRC
implies `H(S)<=Q(S)+o(X)` uniformly.  The C16 recurrence then gives

\[
 M(X)\le M(\lfloor(X+1)/2\rfloor)
       +M(\lfloor(X+1)/3\rfloor)+o(X),               \tag{2}
\]

and hence `M(X)=o(X)` and density `2/3`.

The stronger zero-error version

\[
 \boxed{U_H(S)\le U_E(S)}                            \tag{ORC}
\]

has no counterexample in an exhaustive exact max-closure scan at every
cutoff through `2000`, or at the selected cutoffs through `10^6`.  This is
finite evidence, not a proof.  Two tempting multiplicative strengthenings
are exactly false: `11 U_H <= 5 U_E` first fails at `X=539`, and
`2 U_H <= U_E` first fails at `X=1223`.

A cut-independent sufficient statement is also isolated below.  It survived
every cutoff through `10^6`, but likewise remains unproved.  C67 therefore
reduces the density problem to a weaker arithmetic statement and kills two
overstrong versions; it does not prove the density theorem.

## 1. Boolean-realizable C60 cuts

Fix `X`, and use the C60 notation.  Thus `M_X` is the set of holes, `K_X`
the hard holes, and `E_X` the structural splitless holes.  A C60 source side
is a set `S subset M_X` which contains `E_X` and is closed under every unary
generated-factor descent

\[
 n=gp-1,\quad g\in G_X,\ p\in M_X,
 \qquad n\in S\Longrightarrow p\in S.                \tag{3}
\]

For the source side to come from a Boolean forward-closed set, it also obeys
the contrapositive of seed-2 closure:

\[
 2m-1\in S\Longrightarrow m\in S.                    \tag{4}
\]

Call such an `S` Boolean-realizable.  This is a restriction of the arbitrary
C60 cut class, but it includes the source side `S=M_X` associated with the
actual least generated set, which is the side needed in C16.

Every odd hole `n` has the hole parent `(n+1)/2`.  Iterating this parent map
ends at a unique even hole, called its seed-2 root.  Thus the holes are
partitioned into chains

\[
 r,quad 2r-1,quad 4r-3,quad\ldots,
 \qquad U^i(r)=2^i(r-1)+1.                            \tag{5}
\]

Every even root is exactly one of the following:

* a hard root;
* a structural splitless root;
* a seed-3 reducible root.

Both hard and splitless holes are even, so no such hole lies strictly inside
another root's chain.

For a root `r`, let `top_X(r)` be the largest literal iterate in (5) not
exceeding `X`.  A root included in `S` is **unhealed** if `top_X(r) in S`.
Otherwise it is **healed**.  Write `U_H,U_E,U_3` for the numbers of unhealed
included roots of the three types, and `B_H,B_E,B_3` for the corresponding
healed counts.

### Lemma C67.1 (root-boundary identity)

For every Boolean-realizable C60 source side,

\[
 H(S)=U_H+B_H,
 \qquad
 Q(S)=B_H+B_E+B_3,                                   \tag{6}
\]

and hence (1) holds.

### Proof

Condition (4) makes membership in `S` a prefix on each hole chain.  An
included prefix either reaches the literal top, in which case it is
unhealed, or ends at exactly one seed arc from `S` to its complement (or to
a generated seed child), in which case it is healed.  Thus every healed
included root contributes exactly one unit to `Q`, and no unhealed or
excluded root contributes.  Hard vertices occur only as roots, so the hard
members of `S` are exactly the unhealed and healed hard roots.  This proves
(6), and subtraction proves (1).  QED.

This identity is the point at which the sharp C60 demand disappears: the
hard boundaries `B_H` cancel exactly.  Only hard chains with no boundary
remain unpaid.

## 2. Density consequence

### Lemma C67.2 (WRC is sufficient)

Assume WRC uniformly over all Boolean-realizable C60 source sides.  Then the
least generated set has natural density `2/3` in the allowed residue
classes, equivalently `M(X)=o(X)`.

### Proof

By C13, `E(X)=o(X)`.  Since `U_E(S)<=E(X)`, (1) and WRC give

\[
 H(S)-Q(S)
 \le U_H(S)
 \le U_E(S)+o(X)=o(X).                                \tag{7}
\]

Apply this to `S=M_X`.  C16 gives, with

\[
 Y=\lfloor(X+1)/2\rfloor,
 \qquad Z=\lfloor(X+1)/3\rfloor,
\]

the exact decomposition

\[
 R(X)=M(Y)-Q(X)+S_3(X)+H(X),                           \tag{8}
\]

and `S_3(X)<=M(Z)`.  Since `M=E+R`, equations (7)--(8) prove (2).

Let `L=limsup M(X)/X`, which is finite.  Along a sequence attaining this
limsup, divide (2) by `X` and use `Y/X -> 1/2` and `Z/X -> 1/3`.  Then

\[
 L\le\frac12L+\frac13L=\frac56L,
\]

so `L=0`.  QED.

More generally, a uniform estimate `H(S)<=cQ(S)+o(X)` closes the same
recurrence whenever `c<4/3`.  For `1<=c<4/3`, use `Q(X)<=M(Y)` in (8) to
obtain

\[
 M(X)\le cM(Y)+M(Z)+o(X),
\]

whose normalized coefficient is `c/2+1/3<1`.  For `c<=1`, discard the
nonpositive `(c-1)Q` term and recover (2).  Thus a statement written as
`H<=(2-epsilon)Q+o(X)` is sufficient by this route only when
`epsilon>2/3`.  The root formulation targets the cleaner coefficient `1`.

## 3. Exact max-closure gate

For fixed `X`, maximizing `U_H-U_E` over Boolean-realizable source sides is
an integral maximum-closure problem.

* Put weight `+1` on `top_X(r)` for every hard root whose literal top is a
  hole.
* Put weight `-1` on the analogous splitless-root terminals.
* Force every structural splitless root into the source side.
* Add infinite arcs for (3) and for every reverse seed edge in (4).

An integral `s-t` min cut gives the exact maximum.  `C67_weak_scb.py` uses
integer capacities and independently replays the residual source side and
the root-boundary counts.  No floating-point value is used for acceptance.

Selected exact maxima are:

| `X` | `max_S(U_H-U_E)` | maximizing `U_H` | maximizing `U_E` |
|---:|---:|---:|---:|
| 74 | -5 | 2 | 7 |
| 318 | -17 | 9 | 26 |
| 539 | -22 | 19 | 41 |
| 1,223 | -43 | 44 | 87 |
| 5,000 | -139 | 196 | 335 |
| 100,000 | -2,386 | 3,386 | 5,772 |
| 1,000,000 | -25,834 | 27,056 | 52,890 |

The scan checked every cutoff `2<=X<=2000`; none had a positive maximum.
The larger rows are selected cutoffs only.

### Exact falsifiers to stronger root bounds

The same closure optimization, with integer vertex weights, finds:

1. At `X=539`, a feasible source side has
   `U_H=19`, `U_E=41`, so

   \[
   11U_H-5U_E=209-205=4>0.                             \tag{9}
   \]

   Exhaustion of every smaller cutoff finds no such failure.

2. At `X=1223`, a feasible source side has
   `U_H=44`, `U_E=87`, so

   \[
   2U_H-U_E=88-87=1>0.                                \tag{10}
   \]

   Again this is the first failure in the exhaustive cutoff scan.

The complete integer source sides are stored in `C67_weak_scb.json`.  These
examples do not refute ORC; they show that a proof cannot obtain the desired
reserve by replacing coefficient `1` with either tested smaller coefficient.

## 4. A cut-independent terminal budget

Let `A_H(X)` be the number of hard roots `r<=X` for which every literal
seed-2 iterate through `top_X(r)` remains a hole.  Let

\[
 e^+(X)=E(X)-E(\lfloor X/2\rfloor)                    \tag{11}
\]

be the number of structural splitless holes in the upper half shell.
Every splitless root in that shell is forced into every source side and has
no seed child at most `X`.  Therefore

\[
 U_H(S)\le A_H(X),
 \qquad U_E(S)\ge e^+(X).                             \tag{12}
\]

It follows that the scalar estimate

\[
 \boxed{A_H(X)\le e^+(X)+o(X)}                        \tag{TB}
\]

implies WRC.  TB is stronger than WRC but is strictly weaker than requiring
all hard holes to be sparse through a pointwise boundary assignment: healed
hard roots are omitted before any charging begins.

An exact incremental scan at every cutoff through `10^6` found no failure
of the zero-error inequality `A_H(X)<=e^+(X)`.  Its largest observed ratio
was

\[
 {A_H(X)\over e^+(X)}={656\over1033}
 \quad\hbox{at }X=16620.                              \tag{13}
\]

For comparison, even the stronger finite statement

\[
 |K_X|\le e^+(X)                                      \tag{14}

had no failure through `10^6`; its largest ratio was
`8846/9907` at `X=175956`.  Neither (13) nor (14) is extrapolated.

## 5. Why the available mechanisms do not prove WRC

### Two-step seed-2 arithmetic

C58 proves that every missing endpoint of a hard factorization lies on a
seed-2 chain and that two successors remain below the hard output.  The
needed re-entry conclusion is false.  At `X=74`, the hard hole

\[
 74+1=5\cdot15
\]

has the missing endpoint chain `15,29,57`, all outside the least generated
set, while the actual seed boundaries are in unrelated components.  Thus a
proof cannot charge each unhealed hard root to a boundary in one of its own
factor chains.

### Componentwise splitless charging

At `X=318`, canonical component charging has the exact deficit

\[
 \{54,74,186,318\}\longrightarrow\{41,57,63\}.        \tag{15}
\]

There are four hard sources and only three component-local targets.  ORC
survives at this cutoff with the global counts `U_H=9`, `U_E=26`; it
deliberately pools splitless terminal capacity across components.  Any proof
which refines ORC back to the failed component injection loses this feature.

### Uncorrelated predecessor capacity

C59's many-predecessor inequality cannot supply the global charge.  Its raw
capacity has a harmonic contribution on every earlier dyadic scale; even
the structural splitless family `q-1`, for primes `q=1 mod 3`, contributes

\[
 \left({1\over8}+o(1)\right)X\log\log X.
\]

Consequently one cannot sum independent capacities for all hard
predecessors and then divide by a fixed multiplicity.  A proof of WRC or TB
must correlate the chosen predecessor incidences with seed-chain survival,
or establish a genuinely global dyadic cancellation.  No such correlation
is proved here.

These three failures explain the scope of the result: (1) is proved, WRC is
sufficient, and ORC/TB pass substantial exact gates, but the arithmetic
inequality itself remains the frontier.

## 6. Reproduction

From the repository root:

```powershell
python problems/424/fanout/wave5/C67_weak_scb.py `
  --limits 74 318 539 1223 5000 100000 1000000 `
  --scan-max 2000 `
  --output problems/424/fanout/wave5/C67_weak_scb.json

python problems/424/fanout/wave5/C67_weak_scb.py `
  --limits 74 --scalar-scan-max 1000000 `
  --output problems/424/fanout/wave5/C67_scalar_scan.json
```

The first command performs the exhaustive weighted first-failure scans and
the selected large max-closure probes.  The second scans TB and (14) at
every cutoff through `10^6`.

Re-running both commands with `python -O` produced byte-identical JSON.  The
SHA-256 values are:

```text
C67_weak_scb.py          49003A8603A97DFA43A2778611412BF4813E60D6F1DB71B1DBF40DFF8AE6B546
C67_weak_scb.json        B8AD8E8E9D8F41B916E0CF8770895EA9CF0366A75F711DDAFCD60AAD9F0B6831
C67_scalar_scan.json     DACAA78B5CDC484112285CA859660DF87CECD463EC7063919EA54E50BB2D6C10
```
