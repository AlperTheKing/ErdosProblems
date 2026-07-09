# O14 Pair-Shard Hotspot Note (Codex, 2026-07-09)

This note records the O14 verifier stall diagnosis and the safe rerun path.
It is intentionally about future regeneration only: while Claude's wave is
active, do not mutate `problems/23/lean/Erdos23Delta0/O14/Generated`.

## Observed Hotspot

Claude's active wave (`tmp/claude_o14_wave_regate.py`, PID 74476) had all 32
child `lake` jobs elaborating `Chart014ConePairs000..031`.  The live
`pair_chunk = 16` generated pair shards are large:

- `Chart014ConePairs000.lean`: about 3564 KB / 2201 lines.
- Most early Chart014 pair shards: about 1.6-3.6 MB / about 2200 lines.

This is a Lean elaboration hotspot, not a certificate-data issue.

## Emitter Change

The future default was changed from `--pair-chunk 16` to `--pair-chunk 4` in:

- `_codex_o14_chunked_cone_to_lean_sharded.py`
- `_codex_o14_batch_emit_lean.py`

No live generated files were changed by this edit.

## Temp Verification

Chart000 temp regeneration with the new default:

```text
out: tmp/codex_o14_emit_probe_chart000_pair4
pair_chunk=4
pair_shards=182
first pair shards: about 337-391 KB / 568 lines
forbidden scan: no #print axioms, sorry, admit, native_decide, sorryAx
```

Chart014 temp regeneration from the v108 export:

```text
input: tmp/o14_exports_v108/codex_o14_chart014_chunked_cone_export.json
out: tmp/codex_o14_emit_probe_chart014_pair4
pair_chunk=4
pair_shards=248
max pair shard: 901.3 KB
min pair shard: 127.8 KB
forbidden scan: no #print axioms, sorry, admit, native_decide, sorryAx
```

## Safe Rerun Path If Current Wave Fails/Stalls

Wait for Claude's active wave to report a verdict first.  If it stalls or times
out on Chart014 pair shards, use the pair-4 emitter path:

```powershell
python problems/23/writeup/_codex_o14_batch_emit_lean.py `
  --slots 1-107 `
  --workers 8 `
  --export-dir tmp/o14_exports_v108 `
  --pair-chunk 4 `
  --summary tmp/codex_o14_batch_emit_pair4_summary.jsonl
```

Then run the sharded build with a combined worker budget that keeps the machine
under the agreed 64-thread Codex cap:

```powershell
python problems/23/writeup/_codex_o14_build_chart_payloads.py `
  --slots 1-107 `
  --cache tmp/claude_lean_o_base_v1 `
  --support-workers 16 `
  --base-workers 8 `
  --shard-workers 48 `
  --aggregator-workers 16 `
  --include-registry
```

Prefer this Codex build driver for the rerun instead of
`tmp/claude_o14_wave_regate.py`: it records per-module JSONL events, supports
per-file timeouts (default 1800 seconds; pass `--timeout 0` only for a
deliberate unbounded run), enforces the 64-worker cap, and its hardened token
scanner rejects `#print axioms` as well as `sorry`, `admit`, `native_decide`,
and `sorryAx`.  The active Claude wave script only writes shard failure details
at the end of the shard phase and its token scan does not reject stale axiom
probe lines.

If rerunning only the hot chart first, use:

```powershell
python problems/23/writeup/_codex_o14_build_chart_payloads.py `
  --slots 14 `
  --cache tmp/claude_lean_o_base_v1 `
  --support-workers 4 `
  --base-workers 2 `
  --shard-workers 32 `
  --aggregator-workers 4 `
  --summary-json tmp/codex_o14_chart014_pair4_build_summary.json `
  --summary-jsonl tmp/codex_o14_chart014_pair4_build_events.jsonl
```

The generated tree must have no `#print axioms`, `sorry`, `admit`,
`native_decide`, or `sorryAx` before a final O14 acceptance call.

## Follow-Up Non-Generated Adapter Build

After the generated-payload wave is no longer using the base cache, also build
the non-generated listed dispatcher adapter:

```powershell
lake env lean --root=problems/23/lean `
  problems/23/lean/Erdos23Delta0/O14/ListedChartCoverToODLFull.lean
```

That file composes the accepted listed v108 registry with the existing
`ChartCoverToODLFull` route-tree theorem.  It intentionally imports the
generated registry, so do not build it while the Chart001..107 wave is already
saturating the same cache.
