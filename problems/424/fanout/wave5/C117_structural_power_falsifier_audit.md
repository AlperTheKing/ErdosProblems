# C117 independent audit

## Scope

This audit checks the six declared sparse-template artifacts, the retained
hard-source replay, and the aggregate manifest.  It does not promote finite
non-falsification to a structural theorem.

## Checks

- Recomputed SHA-256 for all six search artifacts; every digest equals the
  value embedded in `C117_manifest.json`.
- Re-ran `C117_structural_power_verify.py` normally and under `python -O`.
  Both outputs are byte-identical to the submitted replay, with SHA-256
  `0DB3E13323CF8E25C1DE8EF1BD88DB4BEDD08B83B4D035D08FB2A832B6049CC1`.
- Rebuilt the manifest under `python -O`; it is byte-identical to the normal
  and submitted manifests, with SHA-256
  `4FB5E1CF259CDECA5A3ED15047789F7E5474BA95FAA131411226B771635A1FCE`.
- Inspected the acceptance test.  The search accepts a counterexample only
  by the exact integer inequality `(s+8)^4 < d^3`; displayed logarithmic
  ratios do not affect acceptance.

## Verdict

The finite claim is accepted: 192,500 declared evaluations include 186,819
exact recursive classifications, eight hard survivors, no `3/4` falsifier,
maximum tested `d=128`, and largest tested source
`132131012341607575950114`.  All 86,319 classified divisor-raising sources
are generated; the hard survivors occur only in fixed-divisor-shape slot
substitutions.  The pointwise power law remains unproved.
