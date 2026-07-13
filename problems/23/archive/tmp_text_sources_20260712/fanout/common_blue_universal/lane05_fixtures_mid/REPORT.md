# Lane 05 — N=311 and N=2928 MicroMatching gate

## Verdict

`ABSENT_MATCHING_INPUTS`: zero MicroMatching passes and zero MicroMatching falsifiers. Both requested fixtures lack an available complete row-choice input, so two inputs are skipped exactly, not heuristically.

## Exact replay performed

Command (PowerShell, repository root):

```text
python tmp\fanout\common_blue_universal\lane05_fixtures_mid\audit_inputs.py
```

The wrapper ran:

```text
python problems\23\writeup\_claude_r20_311_gate.py
```

N=311 structural certificate replay returned rc=0 and checked triangle-free, exact max-cut 1359, Gamma 2300, N=311, |E|=1451, |B|=1359, |M|=92, 28 unique core rows, and 64 attachment atoms with 4096 shortest rows each. Full stdout/stderr are preserved.

## MicroDemand coverage

- Graph claims inventoried: 2 (one N=311, one N=2928).
- Complete canonical/global-minimum row choices available: 0.
- HitNeed=0 tuples inherited: 0.
- HitNeed>0 tuples recomputed: 0.
- Exact integer flows: 0. Exhaustive Hall cuts: 0.
- Passes: 0. Failures: 0. Exact skips: 2.

N=311 is skipped because the available constructor only proves aggregate row multiplicities and does not emit one selected Row5 for each of the 92 bad edges. `FreeHalf`, `ScopedReserved`, collision demand, and HitNeed cannot be evaluated without that tuple. Enumerating all `4096^64` attachment selections was not claimed or sampled.

N=2928 is skipped because only the R28/R29 prose specifications exist locally. The inventory found no executable constructor, serialized edge/cut payload, complete row choice, or replayable max-cut/Gamma certificate. The prose values are not treated as theorem evidence.

## Relation audited

The pinned production source defines owner demand as collision halves plus 25 copies of each ActiveHitNeed, and availability as `(EligibleOwner OR CommonBlueOwner) AND NOT ScopedReserved`. No older one-copy result was inherited.

Machine-readable counts, source paths, and SHA-256 hashes are in `result.json`. `MANIFEST.sha256` hashes every delivered artifact except itself.
