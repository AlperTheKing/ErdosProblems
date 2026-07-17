# C92: common-bank ratio and quarter-scale obstruction

## Verdict

No uniform proof of

\[
  6D(X)\ge 5A_H(X)                                           \tag{C92}
\]

or of either proposed quarter-scale inequality is obtained here.  Exact
integer computation checks every cutoff through `4,000,000,000` and finds
no failure of

\[
 A_H(X)\le D(X)+A_H(\lfloor X/4\rfloor)+1,                  \tag{I}
\]

\[
 2D(X)\ge7A_H(\lfloor X/4\rfloor).                          \tag{II}
\]

This is finite census evidence, not a theorem.

Two rigorous conclusions delimit the proof frontier.

1. Either (I) or (II), by itself, proves `A_H(X)=o(X)` and hence the full
   density theorem by C72.  Thus neither is a routine auxiliary estimate.
2. Every hard root has a missing-factor descent to a hole root at most one
   quarter as large, but this descent has neither target eligibility nor
   bounded multiplicity.  At cutoff `450`, three persistent hard roots have
   forced descents to the same healed splitless root.  Consequently the
   quarter scale is explained, but a local injection is exactly false.

The remaining requirement is a genuinely nonlocal amortized control of the
many-to-one descent fibers.  No such control is proved.

## 1. Definitions

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\}
\]

and let `G` be the least subset of `A` containing `2,3` and closed under
`ab-1` for distinct `a,b in G`.  A factorization is admissible when

\[
 n+1=ab,\qquad 2\le a<b,\qquad a,b\in\mathcal A.            \tag{1}
\]

Put `U(n)=2n-1`.  Every hole belongs to the literal seed-2 chain

\[
 r,U(r),U^2(r),\ldots,qquad U^j(r)=2^j(r-1)+1,              \tag{2}
\]

of one even hole root `r`.

`A_H(X)` counts hard roots whose chain has not reached `G` by cutoff `X`.
`D(X)` counts structural splitless roots whose chain has reached `G` by
cutoff `X`.  Write `B_H(X)` for all hard roots at most `X` and `C_H(X)` for
hard roots whose first generated chain descendant is at most `X`.  Then the
root intervals give the exact identity

\[
 A_H(X)=B_H(X)-C_H(X).                                     \tag{3}
\]

## 2. Exact event form of (I)

Set `Y=floor(X/4)`.  Substituting (3) shows that (I) is exactly

\[
 B_H(X)-B_H(Y)
 \le D(X)+C_H(X)-C_H(Y)+1.                                \tag{4}
\]

Thus (I) does not merely compare two cumulative root counts.  Its left side
is the number of hard births in the quarter shell `(Y,X]`; its right side is
all splitless deaths through `X`, plus hard deaths in the same quarter
shell, plus one exceptional unit.

The independent event verifier checks the algebraic equality of the two
margins at every cutoff through `100,000`.  This is a replay of an identity,
not evidence toward its sign.

The harder-looking shell simplification

\[
 B_H(X)-B_H(\lfloor X/4\rfloor)\le D(X)+1                  \tag{5}
\]

is false.  Its first exact failure is

\[
 X=1404,\qquad B_H(X)-B_H(351)=51,qquad D(X)=49.           \tag{6}
\]

Likewise the local half-shell induction

\[
 6\bigl(D(X)-D(\lfloor X/2\rfloor)\bigr)
 \ge5\bigl(A_H(X)-A_H(\lfloor X/2\rfloor)\bigr)            \tag{7}
\]

first fails at `X=144`: its two sides are `12` and `15`.  Therefore neither
proposed inequality follows by discarding hard deaths or by summing
independent half-shell margins.

## 3. Each quarter inequality is theorem-strength

C13 proves that the structural splitless counting function `E(X)` satisfies

\[
 E(X)=o(X).                                                \tag{8}
\]

Since every root counted by `D` is splitless,

\[
 0\le D(X)\le E(X)=o(X).                                  \tag{9}
\]

### Proposition 3.1

If (I) holds for every sufficiently large integer `X`, then
`A_H(X)=o(X)`.

### Proof

Let

\[
 L=\limsup_{X\to\infty}{A_H(X)\over X}.
\]

The count is at most `X`, so `L` is finite.  Divide (I) by `X`, use (9),
and take the limsup.  The floor changes the argument by at most one, and

\[
 \limsup {A_H(\lfloor X/4\rfloor)\over X}\le {L\over4}.
\]

Hence `L<=L/4`, so `L=0`.  QED.

### Proposition 3.2

If (II) holds for every sufficiently large integer `X`, then
`A_H(X)=o(X)`.

### Proof

Put `X=4Y`.  Then `floor(X/4)=Y`, and (II) gives

\[
 A_H(Y)\le {2\over7}D(4Y)=o(Y)                             \tag{10}
\]

by (9).  QED.

