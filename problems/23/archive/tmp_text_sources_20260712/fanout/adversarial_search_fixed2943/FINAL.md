Result: the GLOBAL optimum and hub deactivation are not certifiable from the archived specification available in this checkout.

Exact reconstructed objective:

\[
S(\omega)=2\sum_{x,y}\max(\operatorname{pairCount}_\omega(x,y)-1,0)
+2|\operatorname{activeEdges}_\omega|,
\]

over \(680^{676}\) selector-row choices, with 707 rigid rows. `activeEdges` depends on the full selected vertex and path-edge unions.

Verified integer facts:

- \(676(680-1)=459004\) Hamming-one replacements.
- Baseline \(S=30811\); archived Hamming-one minimum \(30813\).
- \(19953+52\cdot200+458=30811\).
- \(2943-2775=168\).

Explicit falsifier to deriving a global conclusion from those aggregates: two symmetric landscapes can agree at the baseline and every Hamming-one move yet differ globally:

- \(S_A(k)=30811+2k\): minimum 30811; hubs remain active.
- \(S_B(k)=S_A(k)\) for \(k<676\), but \(S_B(676)=0\): all selectors changed jointly and hubs deactivate.

I checked every compressed count \(k=0,\ldots,676\). These are logical completions, not realizability witnesses; they rigorously show that the archived aggregate data do not determine the requested answer.

Missing proof-critical data:

- canonical 2943-vertex edge list and cut;
- all \(676\times680\) selector rows and their ordering;
- 707 rigid selected rows and baseline indices;
- precise scoped-component activation data.

The referenced artifact with SHA-256 prefix `00186166` is absent.

Source hashes:

- `CODEX_ONBOARDING.md`: `e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0`
- `CLAUDE_TO_CODEX.md`: `b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126`
- `WALL_ATTACK_R29_GPTPRO56.md`: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
- `MinimumDemandRowSelection.lean`: `e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a`

Artifact writing was blocked by the Windows sandbox wrapper; no nonempty lane report/code could be safely emitted.