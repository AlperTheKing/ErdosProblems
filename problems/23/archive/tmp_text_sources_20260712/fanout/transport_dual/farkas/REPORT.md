# Finite Farkas dual for component-aware coordinate transport

Fix parameters and set `Z=CoordinateNewDemandBundle`, `Q=OneCoordinateAlternative`, `D=OutsideShoreDemand`, `S=ShoreSource`, `T=(Q×D)⊕(Q×S)`. All `Q×D` targets are allowed. A `(q,s)` target is allowed from `z` iff `ComponentTransportSourceEligible ... z s`; Lean does not require `q=z.1`.

Primal: rational `x[z,t]≥0` on allowed pairs, `Σ_t x[z,t]=1` for every `z`, and `Σ_z x[z,t]≤1` for every `t`. By bipartite max-flow integrality this is feasible iff the required component-aware injection exists.

Exact Farkas obstruction: rational `alpha[z]` and `beta[t]≥0` with `alpha[z]≤beta[t]` on every allowed edge and `Σalpha>Σbeta`. This follows after adding target slacks, with equation multipliers `-alpha,beta`. Thresholding is precisely Hall: some nonempty `X⊆Z` has `|N(X)|<|X|`; conversely `alpha=1_X,beta=1_N(X)` is integral.

The sharp graph lemma (CA-Hall) is

`|X|≤|Q||D|+Σ_q |{s∈S:∃z∈X, ComponentTransportSourceEligible ... z s}|`

for every nonempty `X⊆Z`. It is equivalent to transport because `Q×D` is universal. The proof gap is deriving it from triangle-free/max-cut structure, changed-row locality, persistent-component embedding, and inclusion-minimal deficient shores. Collision variation and HitNeed variation `≤0` act only after transport exists.

Smallest falsifiers: target cardinality alone fails on `2×2` with neighborhoods `{0},{0}`. Whole-left Hall alone fails on `3×3` with `{0},{0},{1,2}`; the first two are deficient. These are abstract, not asserted graph-realizable.

`verify_farkas.py` uses `Fraction` and exhaustively checks all 682 relations through `3×3`. No floats, native_decide, or sorry.

SHA256: goal `CD536B9EDF3A4B1BA9E0E79754C0DAA780C68B98F5F4C06DA84E279B6D2C20F2`; onboarding `E3012793ACCDE4E8F8FA3ED3E514A794A7D006A07E4BDC23E4239D14C9D61AD0`; Claude file `B533191BAF54A2E3D53CE05E1F46269B78E6EEDBA90F08CB9B80B7FEAB6E9126`; R29 `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`; Lean `2821EB83265C85DC41F42EDD2B31DAE11FE60256B257E6C129BBB6E882AB5706`.

Proof gap: CA-Hall remains unproved. No shared/production file edited.

