# R29 gate synthesis

## Canonical reconstructed instance

- Canonical payload SHA256: `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`.
- Counts: `N=2943`, `|E|=8422`, `|B|=7039`, `|M|=1383`.
- Triangle-free and blue-connected; independently replayed by d01 and d02.
- MaxCut is exactly `7039`. The disjoint upper-bound classes are
  `4110+2704+12+207+6`; d03 enumerated all `16*27^2=11664` traffic quotient
  cases and checked an attaining 2943-bit cut.
- Every bad edge has blue distance four, hence `Gamma=1383*25=34575` and this
  maximum cut is Gamma-minimal.
- Exact row histogram: `707` rigid atoms with one shortest row and `676`
  selector atoms with `680` shortest rows. Total materialized shortest rows:
  `460387`. d04 independently enumerated all paths.

The original advertised artifact prefix `00186166...` is absent, so bitwise
identity to that historical artifact is not provable. The gate applies to the
deterministic reconstruction above, which matches every advertised invariant.

## Baseline tuple and Hall gate

- Scoped score: `30811 = 30808` collision halves `+ 3` HitNeed.
- Hub contribution: `3*(6650+1)=19953`; leaf contribution: `52*200=10400`;
  rigid circuit contribution: `458`.
- Scoped owner shore `W={0,1,2}`: demand `19953`, reach
  `17325+2600=19925`, exact min-cut gap `28`.
- d05 checked all eight owner shores and emitted an integral value-19925 flow.

## Hamming-one gate

- Exactly `676*679=459004` nontrivial replacements were full-recomputed.
- Minimum neighbor score: `30813`, so every move is at least `+2`.
- Minimum multiplicity: `1352`.
- Sharp witness:
  `P=[735,732,59,56,2760]`,
  `Q=[735,55,57,56,2760]`, score delta `+2`.
- Exact delta histogram from d07:
  `{2:1352,4:676,6:227812,8:676,14:227136,16:676,24:676}`.
- Universal checks: `Q\\P` is nonempty, each new vertex had baseline row
  multiplicity one, and every positive-score owner persists.
- Falsifier to whole-active-set persistence: the sharp witness removes
  vertices `{57,59,732}` from active scope.
- This also falsifies the lead fixed-scope multiplicity `676`; d06 and d07
  independently obtain `1352` by rebuilding active components for every move.

Therefore the claimed strict Hamming-one local minimum is gated on the
reconstructed instance, and `RealHallFailureHasScopedScoreOneRowDescent` is
false as stated.

## Global selector landscape

- `30811` is not global. The exact global minimum is `23115`, attained on the
  all-anchor face (`676` selector rows changed), with delta `-7696`.
- Minimum decomposition: hubs `19953` + rigid circuit `458` + active anchor
  `2704` = `23115` (`23108` collision + `7` HitNeed).
- Every selector family has `676` anchor rows and `4` local rows.
- If side `s` uses `L_s` local rows, at least `ceil(L_s/27)` D leaves are
  active. The exact lower bound over all `339^2=114921` count cells has unique
  minimizing count vector `(L_L,L_R)=(0,0)`; the next bound is `23203`.
- On each side, collision-minimal anchor supports are the two perfect
  matchings of the 338-cycle. Modulo atom labels there are four phase pairs.
  Since the 338 support edges may be assigned bijectively to the 338 labeled
  selector atoms, the labeled row-tuple multiplicity is `4*(338!)^2`.
- No selector trade deactivates hubs `0,1,2`: the six cable edges and rigid
  circuit keep them in the permanent active component.
- At every minimum, all 52 traffic leaves and all 2704 lock-arm descendants
  leave active scope. The selector vertices were already outside active scope.

Thus the global-minimizer route survives this cage: a coordinated trade
descends, although no one-row trade does.

## Primary hashes

- Lead result JSON: `0fa2eb08696372b25b05429a692db9fa5ecabc173ce25dc66f59f68d3bf214f5`.
- Lead constructor: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`.
- d03 MaxCut certificate: `6870d083833f1ef354572636d9d9335c202b77e9ff150f8b4b64b5389122035d`.
- d04 row/Gamma audit: `0476ef826d0c54dc3864242503fccad7441d44da6073e352bac2aaf6dcf0cb56`.
- d05 Hall cut certificate: `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`.
- d06 result file: `56616e845fbe2a7ad60525aa9fe375c7c2595ead67181369096c259c85929e1c`;
  result-preimage SHA256: `b71bdde11707600150f6f111c2644efa3fcfc687349b11a9f891c2a2ea6f521f`.
- d07 aggregate result: `5c287b24ac84fd7a059af6e655792e1e5de5456d94ff3697f166f3058cf16998`.
- d09 global certificate: `5f61d53af12b3abb47e31841c31ee70a563e09c16fec32ef744c1e07c0f5b63f`;
  best tuple SHA256: `93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901`.

## Proof gaps

- Historical provenance: no artifact matching `00186166...` is present.
- No Lean certificate was produced; the finite gates are exact Python/integer
  verifiers only.
- The general theorem that no Hall-failing tuple is a global scoped-score
  minimizer remains open. This lane settles only the reconstructed R29 cage.
- d10 requested a formalized structural reduction for the global lower bound;
  the lead and d09 verifiers implement it exactly, but it is not yet a theorem
  in the production Lean modules.