C72 proves

\[
 A_H=o(X)\quad\Longleftrightarrow\quad H=o(X)
 \quad\Longleftrightarrow\quad M=o(X),                    \tag{11}
\]

where `M` is the full allowed-hole count.  Thus either proposition closes
the density theorem.  The absence of a short proof mechanism for (I) or
(II) is therefore a theorem-strength obstruction, not merely a missing
finite estimate.

## 4. Conditional contraction from (I) and (II)

Although either inequality already suffices asymptotically, their advertised
finite combination is exact.  Put

\[
 A=A_H(X),\qquad A_0=A_H(\lfloor X/4\rfloor),\qquad D=D(X).
\]

Then (I) and (II) give

\[
 A\le D+A_0+1\le {9\over7}D+1,                            \tag{12}
\]

or equivalently

\[
 D\ge {7\over9}A-{7\over9}.                              \tag{13}
\]

Here is the full consequence for the C67/C91 cut reduction.  Let `S` be a
Boolean-realizable source side.  If it has no unhealed hard root, then the
root-boundary identity gives `H(S)<=Q(S)`.  Otherwise every structural
splitless root counted by `D(X)` is a C87 common-bank root: it has no legal
factor pair, and its literal top is generated.  Hence

\[
 Q(S)\ge B_H(S)+D(X),                                      \tag{14}
\]

where `B_H(S)` counts healed hard roots in `S`.  Since unhealed hard roots
are among those counted by `A_H(X)`, (12) gives

\[
\begin{aligned}
 H(S)&\le A_H(X)+B_H(S)\\
     &\le {9\over7}D(X)+1+B_H(S)\\
     &\le {9\over7}\bigl(D(X)+B_H(S)\bigr)+1\\
     &\le {9\over7}Q(S)+1.                                \tag{15}
\end{aligned}
\]

Insert (15) into the exact C16 recurrence, with

\[
 Y=\lfloor(X+1)/2\rfloor,\qquad
 Z=\lfloor(X+1)/3\rfloor.
\]

Using C13's splitless error `o(X)` gives

\[
 M(X)\le {9\over7}M(Y)+M(Z)+o(X).                         \tag{16}
\]

The normalized coefficient is

\[
 {9\over14}+{1\over3}={41\over42}<1,                     \tag{17}
\]

so the standard limsup contraction forces `M(X)=o(X)`.

More generally, a proved estimate

\[
 D(X)\ge\alpha A_H(X)-C,qquad \alpha>3/4,                \tag{18}
\]

would yield

\[
 H(S)\le\alpha^{-1}Q(S)+O(1)
\]

and normalized coefficient

\[
 {1\over2\alpha}+{1\over3}<1.                            \tag{19}
\]

This proves the requested density consequence without hiding any use of
the desired conclusion.

## 5. Proved quarter descent and its exact failure as an injection

### Lemma 5.1 (hard roots descend below one quarter)

Let `h` be a hard root and let `h+1=ab` be any admissible factorization.
Every endpoint is at most `(h+1)/5`.  At least one endpoint is a hole, and
the seed root of that endpoint is at most `h/4`.

### Proof

The product `h+1` is odd.  A hard root has no admissible seed-3
factorization: either `3` does not divide `h+1`, or its cofactor is forbidden
or equal to `3`.  Hence an admissible pair cannot contain `2` or `3`, so its
smaller endpoint is at least `5`.  If `a<b`, then

\[
 b={h+1\over a}\le {h+1\over5};
\]

both endpoints are at most `b`.  Since `h` is a hole, no admissible pair has
both endpoints generated, so at least one endpoint `p` is a hole.  Its
seed root is at most `p`.  Finally `(h+1)/5<=h/4` for `h>=4`.  QED.

This lemma explains the appearance of the quarter scale.  It does not prove
(I), because the lower root need not be in `D` or `A_H`, and many hard roots
can have the same forced lower root.

### Proposition 5.2 (capacity-one local descent is false)

At cutoff `450`, the roots

\[
 54,\quad186,\quad450                                      \tag{20}
\]

are all hard and persistent.  Their unique admissible pairs are

\[
 55=5\cdot11,\qquad187=11\cdot17,\qquad451=11\cdot41.     \tag{21}
\]

The values `5,17,41` are generated, while `11` is a hole on the splitless
chain rooted at `6`.  The root `6` is healed at `41`, because

\[
 41+1=3\cdot14
\]

with `3,14` distinct and generated.  Thus every missing-factor-root descent
from each source in (20) is forced to the same `D`-root `6`.

The visible chains through `450` are

```text
54  : 54, 107, 213, 425
186 : 186, 371
450 : 450
```

