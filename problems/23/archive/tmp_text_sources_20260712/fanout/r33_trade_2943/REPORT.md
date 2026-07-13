# R33 2943 collision-only selector trade

## Verdict

The requested literal `28 -> 0` collision-only label is false.  The exact
concrete trade is:

| endpoint | collision demand | maximum coherent matching | defect |
|---|---:|---:|---:|
| `baselineLocal` | 30808 | 30783 | 25 |
| `metadataAnchor` | 23108 | 23108 | 0 |

The old value 28 is the three-hub mixed-demand gap
`19950 collision + 3 HitNeed - 19925 reach`.  HitNeed is excluded from the
collision relation requested here, so the exact collision defect is 25.

The coarse R33 labels also hide choices.  `baselineLocal` is the R29
reconstruction's displayed local row in each of 676 selector families.
`metadataAnchor` is the specific `selectorMeta[j]["anchorRow"]` in each
family.  Each family actually has 4 local and 676 anchor rows.

## Tuple IDs

Selector choice IDs are zero-based indices in each complete lexicographically
sorted 680-row shortest-path family.  The 676 IDs for each endpoint are in
`certificate.json`.

- baseline full-row SHA256 / tuple ID payload:
  `b3e6eff382869c067c297ab2d9ab20ff85fee6dca221c7bbda8b6a9face0fa1a`
- anchor full-row SHA256 / tuple ID payload:
  `ab37d295364a110795388fbb8bb695f5ae849514348ff84bc29edf8ca57493f9`
- complete selector-family catalog SHA256:
  `3afd226b4057b978b31766289ea2d1a1af74da8f03d696dcf2d0d235d15b7467`
- structural-gate incidence SHA256:
  `7f3c69376e074adefe505f709643bdf14a9a5c5b18e9816d8b88e24d7b59f087`
- R29 lead canonical graph/row SHA256:
  `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`

Exactly the global row interval `[676,1352)` changes, hence 676 rows.

## Exact certificate

The relation is the deduplicated union of P1 same-first, P3 row-companion,
strict P4, and static P5.  P2 and common-blue are absent.  Scoped-reserved
half-zero keys have capacity zero.  Every collision obligation and every
physical ordered FreeHalf `(x,y,half)` has capacity one.

`certificate.json` contains all 53891 assigned obligation/source records,
the 25 explicit baseline unmatched obligations, destination component roots,
eligible-pattern masks, tuple IDs, demand vectors, Hall data, and assertions.

Baseline maximality has both sides:

- a feasible exclusive, base-component-coherent assignment of size 30783;
- the Hall shore `{0,1,2}` has demand 19950 and reach 19925, so every matching
  has size at most `30808 - 25 = 30783`.

Anchor maximality follows from a feasible assignment of size 23108, equal to
the complete collision demand.  Although the full static-P5 relation is much
larger, the displayed assignment was solved using full P1/P3/strict-P4 plus
only the historical 28 keys `(3,56+2*j,h)`, `0 <= j < 14`, `h in {0,1}`.
Exactly those 28 keys are P5-only in the assignment.

- baseline assignment SHA256:
  `ec66dbcc0459aa3367a26259d3e858035208081f6e31b7aa86b985f6c1ff6757`
- baseline unmatched-obligation SHA256:
  `b441901f4a2310adb5f04e737ec6ea6aba3be467eed9eecfc60f6a9ded671a6b`
- anchor assignment SHA256:
  `34f42e6a86cd5b0d5f835c0257147ce8bedd6410f4c40ed4532e2532b076642e`
- anchor P5-only key-set SHA256:
  `d8dd097b5251c089068f75c3c93894ad34e401f4db673dc69372e6b88868b718`

All assigned physical keys are exclusive.  Both assignments satisfy
`BaseKeyComponentCoherent`: the two halves of every used ordered base `(x,y)`
are assigned only inside one active destination component.

## HitNeed typing

HitNeed is metadata for typed bank sinks and is never added to collision
demand.  The baseline has 3 such sinks and its Door-only diagnostic matches
3/3.  The anchor has 7 sinks and its Door-only diagnostic matches 6/7.  The
Door diagnostic is outside this collision certificate; no collision defect or
maximum uses it, and no claim is made here that Doors alone pay every bank
sink.

## Commands

Run from `E:\Projects\ErdosProblems`:

```powershell
python tmp/fanout/r33_trade_2943/build_certificate.py
python tmp/fanout/r33_trade_2943/replay_certificate.py
python problems/23/writeup/_claude_r29_2943_structural_gate.py
python problems/23/writeup/_claude_r29_pattern5_gate.py
```

Observed results: build assertions passed; replay status was `PASS`; the
structural gate passed S1-S6; and the Pattern-5 gate validated the 28-key
historical witness.  `replay_output.json`, `structural_gate.log`, and
`pattern5_gate.log` contain the outputs.

An independently produced concurrent replay was also checked without editing
its files:

```powershell
python tmp/fanout/r33_trade_2943/replay.py --verify tmp/fanout/r33_trade_2943/certificate_replay.json
```

It independently returns 30808/30783/25 and 23108/23108/0, with identical
full-row hashes and all 676 selector IDs.  Its different assignment digest is
expected because maximum assignments are not unique.

## SHA256

```text
17e5bad02dc1672b55ca4a58de14b37862ce096086746fb110f488fdc952294e  certificate.json
44a3bcef983716e1161b60381bdc2d2a34e7eea7f364b06ace8760c2e6265f91  certificate_core.py
77c69050ea7082f98a27e8644375de7774dc3dd76471618679af738b5464641b  build_certificate.py
a6381a34326863df9af7860a275bf5a60fe1e3fac99b3e9bef97bee64d0dee18  replay_certificate.py
774e9868a7067d31429cd1523484d5f53d1217595672c59551b9830544067bb5  replay_output.json
d27bbfd0ba7331e53274d400b96c98856b6b898a1611adad9204230a65c9c26e  structural_gate.log
c559721b67cd48a395e671870dfda0cd82bb57c39469e26fb0197e3d3ab176f9  pattern5_gate.log
```

Concurrent files, verified but not modified by this lane:

```text
3c1413a766d2c71ce2b5b3ffd27359e3ada87c55ba63604ccb8ac94cc84a93df  replay.py
75a0b84027f1d92d6d1f3751e2c1a4b566d9f40a25ef1cb3d0d97a58cba88488  certificate_replay.json
```
