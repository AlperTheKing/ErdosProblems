# C72: persistent hard-chain sieve

## Verdict

No estimate `A_H(X)=o(X)` is proved.  There is a precise obstruction: if
`H(X)` counts all hard roots, then

\[
 H(X)-H\!\left(\left\lfloor{X+1\over2}\right\rfloor\right)
 \le A_H(X)\le H(X),                                      \tag{1}
\]

and therefore

\[
 \boxed{A_H(X)=o(X)\quad\Longleftrightarrow\quad H(X)=o(X).} \tag{2}
\]

Using C13 and the exact C16 recurrence, these are also equivalent to
`M(X)=o(X)`.  Thus C67's scalar terminal budget

\[
 A_H(X)\le E(X)-E(\lfloor X/2\rfloor)+o(X)                \tag{TB}
\]

is asymptotically equivalent to the full density-`2/3` conclusion, not a
strictly weaker tail-sparsity statement.

There is nevertheless an exact arithmetic map for persistent roots old
enough to expose a selected factor `3`.  It injects them into holes below
`(X+1)/3`.  Its image is not confined to splitless holes: the first
counterexample is the persistent hard root `174` at `X=347`, which maps to
the reducible seed-3 root `116`.  At `X=10^6`, the map handles only `2,102`
of the `27,056` persistent hard roots; its images comprise `1,345`
splitless, `337` seed-3, and `420` hard holes.

The natural exact map `r -> top_X(r)` is injective into upper-half holes,
but every one of its images is reducible.  Combining several fixed
generated divisors also loses injectivity: the least-depth rule on
`3,5,9,17,27,33` first maps both `846` and `1410` to the hard hole `564`
at cutoff `2819`.

## 1. Fresh-root obstruction

Retain the C67 definitions.  Put `U(n)=2n-1`, let `H(X)` count hard roots
through `X`, and let `A_H(X)` count hard roots `r<=X` for which every
`U^j(r)<=X` is a hole.

### Theorem 1 (fresh-shell equivalence)

For every integer `X>=2`, equation (1) holds.  Consequently, equation (2)
holds.

### Proof

Put

\[
 Y=\left\lfloor{X+1\over2}\right\rfloor.
\]

Every hard root `r` with `Y<r<=X` has `U(r)=2r-1>X`.  Its literal chain
through `X` therefore consists only of `r`, which is a hole by definition.
It is counted by `A_H(X)`.  This proves the lower bound in (1); the upper
bound follows because every root counted by `A_H` is hard.

Only the forward implication in (2) needs proof.  Define

\[
 D(X)=H(X)-H\!\left(\left\lfloor{X+1\over2}\right\rfloor\right).
\]

If `A_H(X)=o(X)`, then (1) gives `D(X)=o(X)`.  Starting at `X_0=X`, put

\[
 X_{i+1}=\left\lfloor{X_i+1\over2}\right\rfloor.
\]

The differences telescope:

\[
 H(X)=\sum_{i=0}^{k-1}D(X_i)+H(X_k)                       \tag{3}
\]

for every `k`.  Given `epsilon>0`, choose `N` such that
`D(t)<=epsilon t` for `t>=N`, and stop at the first `X_k<N`.  Since
`X_i<=X/2^i+1`, equation (3) gives

\[
 H(X)\le 2\epsilon X+O(\epsilon\log X)+H(N).
\]

Divide by `X` and let `X` tend to infinity, then let `epsilon` tend to zero.
This proves `H(X)=o(X)`.  The reverse implication follows from
`A_H(X)<=H(X)`.  QED.

### Corollary 2 (collapse of the scalar target)

With the proved C13 estimate `E(X)=o(X)` and the exact C16 partition,

\[
 \boxed{\text{(TB)}\Longleftrightarrow A_H=o(X)
 \Longleftrightarrow H=o(X)\Longleftrightarrow M=o(X).}    \tag{4}
\]

