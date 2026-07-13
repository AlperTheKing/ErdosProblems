Completed an exact bounded cage audit, but no lane files could be written because the workspace patch sandbox rejected both creation and modification inside the assigned directory.

Key findings:

- Private C5 seed with a unique row selects its attachment anchor but adds no off-support active edge. It therefore does not itself prevent active-component deactivation.
- If `k` private seed rows share anchor `a`, their exact active-scoped collision contribution is
  \[
  2(k-1)\mathbf 1_{\mathrm{ActiveOwner}(a)}.
  \]
- With prior selected load `5L(a)`, active degree `d_A(a)`, and `k` added seeds, the exact hit-need change is
  \[
  [d_A(a)-(N-5(L(a)+k))]_+
  -
  [d_A(a)-(N-5L(a))]_+.
  \]
  Thus extra seeds never reduce score; they cost collision score and may also exhaust vertex slack.
- Cross-cage blue edges can rigidify the active graph without immediate score while endpoint slack remains. Once slack is exhausted, each degree increment contributes hit-need. Consequently, rigidity is not automatically charged `2` per cage edge, but sufficiently dense rigidity necessarily becomes exploitable score.
- If a simultaneous trade removes the selected anchor or disconnects it from every component containing both endpoints of a selected bad atom, all collision and hit-need obligations owned there deactivate. Private C5 seeds do not block this because their four path edges are selected support and hence absent from `activeGraph`.

Exact computational range:

- All eight dihedral multiplicity types in `{1,2}^5`.
- Additional types `(1,2,3,2,1)`, `(2,2,3,2,2)`, `(2,3,2,3,2)`, and `(3,3,3,3,3)`.
- Orders `N=5..15`, up to 9 bad edges, 27 rows per bad edge, and 243 row literals.
- Every integer optimum was independently replayed.
- No Hall-failing optimum was found.
- Uniform results:
  - `t=1`: optimum `0`
  - `t=2`: optimum `36`
  - `t=3`: optimum `84`
- Representative nonuniform results:
  - `(1,2,1,2,2)`: `12`
  - `(1,2,2,2,2)`: `12`
  - `(2,2,3,2,2)`: `36`
  - `(2,3,2,3,2)`: `36`

These computations optimize the repository’s exact integer `obligationScore` surrogate. They do not prove the full active-scoped global-minimum claim; translating the optimizer to recompute `ActiveOwner` components and scoped hit-needs for every tuple remains the principal proof gap. The R29 2,943-vertex constructor is also absent, preventing direct cage-variant reconstruction.

Source SHA-256:

- R29 wall: `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`
- Active scoped definitions: `B916318F53D69B4D9ADFF2C4A79B23C139513640F16550DAEA092CE3A9E77982`
- C5 optimizer: `25707F776CFCA057EF17AAB5F54303F1C9D5A1EE796583FDDDB03BFFFC63CF68`
- Independent evaluator: `B49E9A2ADD265052605AC412449B9FB12B1B879CC67E254B68189DB7B831A737`
- Exact score implementation: `73697B12B1E22A30E320FB970415E79FA90D88D1A6DB27F42022CF9FFD9C6D83`

No production, coordination, progress, Lean, or other-lane files were modified.