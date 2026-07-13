# Erdos 23 Preservation Manifest

Frozen: 2026-07-12
Workspace: E:\Projects\ErdosProblems

## Durable artifacts

| Artifact | Files | Size | Integrity/status |
|---|---:|---:|---|
| Final handoff | 1 | text | Section-by-section proof boundary |
| 108-chart exact archive | 442 | 457.02 MiB | 108 rows, 0 hash mismatches |
| Final replay archive | 81 | 25.45 MiB | 9/9 expected exits after tmp deletion |
| Recovered tmp text sources | 3,328 | 458.12 MiB | SHA256SUMS included |
| Obstruction paper source | 13 | 0.16 MiB | clean 5-page arXiv build |
| Release PDF and ZIP | 3 | 0.10 MiB | hashes below |

## Canonical hashes

    chart ledger:
    981D353F88C8148DEC975DF75CBEDCC4975505F2ADF2345E6A6A9329FD3BD1AF

    chart SHA256SUMS:
    84EBDBA3FFA6DEEC3AF135763856F95D3936BC1E6058BB6FD5A8AA9A700ACDD1

    replay manifest:
    2A2B06FB4DFF54BEE472E1CE8A3B459D7714A2C502C2868D8FBCB0C3454418C7

    replay report:
    B225BCB558519E162ED5B1229D62D585D0307FFB3EC747E440BF30AAEDF69581

    recovered-source SHA256SUMS:
    B1246199AE34617498773EC0662C9C1611D9800987797572C13BF077D8F23514

    obstruction paper PDF:
    67DD92FEF8376B81091327CDA1CDA5690603BBAC7C4E0A8B6AEEB4BF0E7BBCFB

    obstruction paper source ZIP:
    6831828B86D5151DCEC5C29869536E65D2B4B1D5EF0ABA96498E4BF4DBF2943C

## Canonical paths

    problems/23/ERDOS23_FINAL_HANDOFF_20260712.md
    problems/23/archive/chart_v108/
    problems/23/archive/20260712_replay_audit/
    problems/23/archive/tmp_text_sources_20260712/
    problems/23/writeup/CODEX_GAP1_GROUNDING_MAP_20260709.md
    problems/23/writeup/WALL_ATTACK_R58_FINAL_R55_R57_VERDICT.md
    problems/23/writeup/SHORTEST_SUPPORT_HALL_COUNTEREXAMPLE_FAMILY.md
    problems/23/writeup/arxiv/shortest_support_obstructions/
    output/pdf/

## Removed reproducible data

First pass:

    28,686 files
    1,131.258 logical GiB
    tmp oleans, executables, bytecode, temporary shards, stale logs

Final pass:

    old tmp tree: 8,863 files, 9.1 GiB before archival/deletion
    O14/Generated: 43,136 files, 34.96 GiB
    O14/CompactPilot: 277 files, about 0.03 GiB
    remaining problems/23 oleans: 2 files, 10.68 MiB

Final disk state:

    E free: 1,062.15 GiB
    problems/23: 1.05 GiB
    tmp: empty directory

## Regeneration

The chart archive is the non-regenerable exact result. Generated Lean O14
payloads are regenerable from the archived chart data and generator scripts
under problems/23/writeup or the recovered-source archive.

To restore historical tmp-relative chart paths:

    Copy-Item problems/23/archive/chart_v108/* tmp/ -Force

To replay the final exact gates:

    python -B problems/23/archive/20260712_replay_audit/run_audit.py
    python -B problems/23/archive/20260712_replay_audit/finalize_audit_v2.py
    python -B problems/23/archive/20260712_replay_audit/verify_manifest.py

To verify the infinite support-Hall counterexample family:

    python -B problems/23/writeup/_codex_support_hall_family_verify.py

## Scope warning

The archive preserves a published finite theorem, exact finite certificates,
and new obstruction results. It does not contain a proof of the full Erdos 23
conjecture. The missing theorem is the real graph-derived full-bank provider
described in ERDOS23_FINAL_HANDOFF_20260712.md.
