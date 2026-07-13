# R32 Pattern-5 static ownership promotion

## Production result

`problems/23/lean/Erdos23Delta0/Gamma/Pattern5StaticOwnership.lean`
promotes the assignment-level construction from the temporary static-token
module.  It exports:

- `BaseKeyComponentCoherent` on a selected half-key injection;
- `sourceComponentOf` and `sourceComponentOf_assigned`;
- `exists_sourceComponent_iff_baseKeyComponentCoherent`;
- `CoherentMicroAssignment.toResidualData` at the exact `Fin 25` scale.

The module deliberately contains no graph-local relation-level uniqueness
predicate or theorem.  It assumes coherence of the chosen global matching.
It does not claim the Erdős #23 main theorem or construct a full-bank flow.

## Lean verification

Pinned toolchain: Lean `4.27.0`.

`production_build.log` records a successful kernel build (`rc=0`).
`axiom_probe.log` records a successful probe of four declarations.  Each
depends only on:

```text
propext, Classical.choice, Quot.sound
```

No `sorry`, `admit`, `native_decide`, or `sorryAx` is used.

## External doubled-cage evidence

The relation-level claim remains false outside theorem data.
`replay_doubled_cage.py` pins and replays the integer-only checker at source
SHA-256
`0b73b97e75a2440e28833883da9f650bfd36223bdb9211f84a70e343d5cd1237`.
It writes `doubled_cage_result.json`, SHA-256
`be92dde1a764f4d8a9df2a4d00627c982d6dbbc9f152aa57ef726d4f73a61c2e`.

The replay certifies a triangle-free, blue-connected doubled cage with:

```text
n = 5886
edges = 16845
blue = 14079
bad = 2766
MaxCut upper = attaining cut = 14079
bad blue-distance histogram = {4: 2766}
Gamma = 69150
source base key = (3, 56)
eligible destination roots = {0, 2943}
```

Thus the same base key is locally Pattern-5 eligible in two destination
components.  Full half-key injectivity does not imply base-key component
coherence; the selected global matching must impose it.

## Reproduction

```powershell
python tmp/fanout/r32_static_ownership/replay_doubled_cage.py
```

The Lean logs were produced with the complete hardlinked Erdos olean closure
under `tmp/fanout/r32_static_ownership/olean` and `LEAN_PATH` set to that
directory.
