# C80: exact obstruction to blocker-local least-counterexample induction

## Proposition

The C78 shell identity gives the following exact first-failure normal form,
but the induction step does not follow from complete factor-blocker descent.
There is a genuine infinite forward-closed source

\[
 S=\operatorname{Cl}\{2,3,21\}
\]

and cutoff `74` for which `T=F(S)` has

\[
 Q_T(73)-H_T(73)=1,\qquad Q_T(74)-H_T(74)=0.
\]

The unhealed hard roots at `74` are `{54,74}` and the healed nonhard roots
are `{6,18}`.  Closing either hard root under every missing factor at every
missing point of every recursively reached seed-2 chain gives

\[
 54\longmapsto\{6\},\qquad 74\longmapsto\{6\}.
\]

This remains true whether "missing" means absent from the source `S` or
absent from the image `T`.  Thus the complete blocker-local Hall graph has
matching size `1<2`.  The reserve consumed at the hard event `74` is the
unrelated healed splitless root `18`; no blocker descent from `74` reaches
it.  The same shell and reachability data hold for the canonical grounded
source `G=Cl{2,3}=F(G)`, so the extra source point `21` is not load-bearing.

This is not a counterexample to the C23 image inequality: equality holds at
`74`.  It is a precise obstruction to discharging a least-counterexample
step by recursively applying the induction hypothesis to the new hard
root's factor blockers.  A successful induction must carry a nonlocal bank
or flow invariant that imports credit from unrelated components.

## 1. First-failure normalization

Put

\[
 D_T(X)=Q_T(X)-H_T(X).
\]

Every `Q` event has coordinate `2m-1`, hence is odd.  Every hard event is
even.  Therefore, if `X` is the least cutoff with `D_T(X)<0`, then:

1. `X=h` is an even hard-shaped hole of `T`;
2. no `Q` event occurs at `h`; and
3. `D_T(h)=D_T(h-1)-1`.

Minimality and integrality force

\[
 D_T(h-1)=0,\qquad D_T(h)=-1.                 \tag{1}
\]

Using the C78 shell identity, (1) says that the healed-nonhard and
unhealed-hard shell counts are equal at `h-1`, and the new root `h` is one
additional unhealed hard chain.  Thus ordinary induction on the cutoff
requires the strict reserve statement

\[
 h\notin T,\ h\text{ hard-shaped}
 \quad\Longrightarrow\quad D_T(h-1)\ge1.       \tag{2}
\]

The weak induction hypothesis `D_T(h-1)>=0` is one unit short.  The issue is
to prove (2), not to identify the parity of the first event.

Moreover, (2) is equivalent to the desired all-cutoff inequality for a
fixed `T`.  The forward implication follows from
`D_T(h)=D_T(h-1)-1>=0`.  Conversely, sweep the event coordinates in order:
an odd boundary can only increase `D_T`, a hard member changes nothing, and
(2) prevents a hard hole from making `D_T` negative.  Thus presenting (2)
without an independent reserve construction merely renames the missing
induction step.

## 2. Exact image

Every output `ab-1` from distinct allowed factors is larger than both
factors.  Consequently the prefix of the infinite closure
`S=Cl{2,3,21}` through `74` is determined without any truncation error:

```text
S <= 74 =
2,3,5,9,14,17,21,26,27,33,41,44,50,51,53,62,65,69.
```

The complete products of two distinct members with product at most `75`
are exhausted by

```text
2*(3,5,9,14,17,21,26,27,33),
3*(5,9,14,17,21),
5*(9,14).
```

Their outputs are all in the displayed prefix, proving forward closure.
Taking all supported outputs gives

```text
T=F(S) <= 74 =
2,3,5,9,14,17,26,27,33,41,44,50,51,53,62,65,69.
```

The sole unsupported source member is `21`: its only admissible pair is
`22=2*11`, and `11` is absent from `S`.  Every other listed nonseed has a
displayed supporting product in `S`.

For a grounded-source red-team, delete the extra generator `21`.  Ascending
closure then gives

```text
G=Cl{2,3}=F(G) <= 74 =
2,3,5,9,14,17,26,27,33,41,44,50,51,53,65,69.
```

