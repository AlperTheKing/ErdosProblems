# Hamming correction

The fixed-baseline-active-scope delta method in `r29_hamming_gate.py` is not an
acceptance verifier. It obtained the correct minimum score `30813`, but reported
minimum multiplicity `676` instead of `1352`.

Exact falsifier to the fixed-scope assumption:

- old row: `[735,732,59,56,2760]`
- new row: `[735,55,57,56,2760]`
- full active-scoped score: `30813`
- vertex `57` is duplicated but leaves active scope, so its fixed-scope diagonal
  contribution must not be counted.

Accepted replacement gate: `d06/retry2/audit_retry2.py` recomputed selected
vertices, support, active components, collision, and HitNeed from first
principles for all `459004` replacements. Result: minimum `30813`, delta `+2`,
multiplicity `1352`; output SHA256
`b71bdde11707600150f6f111c2644efa3fcfc687349b11a9f891c2a2ea6f521f`.

The universal premises `Q\\P != empty` and baseline multiplicity one remain
true, but a new diagonal term counts in the scoped score only while its owner
remains in active scope.
