# Lead result: global scoped minimum

## Decisive R29 update

After this file's initial build, the dedicated R29 lane landed an executable
2943 reconstruction plus independent global-minimum and Hall certificates.
Their all-anchor tuple has globally minimum scoped score `23115` and the owner
shore `{0,1,2}` still has demand `19953`, neighborhood `19925`, and defect
`28`.  `verify_r29_global_min_hall_falsifier.py` cross-checks that the two
certificates use the same all-anchor tuple.  Therefore
`AllGlobalScopedMinimaHall`, its equivalent unbounded-descent form, and PHT
are false.  See `../SYNTHESIS.md` for the final result.

## Exact theorem chain

`GlobalScopedMinimum.lean` proves, without `sorry`, `admit`, or
`native_decide`, the equivalence

`HallFailureHasGlobalScopedScoreDescent <-> AllGlobalScopedMinimaHall`.

The forward implication is one finite-order contradiction: a lower tuple
contradicts global minimality.  The reverse implication is exact as well: if
no lower tuple exists, `Nat.le_of_not_gt` makes the failing tuple a global
minimum, contradicting Hall at every global minimum.

Together with the existing `matching_nonempty_iff_hall` and
`scopedCanonicalChoice_optimal`, the shortest surviving chain is:

1. Scoped Hall failure at `omega`.
2. **OPEN G:** produce any row tuple `eta` with
   `scopedObligationScore eta < scopedObligationScore omega`; no Hamming
   bound is allowed.
3. At a global minimizer, step 2 contradicts minimality.
4. `matching_nonempty_iff_hall` converts the resulting matching to scoped
   Hall.

The Lean build printed only `propext`, `Classical.choice`, and `Quot.sound`
for all three wrapper theorems.

## Exact evidence

Repository protocol records the active-scoped exhaustive gates:

- N <= 11: 1,085,580 tuples, 308,912 scoped minima, zero Hall-failing
  minima (`PROGRESS_CODEX.md`, 2026-07-11T06:27:53Z).
- N = 12: 39,142,819 tuples, 4,572,937 scoped minima, zero Hall-failing
  minima (`PROGRESS_CODEX.md`, 2026-07-11T07:41:36Z).
- Heavy N12 coordinate gate: 4,801,067 tuples; all component transports
  pass.  The user additionally supplied that every failure has negative
  summed one-coordinate variation.

These computations are integer-exact.  They support OPEN G but do not prove
it.

## Multi-row route using persistence

The new compiled local facts are
`activeDegree_new_le_old_of_not_touchesChangedRows` and
`hitNeedUnits_new_le_old_of_not_touchesChangedRows` in
`ActiveScopedCoordinateTransport.lean`.  They support this amortized target:

> From a minimal deficient owner shore at a global minimizer, choose a finite
> coordinated row trade.  While its active component avoids each changed-row
> interface, transport persistent demand forward and use the two monotonicity
> lemmas.  At the first component split, charge the terminal demand drop
> against all collision increases accumulated along the path.  The telescoped
> scoped score must be negative.

Exact missing lemmas:

- **G1, coherent realization:** component-wise coordinate injections compose
  to one simultaneous row tuple; separate best alternatives can conflict.
- **G2, deficient-shore persistence:** before the terminal split, either the
  same owner shore remains deficient or a strictly smaller deficient shore is
  exposed.
- **G3, terminal amortization:** the component-splitting demand drop exceeds
  cumulative diagonal-collision creation.  R29 shows every individual move
  may cost at least two, so this must be a whole-trade inequality.

No descendant or lead proof closes G1-G3.

## Mandatory 2943 gate

The later R29 artifacts replace the initial unavailable status.  The old
score-30811 tuple is a strict Hamming-one local minimum, but a 676-row
all-anchor trade reaches the certified global score 23115.  That global tuple
retains the exact Hall defect 28, so it is the required falsifier.

## Hashes

- `GlobalScopedMinimum.lean`:
  `5A6B8B41407061CAC35FA56A8A319A55C84DE670A04AA7B1F2E419FAD19CF03F`
- current `ActiveScopedMinimumExchange.lean`:
  `8F39D8443DDC26D38BB76DA10B9BED223F5F141546E6194C5177779F03174BC8`
- current `ActiveScopedCoordinateTransport.lean`:
  `6B10458BEDD26B4D460FDD4AD034D55CB6B1DEE16A2691F22460E562941DC272`
- `_codex_scoped_variation_anatomy.py`:
  `A2A10E6241CB7D5254DB8530C44D510C3E36779876BA7B219BDCE49E5FA3ED62`
- `WALL_ATTACK_R29_GPTPRO56.md`:
  `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`