### Proof

The upper-half splitless count

\[
 e^+(X)=E(X)-E(\lfloor X/2\rfloor)
\]

satisfies `0<=e^+(X)<=E(X)=o(X)`.  Hence (TB) implies `A_H=o(X)`, while
`A_H=o(X)` implies (TB) by using `A_H(X)` itself as the `o(X)` error.
Theorem 1 gives the middle equivalence.

Finally, `H(X)<=M(X)`, so `M=o(X)` implies `H=o(X)`.  Conversely, C16 gives

\[
 R(X)=M(Y)-Q(X)+S(X)+H(X),\qquad S(X)\le M(Z),             \tag{5}
\]

where `Z=floor((X+1)/3)` and `M=E+R`.  If `H=o(X)`, then (5) and C13 give

\[
 M(X)\le M(Y)+M(Z)+o(X).
\]

The normalized coefficient is `1/2+1/3=5/6`, so the C16 limsup argument
gives `M=o(X)`.  QED.

Equation (4) is the main obstruction in this lane.  Any proof of
`A_H=o(X)` must already control the hard roots born in the current top
half, where persistence imposes no additional chain condition.

## 2. The upper-half top map misses `E`

### Lemma 3 (exact reducible-shell injection)

For fixed `X`, the map

\[
 r\longmapsto top_X(r)                                    \tag{6}
\]

is an injection from the roots counted by `A_H(X)` into the reducible holes
in `(Y,X]`.  Its image is disjoint from the structural splitless set.

### Proof

Let `t=top_X(r)`.  Since `U(t)>X`, one has `t>Y`.  Persistence makes `t` a
hole.  Different roots have disjoint seed-2 chains, so (6) is injective.

If `t=r`, then `t` is hard and hence reducible.  Otherwise
`t=U(s)=2s-1` for the preceding allowed chain member `s`; the distinct
allowed pair `(2,s)` factors `t+1`.  Thus `t` is reducible in both cases and
cannot be splitless.  QED.

This kills the canonical same-chain injection to the upper-half splitless
bank.  More generally, if a lower splitless hole `e` is moved upward by one
or more seed-2 steps, every iterate `U^j(e)`, `j>=1`, has the admissible
split `(2,U^(j-1)(e))` and is no longer splitless.

Any unrelated injection of all persistent roots into upper-half splitless
holes would imply

\[
 H(X)-H(Y)\le e^+(X)=o(X),
\]

which telescopes to `H=o(X)` by Theorem 1.  Such an injection is therefore
already a proof of the full conclusion in (4), not a consequence of the
known splitless characterization alone.

## 3. A proved factor-3 gate

The hard-shape residues modulo `9` are exactly

\[
                         0,2,3,6\pmod 9.                  \tag{7}
\]

Indeed, a reducible even hole in residue `5` or `8` has the usable seed-3
factorization, apart from `8`, where `9=3^2` violates distinctness and the
hole is splitless.  Residues `0,3,6` have no seed-3 factorization, while in
residue `2` the putative seed-3 cofactor is forbidden modulo `3`.

For a hard root `r`, define

\[
 j(r)=
 \begin{cases}
 0,&r=0\text{ or }3\pmod9,\\
 1,&r=2\pmod9,\\
 2,&r=6\pmod9,
 \end{cases}                                             \tag{8}
\]

and set

\[
 n(r)=U^{j(r)}(r),\qquad
 \phi(r)={2n(r)\over3},\qquad
 c(r)=U(n(r))=3\phi(r)-1.                                \tag{9}
\]

### Lemma 4 (mature factor-3 injection)

For every `X`, the map `phi` is injective on

\[
 B_3(X)=\{r:r\text{ is counted by }A_H(X),\ c(r)\le X\}, \tag{10}
\]

and its image lies in

\[
 \mathcal M\cap\left[2,\left\lfloor{X+1\over3}\right\rfloor\right]. \tag{11}
\]

