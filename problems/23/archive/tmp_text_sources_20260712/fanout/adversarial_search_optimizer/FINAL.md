Implemented the exact scoped-score optimizer and certificate framework under [adversarial_search_optimizer](E:\Projects\ErdosProblems\tmp\fanout\adversarial_search_optimizer).

Key results:

- Exact integer-only evaluation and exhaustive global optimization.
- Safe per-atom duplicate-row orbit compression.
- Active-component deactivation support.
- Replayable `exact-scoped-opt-v1` certificates with SHA-256 bindings.
- Selector/cable toys verified for \(k=1,\ldots,8\), covering 2–256 compressed terminal states.
- All toy optima are exactly 0 via the all-bypass choice.
- R29-2943 was not reconstructed: the handoff omits the canonical 676×680 row database, so aggregate data cannot determine component deactivation exactly.
- Remaining gaps: boundary-equivalent cut-state merging, cross-atom orbit compression, and stronger deactivation-aware lower bounds.

Full claims, falsifiers, tested ranges, hashes, and proof gaps are in [REPORT.md](E:\Projects\ErdosProblems\tmp\fanout\adversarial_search_optimizer\REPORT.md). Report SHA-256: `FD75108170F88554E668BC0031F8870B01C3502A38405A66D4941E8A74E20CD7`.