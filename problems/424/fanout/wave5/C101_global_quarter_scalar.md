# C101: global quarter scalar and a 3-adic ballot obstruction

## Verdict

The scalar inequality

\[
 A_H(X)\le D(X)+A_H(\lfloor X/4\rfloor)+1                 \tag{Q}
\]

is neither proved nor falsified here.  The returned result is an exact
finite structural falsifier to a source-independent arithmetic mechanism
which would imply `(Q)`.

Partition every root `r` only by the global arithmetic signature

\[
 \sigma(r)={\bf1}_{3\mid r+1}.                            \tag{1}
\]

Allow all-to-all pairing inside each signature class, with no factor,
matching, or ancestry restriction.  Even this maximally permissive
type-preserving ballot cannot use one exceptional token to prove `(Q)`.
Its first exact failure is

\[
                              \boxed{X=186}.              \tag{2}
\]

At this cutoff the nondivisible class needs two exceptions, while the
divisible class has one spare healed root.  The total scalar margin is
exactly `-1`, so `(Q)` itself holds with equality.  It holds only after a
bank unit is transferred across the partition (1).

Thus a proof by separate event ballots, monotone involutions, or cumulative
rank comparisons for the two basic `3`-adic divisor types is impossible.
Any arithmetic classification proof of `(Q)` must include a cross-type
transport law.  This obstruction uses no hard-source neighborhood and no
missing-factor ancestry.

## 1. Typed counts

Use the C92 definitions.  Let `H_X` be the hard roots persistent through
`X`, and let `D_X` be the structural splitless roots healed through `X`.
Put `q=floor(X/4)` and, for `i in {0,1}`, define

\[
\begin{aligned}
 H_i(X)&=\{h\in H_X:\sigma(h)=i\},\\
 D_i(X)&=\{e\in D_X:\sigma(e)=i\},\\
 A_i(X)&=|H_i(X)|,\qquad E_i(X)=|D_i(X)|,               \tag{3}
\end{aligned}
\]

and the signed type margin

\[
 F_i(X)=E_i(X)+A_i(q)-A_i(X).                            \tag{4}
\]

These are global cumulative counts.  No relation between an individual
hard root and an individual healed root has been imposed.

Summing (4) gives the exact C95 scalar margin

\[
 F_0(X)+F_1(X)=D(X)+A_H(q)-A_H(X).                       \tag{5}
\]

## 2. The falsified intermediate

Consider the following proposed proof mechanism.

> **Type-preserving one-exception ballot `(TP)`.**  Match the labelled set
> `H_X` injectively into the disjoint union
> \[
> D_X\sqcup H_q\sqcup\{\star\},                         \tag{6}
> \]
> requiring every nonstar image to have the same signature (1) as its
> source.

This is strictly more permissive than a source-local construction: within a
signature class every source may use every target.  By cardinality, `(TP)`
would imply `(Q)`.

### Lemma C101.1 (exact typed ballot criterion)

For a fixed cutoff `X`, `(TP)` holds if and only if

\[
 \sum_{i=0}^1 \max\{0,-F_i(X)\}\le1.                    \tag{7}
\]

### Proof

Before the singleton is used, type `i` has `A_i(X)` sources and
`E_i(X)+A_i(q)` eligible targets.  It therefore has deficit
`max(0,-F_i(X))`.  Since `star` can cover one source in only one class, the
sum of the two deficits must be at most one.

Conversely, if (7) holds, each nondeficient class can be injected into its
same-type target set.  There is at most one remaining source over both
classes, and it is sent to `star`.  QED.

The lemma concerns only cardinalities of global arithmetic classes.  In
particular, failure of (7) cannot be repaired by changing a local descent or
by adding more edges inside one class.

## 3. Exact counterexample at 186

The independent trial-divisor reconstruction gives

\[
 H_0(186)=\{54,114,144,174,186\},\qquad
 H_1(186)=\{74\},                                      \tag{8}
\]

and

\[
 D_0(186)=\{6,18,66\},\qquad
 D_1(186)=\{20,38\}.                                   \tag{9}
\]

There are no persistent hard roots through `q=floor(186/4)=46`.  Hence

\[
 (F_0(186),F_1(186))=(3-5,2-1)=(-2,1).                 \tag{10}
\]

Equation (7) has left side `2`, so `(TP)` is false even with the singleton.
On the other hand,

\[
 D(186)+A_H(46)-A_H(186)=5+0-6=-1,                    \tag{11}
\]

so `(Q)` holds with equality.  The one spare type-`1` target is exactly what
the untyped scalar count needs to cover the second type-`0` deficit.

For direct checks of (9), the five splitless chains first reach generated
values as follows:

```text
6  -> 11 -> 21 -> 41,   41+1  = 3*14
18 -> 35 -> 69,         69+1  = 5*14
20 -> 39 -> 77,         77+1  = 3*26
38 -> 75 -> 149,        149+1 = 3*50
66 -> 131,              131+1 = 3*44
```

The factors displayed on the right are generated.  Their successor shapes
are respectively `7`, `19`, `3*7`, `3*13`, and `67`, so the roots are in
the splitless classes of C96.  Exact divisor enumeration verifies that
these are all healed splitless roots through `186`, that (8) is the complete
persistent hard set, and that `H_46` is empty.

