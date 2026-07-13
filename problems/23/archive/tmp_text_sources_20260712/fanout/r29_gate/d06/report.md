# R29 Hamming-one gate (d06)

## Verdict

**NOT REPRODUCIBLE FROM WORKSPACE INPUTS.** I did not verify the claimed
minimum 30813, its multiplicity, or a sharp witness. The sole located R29
artifact is an aggregate prose claim, not the claimed selected tuple.

## Exact checks completed

- Candidate-count arithmetic is exact:
  `676 * (680 - 1) = 459004` nontrivial selector-row replacements.
- The aggregate claim says baseline `30811` and minimum `30813`, hence claimed
  gap `2`; neither value can be recomputed without the omitted objects below.
- `audit_manifest.py` uses only `int` and `fractions.Fraction`, rejects floats,
  and refuses to run a census unless first-principles inputs are present.
- Running it on `aggregate_claim.json` yields the falsifier:
  `INCOMPLETE MANIFEST: missing vertices, edges, cut_side, rows, selected, scope`.

## Missing proof inputs / gaps

The workspace does not provide, in machine-readable or fully explicit form:

1. the 2,943 labelled vertices and 8,422 labelled edges;
2. the labelled max-cut partition defining `B` and `I`;
3. every admissible ordered row (including all 680 rows for each selector atom);
4. the 1,383-entry claimed selected tuple and atom-to-row indexing;
5. the exact scoped-score definition and scoped vertex set for this instance;
6. the claimed sharp replacement witness.

Consequently, enumerating 459,004 indices would only enumerate aggregate
placeholders, not row replacements, and assigning scores would necessarily
encode the diagonal-collision claim that this task explicitly forbids using as
code. Exact minimum and multiplicity are therefore **undetermined**.

## SHA-256

- source prose `problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md`:
  `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
- `audit_manifest.py`:
  `f3dd0ec6560b13645741eff04320c0e16c3b7d2d3d2d6bf8daf17539061511cb`
- `aggregate_claim.json`:
  `a8c8af89dda18b839a90783c480f1ac03cdebedffad0eee95cb0425fcc2fdbe6`

## Required falsifier-first rerun

Supply one canonical JSON manifest containing the six rejected keys. The gate
must then reconstruct row validity, `I`, active components, collision counts,
and scoped score independently for the baseline and all replacements; any
score `< 30813`, count other than 459004, or mismatch of baseline 30811
falsifies the claim.
