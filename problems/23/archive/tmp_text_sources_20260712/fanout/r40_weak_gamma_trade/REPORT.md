# R40 weak-pair Gamma/row-trade audit

## Verdict

The proposed Gamma-minimality proof does not go through. There are two exact
obstructions.

1. A weak switch with `sigma=1` is not another maximum cut, so Gamma
   minimality is inapplicable. A switch with `sigma=0` is another maximum cut,
   but it changes the bad-edge set and therefore changes the row-choice domain;
   the Gamma inequality contains no comparison of collision defects.
2. In the current Lean production API, `GammaMinimalConnected` is vacuous:
   its `gammaOfCut` field is an arbitrary function. The compiled audit
   `GammaMinimalConnectedAudit.lean` inhabits it for every graph and cut with
   the constant-zero function.

No exact real positive-defect weak-pair counterexample was found. The exact
fixtures remain separated: the real weak cage has defect zero at both row
tuples, while the real positive-defect cage has no weak probe. Thus this report
rules out the named proof route; it does not refute the stronger semantic
statement for genuine graph-theoretic Gamma.

## Exact boundary calculation

For a vertex switch set `S`, write `c^S` for the flipped cut. Every boundary
edge swaps blue/bad status and every other edge keeps its status. Hence

```text
badCount(c^S) = badCount(c) - dM_c(S) + dB_c(S)
              = badCount(c) + sigma_c(S),                 (1)

blueCount(c^S) = blueCount(c) - sigma_c(S).                (2)
```

These are exactly the identities documented and proved around
`CertGraph.lean:366-368` and used by `IsMaxCut`.

If `sigma(S)=1`, equation (1) puts `c^S` one bad edge above the maximum cut.
The production Gamma hypothesis only compares valid, B-connected cuts having
the same bad count as `c`:

```text
GammaMinimalConnected.gamma_min:
  badCount G d = badCount G c -> ... -> gammaOfCut c <= gammaOfCut d.
```

Therefore it says nothing about a sigma-one weak probe.

If `sigma(S)=0`, the new cut is maximum, but its bad set is

```text
M(c^S) = (M(c) minus delta_M(S)) union delta_B(S).          (3)
```

For an attachment pair `S={x,y}` with common blue owner `v`, the two edges
`vx,vy` lie in `delta_B(S)` and become bad after the switch. Simultaneously,
`dM(S)=dB(S)` old bad boundary edges become blue. Thus the atoms indexing the
old row families are not the atoms indexing the new row families. A
`RowChoice bads(c)` cannot be changed in one coordinate to obtain a
`RowChoice bads(c^S)` without an additional atom/row transport theorem.

Even if such transport were supplied, Gamma minimality yields only the scalar
inequality `Gamma(c) <= Gamma(c^S)`. Collision defect depends on selected-row
co-occurrences, active support, reservations, and a maximum matching. None of
those terms occurs in (1)-(3) or in `GammaMinimalConnected.gamma_min`. Hence no
sign for `defect(omega')-defect(omega)` follows.

The suggested picture of rotating one unpaid cut edge around an odd cycle
therefore performs a cut change, not a shortest-row change in the fixed-cut
canonical tuple space.

## Lean-level obstruction

The production definition at `CertGraph.lean:2430-2435` is

```lean
structure GammaMinimalConnected (G : GraphData) (c : CutData) : Type where
  gammaOfCut : CutData -> Rat
  gamma_min : forall d, checkCut G d = true ->
    badCount G d = badCount G c -> BConnected G d ->
    gammaOfCut c <= gammaOfCut d
```

There is no field equating `gammaOfCut` with the graph-theoretic Gamma
functional. The existing module
`problems/23/lean/Erdos23Delta0/Gamma/GammaMinimalConnectedAudit.lean` gives

```lean
def trivialGammaMinimalConnected (G) (c) : GammaMinimalConnected G c where
  gammaOfCut := fun _ => 0
  gamma_min := by intros; norm_num

theorem gammaMinimalConnected_nonempty (G) (c) :
    Nonempty (GammaMinimalConnected G c)
```

and prints only standard axioms. Consequently no nontrivial row
reconfiguration theorem can use this carrier as its load-bearing hypothesis.
It must instead assume a semantic Gamma bridge that fixes `gammaOfCut`, plus a
separate theorem transporting bad atoms, shortest-row databases, and defect
matchings across a zero-sigma cut switch.

Audit file SHA256:

```text
03140109BB4F8FD1A6B4DB9CB20B55B433231927F015540F84B54D688AFADB10
```

## Exact fixture separation

### Weak real cage

The 20-vertex R36 cage has a lex-first weak probe

```text
(owner,x,y) = (7,0,5), dB=3, dM=2, sigma=1.
```

Its only non-singleton family has rows

```text
(0,2,3,4,1), (0,7,10,15,1).
```

Exact replay gives collision demand and defect `(0,0)` for each of the two row
choices. Thus the available alternative tuple does not strictly lower defect;
it preserves zero. This is not a positive-defect counterexample.

### Positive-defect real cage

The 24-vertex fixture has collision-only profile

```text
demand=240, matched=172, defect=68,
first one-row trade: 68 -> 51.
```

Its complete attachment classification has `0` weak probes, `0` detour probes,
and `153` probes with `sigma>=2`. It therefore does not test the weak-pair
implication.

### R29 local-minimum cage

The exact 2,943-vertex Gamma-minimal R29 cage has positive four-pattern owner
defect `28`, invariant under its selector choices, and no lowering one-row
selector move at the baseline. However, direct enumeration of all `5,523`
active-edge/support-edge probes found no sigma-zero or sigma-one probe; the
minimum sigma is `3`. It is not the requested counterexample.

## Consequence

A viable lemma must not say that Gamma minimality itself forces a row trade.
The minimum additional surface is:

```text
sigma(S)=0
+ a semantic graph-theoretic Gamma functional
+ a checked transport from bads(c) and rows(c) to bads(c^S) and rows(c^S)
+ an explicit matching map proving defect(new) < defect(old).
```

The sigma-one case needs a different mechanism because it leaves the
maximum-cut class. For the fixed-cut row space, the still-honest frontier is a
direct alternating-row/matching augmentation theorem; calling that theorem a
consequence of Gamma minimality would be circular unless the three transport
bullets above are independently proved.

## Replay

```powershell
python tmp/fanout/r36_freepair_proof/verify_counterexample.py
python tmp/fanout/r39_weak_free_switch/check_cage.py
python tmp/fanout/r39_weak_free_comp/verify_boundary.py
```

All three commands return exit code zero. The final command reports the exact
fixture split `CAGE20 defect=0, weak=1` and `CAGE24 defect=68, weak=0`.
