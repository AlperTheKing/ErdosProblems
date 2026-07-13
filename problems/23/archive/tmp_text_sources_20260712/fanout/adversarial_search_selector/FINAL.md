Unable to execute the requested exact global search.

Exact blockers:

- R29 provides aggregate claims only; no labelled 2943 graph constructor, 676×680 row menus, initial selector tuple, or executable HitNeed/Hall certificate.
- Searches found no 2943 constructor elsewhere in the workspace.
- Writes under `tmp/fanout/adversarial_search_selector/` fail because the filesystem sandbox rejects split writable roots. No files were modified.
- Therefore no global-minimizer claim, witness, or falsifier is asserted.

Required reconstruction payload: canonical `B` and `M`, ordered row menus, initial choice, and exact HitNeed/Hall definitions. The finite optimization is:
`min_r [2 Σ_(x,y active(r)) max(0,n_r(x,y)-1) + HitNeed(r)]`,
checking Hall for every tied minimizer. A correct compressed DP must retain active-component connectivity, endpoint-pair closure flags, truncated pair multiplicities—including diagonals—and Hall-distinct source signatures.

Input SHA-256 hashes:

- Onboarding: `E3012793ACCDE4E8F8FA3ED3E514A794A7D006A07E4BDC23E4239D14C9D61AD0`
- Claude handoff: `B533191BAF54A2E3D53CE05E1F46269B78E6EEDBA90F08CB9B80B7FEAB6E9126`
- R29 wall: `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`
- Existing exact census gate: `C19C4BBEFE518133F834599672F54F4889222C4D234FF08ABB0424A8D49286F4`