### Proposition C101.2 (global type obstruction)

No proof of `(Q)` can consist of independent type-preserving injections or
independent signed prefix ballots for the partition (1), with one common
exception and no transfer between the two types.

### Proof

Such a proof would produce `(TP)` at every cutoff.  Equations (8)-(10) and
Lemma C101.1 falsify `(TP)` at `X=186`.  QED.

This is a falsifier of the proposed intermediate, not of `(Q)`.

## 4. Exact computation

`C101_seed3_global_audit.py` uses an SPF table, ascending exact closure, and
complete admissible-divisor enumeration.  It checks the untyped and typed
event margins at every integer cutoff through `100000`.  It finds:

```text
first type-preserving one-exception failure: X=186
nonthree row at X=186: (A_H, D, A_H(q), F) = (5,3,0,-2)
three row at X=186:    (A_H, D, A_H(q), F) = (1,2,0, 1)
minimum nonthree F through 100000: -6 at X=6192
minimum total F through 100000:    -1 at X=186
```

The value at `6192` is a stronger finite failure of a separate nondivisible
ballot:

\[
 (A_0(6192),E_0(6192),A_0(1548))=(220,167,47),          \tag{12}
\]

so six same-type exceptions are required.  No bounded-error or asymptotic
claim is inferred from this finite row.

`C101_type_ballot_verify.py` is independent of the SPF scanner.  It uses
direct trial divisors, reconstructs the closure, scans every cutoff, and
stores the complete labelled certificate (8)-(9).  It proves by exhaustion
that `186` is the first failure of (7).  Normal and `python -O` runs through
`100000` are byte-identical.  The two implementations have the same
classification SHA-256 through `100000` and the same typed minima.

The initial computation also rejected a different global scalar shortcut.
Mapping a healed seed-3 root `r` to the seed-2 root of its mandatory
cofactor `(r+1)/3` is neither type-pure nor injective.  The first collision
is

\[
 32\longmapsto6,\qquad62\longmapsto6,                  \tag{13}
\]

with healing times `125` and `489`.  Through `100000`, the 782 healed
seed-3 roots have cofactor-root types

```text
splitless 471, hard 191, seed-3 120.
```

This reconnaissance is not used in Proposition C101.2; it records why the
proof attempt was redirected to the source-independent type ballot.

## 5. Reproduction

From the repository root:

```powershell
python problems/424/compute/wave5/C101_seed3_global_audit.py `
  --limit 100000 `
  --output problems/424/compute/wave5/C101_seed3_global_audit_100k.json

python problems/424/compute/wave5/C101_type_ballot_verify.py `
  --limit 100000 `
  --output problems/424/compute/wave5/C101_type_ballot_verify_100k.json

python -O problems/424/compute/wave5/C101_type_ballot_verify.py `
  --limit 100000 `
  --output problems/424/compute/wave5/C101_type_ballot_verify_100k_replay.json
```

SHA-256:

```text
E9A253A209EB540F2B0B740BB067BCF872830ACB132657BE64325F5D29190F05
  C101_seed3_global_audit.py
A954107DEE7A3CCAD5818631E387F7D02B39AC9FC1808E20DB9968451373B896
  C101_seed3_global_audit_100k.json
7298F4137E7C77CAC7246C780C7630B43994270210C35E3E41DBE77B33A5E655
  C101_type_ballot_verify.py
8B0E736383C66893BF6AA7CDAA863678DB330DEE712060F9460FC0A0A479A2C1
  C101_type_ballot_verify_100k.json
8B0E736383C66893BF6AA7CDAA863678DB330DEE712060F9460FC0A0A479A2C1
  C101_type_ballot_verify_100k_replay.json
```

The shared classification digest through `100000` is
`4ECBEA379DF3413BC1D640A3F67AB2359D86E89A43A771CD699BE57F1720BEA1`.

## 6. Relation to prior lanes and exact status

C95 and C97 falsify factor-local, critical-chain, and complete-ancestry
payments.  Proposition C101.2 does not restrict targets by a source: it
allows every target of the same global arithmetic type.  Its obstruction is
the need to move scalar capacity between divisor types.

C83 treats static local feature potentials in arbitrary grounded images.
C101 treats the actual least-closure event counts in the quarter recurrence.
C99 counts admissible divisor pairs and studies the C85 reciprocal bank;
C101 uses neither its sieve nor its witness-root basins.  The C100 artifacts
audit overlaps of fixed generated witnesses; they do not partition the hard
birth and splitless-healing event ballot in (5).

A repository search found no prior statement of criterion (7) or the typed
failure (10).  The official Problem 424 page, checked 2026-07-13, still
marks the problem open and lists no claimed partial or complete solution.

**Proved:** Lemma C101.1 and Proposition C101.2.

**Exact finite falsifier:** `(TP)` first fails at `X=186`; the nondivisible
class has deficit two while the total recurrence has deficit one.

**Not proved or falsified:** the untyped all-`X` inequality `(Q)`.  The
remaining direct scalar frontier must explain cross-type bank transfer; a
direct sum of divisor-type ballots cannot do so.
