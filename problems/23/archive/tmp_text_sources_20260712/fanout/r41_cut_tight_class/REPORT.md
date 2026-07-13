# R41 cut-tight attachment class and monotone-support audit

## Verdict

The strengthened R41 support statement is proved exactly.  A genuine directed
two-edge detour never decreases selected support.  Equality holds exactly when
both removed middle edges have one selected-row occurrence; in that case the
target state has four new ordered zero-pairs, hence eight raw `FreeHalf` keys.
Consequently every directed neutral cycle is support-constant edge by edge and
is fully unsaturated.  The multiplicity-saturated R38 rotor is impossible.

This does **not** yet prove the larger forcing statement in the prompt, and no
real positive-defect counterexample was found.  The exact surviving obstruction
is a source-swap rotor: on every support-constant transition, all newly created
compatible keys are consumed (or component/reservation blocked) by the target
optimal matching.  Neither bad-incidence equality nor complete anchored rows
excludes that matching permutation.  Claiming a defect-lowering simultaneous
trade at this point would assume the remaining expansion theorem.

No `GammaMinimalConnected` hypothesis or `gammaOfCut` field is used below.

## 1. The entire singleton-tight class

Fix an active owner `v`.  Let `A` be its active blue neighbours and `S` its
selected-support blue neighbours.  For `z` in either class put

```text
a(z) = sigma({z}) = dB({z}) - dM({z}).
```

Maximum-cutness gives `a(z)>=0`.  Triangle-freeness makes `N_B(v)` independent,
so for every `x in A`, `y in S`,

```text
sigma({x,y}) = a(x)+a(y).                                  (1)
```

If every probe is weak, its integral surplus is below two.  If both classes
contained a positive singleton, (1) would give a cross-pair surplus at least
two.  Hence

```text
(forall x in A, a(x)=0) or (forall y in S, a(y)=0).         (2)
```

This is `WeakProbeClassTightness.one_class_zero_of_pair_sum_lt_two`.
For the zero class `Z`, the vertices are pairwise nonadjacent, so boundary
incidences add without interaction:

```text
dB(Z) = sum_{z in Z} dB({z}),
dM(Z) = sum_{z in Z} dM({z}),
dB(Z)-dM(Z) = sum_{z in Z} a(z) = 0.                       (3)
```

Thus flipping the entire class is an honest maximum-cut-preserving switch.
Equation (3), however, is only an equality of bad and blue boundary counts.  It
does not pair an old bad carrier with a replacement row for the same anchored
bad atom.

## 2. Exact support identity for a detour

Let the selected row of atom `f` be

```text
Q  = (a,x,m,y,b)
```

and let completeness supply the genuine replacement

```text
Q' = (a,x,v,y,b).
```

Write `S_omega` for selected support and `r_omega(e)` for the number of selected
rows using blue edge `e`.  Assume the entering edges `xv,vy` are active, hence
absent from `S_omega`.  Only four row edges change.  Put

```text
D = {xm : r_omega(xm)=1} union {my : r_omega(my)=1}.
```

Directly from the union defining selected support,

```text
S_omega' = (S_omega minus D) union {xv,vy}.                (4)
```

The two entering edges are distinct and absent from the old support, while
`D` has at most two elements.  Therefore

```text
|S_omega'| = |S_omega| + 2 - |D| >= |S_omega|.             (5)
```

Equality in (5) holds iff both old edges disappear, equivalently
`r_omega(xm)=r_omega(my)=1`.

Every checked shortest row is induced: if a blue edge joins two of its
vertices, they must be consecutive, since a nonconsecutive blue chord shortens
the four-edge endpoint path.  Hence, for blue pairs,

```text
r_omega(xm)=pairCount_omega(m,x),
r_omega(my)=pairCount_omega(m,y).                           (6)
```

Thus equality is equivalent to

```text
pairCount_omega(m,x)=pairCount_omega(m,y)=1.               (7)
```

After replacing `Q`, (7) gives

```text
pairCount_omega'(m,x)=pairCount_omega'(m,y)=0.              (8)
```

Both orientations of each pair in (8) are zero-pairs.  They create the four
ordered bases `(m,x),(x,m),(m,y),(y,m)`, each with its two half bits: eight raw
`FreeHalf` keys before reservation, relation, and component filtering.

## 3. Directed cycles

Along a directed cycle of genuine detours, (5) makes support cardinality
nondecreasing.  Returning to the initial row tuple forces every increment to
be zero.  Therefore every transition in the cycle satisfies (7)-(8).

In particular, a transition with either

```text
pairCount_omega(m,x)>=2 or pairCount_omega(m,y)>=2
```

strictly increases support and cannot lie on a directed cycle.  This excludes
the R38 multiplicity-saturated square rotor without any defect or Gamma
argument.

The only remaining cyclic shape is a source-swap rotor.  At every edge its
target matching must consume or block all newly eligible keys from (8); if one
compatible key is unused, the alternating matching gives augmentation, while
if a transition leaves the defect-minimal class it is the required checked
simultaneous trade.  Proving that one of these events occurs is exactly the
missing graph-to-matching expansion lemma.

## 4. Exact replay

`verify_support_dichotomy.py` exhausts all 144 row tuples of the 33-vertex R41
cage.  Among 224 directed middle replacements whose entering edges are absent
from old support, all 224 have strict support growth and there are zero
failures.  This is the saturated branch.

The same checker contains a 10-vertex triangle-free real fixture with complete
anchored rows

```text
Q  = (0,1,2,3,4),
Q' = (0,1,5,3,4),
P  = (6,5,7,8,9).
```

Its displayed cut has size 10 and exhaustive enumeration of all `2^10` cuts
gives exact maximum cut 10.  The entering edges `15,53` are old active edges,
both old pair counts are one, support size is `8 -> 8`, both target pair counts
are zero, and (4) holds exactly.

Replay:

```powershell
python tmp/fanout/r41_cut_tight_class/verify_support_dichotomy.py
```

Expected summary:

```text
verdict=PASS
checkedDirectedDetours=224
strictSupportGrowth=224
equalityFixture.pass=true
equalityFixture.oldSupport=8
equalityFixture.newSupport=8
equalityFixture.createdOrderedZeroPairs=4
equalityFixture.createdRawFreeHalfKeys=8
```

`support_dichotomy.json` SHA-256:

```text
DF90414C3A5F3D573C3D3201004E0D0889FDAD7A2B9B6285DAAB355B80424AE2
```