The optimizer image above differs only by `62=3*21-1`.  Removing `62`
changes neither event list, shell set, nor either complete blocker closure
below.  Thus the obstruction already occurs in the actual least closure.

Exact trial division gives

| cutoff | hard holes | boundary children | `Q-H` |
|---:|---|---|---:|
| `73` | `54` | `41,69` | `1` |
| `74` | `54,74` | `41,69` | `0` |

In root coordinates the two boundaries are

```text
6 -> 11 -> 21 -> 41,
18 -> 35 -> 69.
```

The roots `6` and `18` are splitless because `7` and `19` are prime.  Both
roots are absent from `T`, while the displayed chain tops are in `T`.
Hence the C78 shell sets are

```text
cutoff 73: unhealed hard {54};    healed nonhard {6,18};
cutoff 74: unhealed hard {54,74}; healed nonhard {6,18}.
```

This proves the shell identity directly at both sides of the tight step.

## 3. Complete blocker closure

For a missing even root `r`, inspect its seed-2 chain through `74` up to its
first member of `T`.  At every inspected value `n`, inspect every admissible
factorization `n+1=ab`.  For each endpoint absent from the chosen present
set (`S` or `T`), add its even seed root and repeat.  This is the transitive
closure of all factor descents available on every missing chain segment.

For `54`, the only hard factorization is

\[
 55=5\cdot11.
\]

The blocker `11` has root `6`; the missing root-`6` segment is
`6,11,21`, followed by `41 in T`.  Its only pairs use the same root.  Thus

\[
 \operatorname{Reach}(54)=\{54,6\}.             \tag{3}
\]

For `74`, the only admissible hard factorization is

\[
 75=5\cdot15.
\]

The blocker `15` has root `8`.  The missing root-`8` segment is
`8,15,29,57`; its non-seed pair `30=5*6` reaches root `6`.  Continuing the
root-`6` segment adds nothing.  Hence

\[
 \operatorname{Reach}(74)=\{74,8,6\}.           \tag{4}
\]

Equations (3)-(4) are unchanged when all image holes, rather than only
source blockers, are admitted at each descent.  Intersecting with the
healed nonhard set `{6,18}` gives the exact Hall graph

\[
 \{54,74\}\longrightarrow\{6\}.                 \tag{5}
\]

Its maximum matching has size one.  The second shell credit is root `18`,
whose chain heals at `69=5*14-1`; neither `18` nor its chain occurs in the
complete traces (3)-(4).  This proves the claimed obstruction.

## 4. Parity and distinct-factor audit

The two possible hard-event parities both occur in the witness.

* `54=0 mod 6`; its odd successor is not divisible by `3`, and its unique
  admissible pair is `(5,11)`.
* `74=2 mod 6`; although `75=3*25`, the cofactor `25=1 mod 3` is forbidden.
  Its unique admissible pair is the distinct allowed pair `(5,15)`.

For any hard even value, the successor is odd, so every admissible factor
is odd.  A usable distinct pair `(3,m)` would make the root seed-3-easy,
not hard.  The exceptional successor `9=3*3` does not create a pair:
equal factors are excluded, so `8` is splitless rather than hard.  Likewise
`2*2-1=3` is not a seed-2 closure edge under distinct-value semantics;
`3` is present because it is an explicit seed.  Every later seed-2 edge
uses `(2,m)` with `m>2` and therefore has distinct factors.

These cases exhaust the parity and equality exceptions used in (1)-(5).

## Reproduction

```powershell
python -m py_compile problems/424/compute/wave5/C80_minimal_counterexample.py

python -O problems/424/compute/wave5/C80_minimal_counterexample.py `
  --output problems/424/compute/wave5/C80_minimal_counterexample_74.json
```

The verifier uses integer trial division and explicit exceptions, so its
checks remain active under `python -O`.

```text
035DD201ACD63F082F9CC17BB7257743072EC14BE4CB1C26C8C7914F22406C53  C80_minimal_counterexample.py
69A1DBBD4274B3D9C6D6AED84B2ADC83074A011DC299A8EF3B7FE3E89A321C38  C80_minimal_counterexample_74.json
69A1DBBD4274B3D9C6D6AED84B2ADC83074A011DC299A8EF3B7FE3E89A321C38  C80_minimal_counterexample_74_replay.json
```