Consequently, if `H_R(I)` counts hard roots in interval `I` whose residue
modulo `9` lies in `R`, then

\[
\begin{aligned}
 A_H(X)\le{}&M\!\left(\left\lfloor{X+1\over3}\right\rfloor\right)\\
 &+H_{\{0,3\}}((X+1)/2,X]\\
 &+H_{\{2\}}((X+3)/4,X]\\
 &+H_{\{6\}}((X+7)/8,X].                                \tag{12}
\end{aligned}
\]

### Proof

Applying `U(x)=2x-1` modulo `9` to the four cases in (7) shows that
`n(r)` is `0` or `3 modulo 9`.  Thus `3|n(r)`, and `phi(r)` is an even
allowed integer.  If `r` belongs to (10), persistence says that `c(r)` is
a hole.  But

\[
                         c(r)+1=3\phi(r).
\]

The factors are distinct, `3` is generated, and `phi(r)` is allowed.  If
`phi(r)` were generated, this pair would generate `c(r)`, a contradiction.
Hence `phi(r)` is a hole, and `c(r)<=X` gives the bound in (11).

The image `phi(r)` determines `n(r)=3phi(r)/2`.  A hole belongs to a unique
seed-2 chain and hence has a unique even root, so it determines `r`.
Therefore `phi` is injective.

The roots outside (10) obey `c(r)>X`.  Equations (8)-(9) give respectively

\[
 2r-1>X,\qquad4r-3>X,\qquad8r-7>X,
\]

in the three residue cases.  Counting these exceptional annuli and using
the injection for (10) proves (12).  QED.

Equation (12) is rigorous, but it does not contract: it targets the unknown
hole count `M`, and its three fresh hard annuli can have linear size without
the conclusion of Theorem 1.

## 4. Fixed generated divisors do not reach the splitless bank

The factor-3 proof is an instance of the following exact observation.  Let
`g` be an odd generated value.  If `n` and `U(n)` are holes, `g|n`, and

\[
 q={2n\over g}
\]

is allowed and distinct from `g`, then `q` is a hole, because
`U(n)+1=gq`.  For a fixed `g`, the map `n->q` is injective.  However, it
lands in all holes, not in `E`.

The audit found the following first non-splitless image for each tested
generated divisor.  "First" means least child cutoff, exhaustively checked
through `10^6`.

| `g` | hard root | chain parent `n` | hole child `U(n)` | image `q` | type of `q` |
|---:|---:|---:|---:|---:|---|
| 3 | 174 | 174 | 347 | 116 | seed-3, `117=3*39` |
| 5 | 1,110 | 1,110 | 2,219 | 444 | hard, `445=5*89` |
| 9 | 144 | 144 | 287 | 32 | seed-3, `33=3*11` |
| 17 | 884 | 884 | 1,767 | 104 | seed-3, `105=3*35=5*21` |
| 27 | 1,404 | 1,404 | 2,807 | 104 | seed-3 |
| 33 | 3,102 | 3,102 | 6,203 | 188 | seed-3, `189=3*63=9*21` |

The first row is already an exact counterexample to the claim that the
proved map in Lemma 4 lands in splitless holes.  All values in the displayed
source chain through the child are holes.

Using several divisors does not preserve injectivity without retaining the
divisor as a color.  Order `3,5,9,17,27,33`, and for each persistent root
choose the least chain depth and then the first divisor giving an allowed
image.  At `X=2819`,

\[
 1691+1=3\cdot564,\qquad 2819+1=5\cdot564.                \tag{13}
\]

The roots `846` and `1410` are both hard and persistent at this cutoff:
their visible chains are `846,1691` and `1410,2819`.  The rule maps both to
the hard hole `564`, for which `565=5*113`.  This is the first collision for
that exact rule through `10^6`.

There is also a scale mismatch with the requested upper-half bank.  Every
fixed-divisor image exposed by a child at most `X` satisfies