and every displayed value is a hole.  The exact verifier reconstructs all
factor pairs and checks these claims without assertions.  They can also be
checked directly.  The values `5=2*3-1`, `9=2*5-1`, `17=2*9-1`,
`14=3*5-1`, and `41=3*14-1` are generated.  The root `6` is splitless
because `7` is prime; `11` and `21` remain holes from the forced pairs
`12=2*6` and `22=2*11`; then `41` is the first generated member of that
chain.  The displayed hard roots have exactly the pairs in (21).  Finally,
direct factor enumeration for successors `108,214,426,372` shows that each
admissible pair contains one of the already listed holes (or a forbidden
factor), proving persistence of the displayed chains.

Therefore even a
single exceptional source cannot repair a capacity-one local injection:
after discarding one of the three sources, two still demand the same target.

This proposition does not falsify (I) or (II).  It proves that their payment
must use unrelated splitless chains or another global amortization, exactly
as the C65 flow examples already suggest.

## 6. Exact census

The main scanner reconstructs `G` in ascending order by enumerating every
divisor pair satisfying (1).  It uses integer states, integer counters, and
integer cross-products.  At every cutoff it checks (C92), (I), and (II).

The optimized implementation stores only the first quarter of the `A_H`
trajectory, since later entries are never queried by the scale gates.  The
`4,000,000,000` run used one CPU thread and completed in `216.961` seconds.

At the endpoint:

```text
A_H(4,000,000,000) =  54,874,815
D(4,000,000,000)   = 159,942,262
hard births        = 106,360,959
hard deaths        =  51,486,144
splitless births   = 342,851,452
splitless deaths   = 159,942,262
```

There are zero failures among all `3,999,999,947` cutoffs with positive
`A_H`.  The global minimum of `D/A_H` remains

\[
 {D\over A_H}={5\over6}\quad\text{at }X=186,              \tag{22}
\]

and the minimum C92 margin is zero there.  Both quarter-scale scans also
have zero failures; the nontrivial minimum margin of (I) is zero at `186`.

An independent Python verifier reconstructs factor pairs by direct trial
division, imports no project arithmetic code, and agrees through `100,000`
on every checkpoint, endpoint count, minimum, and both scale gates.  Normal
and `python -O` outputs are byte-identical.

The memory-optimized C++ scanner was also replayed through `10^9`.  After
removing the nonsemantic timing field, its structured JSON is exactly equal
to the pre-optimization artifact.  The replay artifact has SHA-256
`EB816AF044FA5F01F66EF24B8D08C8B0FE2F0675C539939DBA27B727896CAE43`.

## 7. Reproduction

```powershell
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wconversion -Wshadow `
  -march=native `
  -o problems/424/compute/wave5/C92_common_bank_ratio.exe `
  problems/424/compute/wave5/C92_common_bank_ratio.cpp

problems/424/compute/wave5/C92_common_bank_ratio.exe `
  4000000000 `
  problems/424/compute/wave5/C92_common_bank_ratio_4e9.json

python problems/424/compute/wave5/C92_common_bank_verify.py `
  --limit 100000 `
  --output problems/424/compute/wave5/C92_common_bank_verify_100000.json

python -O problems/424/compute/wave5/C92_common_bank_verify.py `
  --limit 100000 `
  --output problems/424/compute/wave5/C92_common_bank_verify_100000_replay.json

python problems/424/compute/wave5/C92_event_obstruction.py `
  --limit 100000 `
  --output problems/424/compute/wave5/C92_event_obstruction_100000.json
```

Current SHA-256 values are

```text
B45EF9F9CDD232A3DB9FF337211020F0F70165B95A943C9711BB0A998DDC7DE4
  C92_common_bank_ratio.cpp
D1D01C95A73C9BC9AAACBA211D7A8746DB501FAFD4E7E011025E007915E106ED
  C92_common_bank_verify.py
3391E75CF2E629FD7AA6B09D5B47E2646D43647723C6A1EA0595A36447CCC80E
  C92_common_bank_ratio_4e9.json
90A5C4C8F97BF6F326AB41D49BB029D49839E64DEA5DDFC9C2FF02EB47C3D578
  C92_common_bank_verify_100000.json
A29DE7D9D43538E22150FB9A03AF694C215B1F5747C31D00BDAD895DB6DCFE54
  C92_event_obstruction.py
84653A9ED938004766F9D9B8FC40E35B9B036213D0DDB8552EE83E537AB8DE54
  C92_event_obstruction_100000.json
```

## 8. Exact status

**Proved:** the event identity (4), the conditional density implications,
the quarter-descent lemma, and the capacity-one obstruction.

**Exact finite census:** zero failures of (C92), (I), and (II) at every
cutoff through `4,000,000,000`, with an independent replay through
`100,000`.

**Not proved:** any all-`X` lower bound `D(X)>=alpha A_H(X)-O(1)` with
`alpha>3/4`, including (C92), (I), and (II).  The open structural step is a
global amortized bound on the multiplicities of quarter-scale missing-factor
descents.  Proving either quarter inequality would already prove the full
density theorem.
