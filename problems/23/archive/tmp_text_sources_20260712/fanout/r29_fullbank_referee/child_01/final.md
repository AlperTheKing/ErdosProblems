Unable to produce the requested artifacts for two independent reasons:

1. `WALL_ATTACK_R29_GPTPRO56.md` contains only aggregate claims. It omits vertex/edge formulas, cut assignments, bad-edge definitions, row contents, anchor choices, and canonical serialization. Thus the exact graph and payload hash are not reconstructible from that file alone.

2. Writes to `tmp/fanout/r29_fullbank_referee/child_01/` were denied by the workspace patch mechanism, including a one-line test file. No files were changed.

Recoverable facts include:

- `N = 2943`
- `|E| = 8422`
- `|B| = 7039`
- Assuming `E = B ⊔ M`, `|M| = 1383`
- Rigid families: `676 + 28 + 3 = 707`
- Selector families: 676, each with 680 rows
- Selector space: `680^676`
- Hall defect: `19953 − 19925 = 28`

An exact constructor or canonical SHA256 beyond these aggregates would require inventing data absent from the authorized source.