\[
                         q\le {X+1\over g}\le {X+1\over3}. \tag{14}
\]

If `q` happens to be splitless, seed-2 lifting cannot move it into the upper
half while preserving splitlessness, by Lemma 3.  A successful map to
upper-half splitless holes must therefore introduce genuinely nonlocal
arithmetic targets.

## 5. Exact gates

`C72_persistent_hard_sieve.py` imports C67's arithmetic constructor, checks
the distinct-factor convention, and sweeps every integer cutoff through the
requested limit.  Selected rows are:

| `X` | `H(X)` | `A_H(X)` | fresh hard top half | mature factor-3 | `e^+(X)` |
|---:|---:|---:|---:|---:|---:|
| 74 | 2 | 2 | 2 | 0 | 7 |
| 318 | 10 | 9 | 6 | 2 | 26 |
| 10,000 | 518 | 391 | 265 | 67 | 643 |
| 1,000,000 | 45,583 | 27,056 | 21,815 | 2,102 | 52,890 |

The all-cutoff checks found:

* no failure of the fresh-shell lower bound (1);
* no splitless member on any hard-root chain through `10^6`;
* `3,672` globally distinct factor-3 images over all mature intervals;
* no failure of `A_H(X)<=e^+(X)` through `10^6`, with the C67 maximum
  ratio `656/1033` at `X=16620`.

The final scalar inequality is finite evidence only.  It is not used in any
proof above.

`C72_verify_small.py` is an independent trial-divisor constructor: it does
not import C67.  Through `12,000` it reproduces the first collision (13),
finds no failure of (1), and independently gives at `X=5,000`

```text
(H, A_H, mature factor-3, e^+) = (253, 196, 36, 335).
```

## 6. Reproduction and prior-art check

From the repository root:

```powershell
python -m py_compile problems/424/compute/wave5/C72_persistent_hard_sieve.py

python problems/424/compute/wave5/C72_persistent_hard_sieve.py `
  --limit 1000000 `
  --output problems/424/compute/wave5/C72_persistent_hard_sieve_1e6.json

python -O problems/424/compute/wave5/C72_persistent_hard_sieve.py `
  --limit 1000000 `
  --output problems/424/compute/wave5/C72_persistent_hard_sieve_1e6_replay.json

python problems/424/compute/wave5/C72_verify_small.py `
  --limit 12000 `
  --output problems/424/compute/wave5/C72_verify_small_12000.json

python -O problems/424/compute/wave5/C72_verify_small.py `
  --limit 12000 `
  --output problems/424/compute/wave5/C72_verify_small_12000_replay.json
```

The ordinary and optimized outputs are byte-identical.  SHA-256:

```text
C72_persistent_hard_sieve.py          17B4EE4C0EE0BDE9302136652701F55BD4E14634EF4AE2C72036FDCEEF5D56D2
C72_persistent_hard_sieve_1e6.json    2216AB7EC44275B147210B52BBCBEB07606DCBE93E08C6D4341D2B972117BDD1
C72_persistent_hard_sieve_1e6_replay.json
                                      2216AB7EC44275B147210B52BBCBEB07606DCBE93E08C6D4341D2B972117BDD1
C72_verify_small.py                   FF750F138C072BD68A5CC7EB0A3B786055B00AFF258205BAF274A58185952307
C72_verify_small_12000.json           26AF30127E2023D2139EE4A8DF8F2EF749DF084751DD5B486455189CF2304F1F
C72_verify_small_12000_replay.json
                                      26AF30127E2023D2139EE4A8DF8F2EF749DF084751DD5B486455189CF2304F1F
```

A repository search found no earlier statement of Theorem 1 or Lemma 4.
The official problem page, checked 2026-07-13, still lists Problem 424 as
open and lists no partial solution.  The proved results here are internal
reductions and obstructions; no claim about the original positive-density
question is made.
