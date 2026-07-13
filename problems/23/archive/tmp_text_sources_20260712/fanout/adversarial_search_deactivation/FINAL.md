The R29 archive does not determine a joint deactivation threshold.

Exact claims:

- Every Hamming-one trade preserves all positive-score regions, so any deactivation requires at least 2 selectors.
- With 676 selectors, the minimum for hubs, leaves, cable/locks, or circuit is only bounded by `2..676`, or the region may never deactivate.
- Baseline score:
  `19953 hubs + 10400 leaves + 458 circuit = 30811`.
- Direct block removal changes are:
  - hubs: `−19953`
  - each leaf: `−200`
  - all 52 leaves: `−10400`
  - circuit: `−458`
  - cable/locks: no separately specified score
- Conditional on the unproved assumption that joint collision costs remain exactly additive at `+2k`:
  `Δ(k,H,L,C)=2k−19953H−10400L−458C`.
  The radius-one `+2` result does not establish this for joint trades.

Falsifier: for every threshold `d∈[2,676]`, a compressed landscape can preserve all regions for `k<d` and deactivate them at `k=d`, while matching every archived Hamming-one fact. Hence the available facts permit 675 different thresholds, plus “never.”

Proof gaps: the workspace lacks the labelled graph, cut, `676×680` row lists, selected tuple, joint component evaluator, collision matrix, and the full artifact matching `00186166…`. Therefore no actual descending joint trade or connectivity invariant can be certified.

Source hashes:

- R29 archive: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
- Coordination mailbox: `b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126`
- Onboarding: `e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0`

Artifact creation was blocked by the Windows patch sandbox, which refused writes inside the assigned lane despite it being under the workspace. No shared files were modified.