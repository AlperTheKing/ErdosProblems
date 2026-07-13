Verdict: I could not falsify `rowVerts_nodup` itself. It excludes equal semantic rows, reversals, and endpoint duplicates. However, the repair is currently inert: repository-wide search found no use of `hdb.rowVerts_nodup` after its declaration.

Key findings:

- [MinimumDemandCollisionHall.lean:39](E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:39) requires:
  `((bads.get i).rows.map Row5.verts).Nodup`.
- [CertGraph.lean:168](E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/CertGraph.lean:168) ignores `Row5.badId`, but checks length 5, vertex `Nodup`, orientation `u→v`, four blue edges, and the closing bad edge.
- [ActiveScopedVariationReduction.lean:121](E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedVariationReduction.lean:121) defines alternatives by unequal row indices.
- [ActiveScopedCoordinateTransport.lean:24](E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedCoordinateTransport.lean:24) builds flow vertices from those index alternatives and repeatedly uses their `Fintype.card`.
- No existing lemma invokes `rowVerts_nodup` to prove that these indices denote distinct semantic vertex lists.

Exact pre-repair falsifier:

```text
bad owner: (0,4)
blue path: 0-1-2-3-4

R0 = { badId := 0, verts := [0,1,2,3,4] }
R1 = { badId := 1, verts := [0,1,2,3,4] }
```

Both records pass `checkRow5 G c 0 4`, because `badId` is ignored. With `omega=0`, index 1 is a `OneCoordinateAlternative`, although replacement changes no selected vertices, support, pair count, active graph, or score. The new `rowVerts_nodup` field correctly rejects this database.

Other cases:

- Reversed `[4,3,2,1,0]` fails the fixed head/last checks for owner `(0,4)`.
- Separate owners `(0,4)` and `(4,0)` violate `badKeys_nodup` after normalization.
- Repeated endpoints or internal vertices fail `checkRow5`’s vertex `Nodup`.
- Equal checked lists across distinct bad-edge families imply identical oriented endpoints and hence duplicate normalized bad keys.

Explicit proof gap: the transport chain needs and does not presently contain an injectivity bridge such as

```text
q ↦ ((bads.get i).rows.get q.1).verts
```

being injective on `OneCoordinateAlternative omega i`, derived from `hdb.rowVerts_nodup i`. Until that bridge is actually consumed, its flow cardinalities remain index cardinalities rather than proved semantic-row cardinalities.

Commands used:

```powershell
rg -n "rowVerts_nodup|\.rowVerts_nodup|hdb\.rowVerts|hdb" problems/23/lean/Erdos23Delta0/Gamma -g '*.lean'
rg -n "Fintype\.card \(OneCoordinateAlternative|OneCoordinateAlternative.*card" problems/23/lean/Erdos23Delta0/Gamma -g '*.lean'
```

Relevant SHA256 hashes:

```text
ea36fc95...3eb1a7  MinimumDemandCollisionHall.lean
93150a50...bbd31   CertGraph.lean
e4d216fc...67b11a  MinimumDemandRowSelection.lean
f3ffd8b2...f8a921  ActiveScopedVariationReduction.lean
6b10458b...dc272   ActiveScopedCoordinateTransport.lean
50deb444...8dc23   WALL_ATTACK_R25_GPTPRO56.md
80069ddf...ab05e   WALL_ATTACK_R26_GPTPRO56.md
45986dfd...10991   WALL_ATTACK_R27_GPTPRO56.md
819d6a3b...42b9    WALL_ATTACK_R28_GPTPRO56.md
fff06d97...1b04    WALL_ATTACK_R29_GPTPRO56.md
```

I attempted to write `REPORT.md` under the mandated recovery directory, but the workspace tool rejected creation there despite the directory existing. No prohibited file was modified.