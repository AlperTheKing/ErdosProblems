Completed the exact generic gate under [d09](/E:/Projects/ErdosProblems/tmp/fanout/r29_gate/d09/report.md).

Verdict: indeterminate from available artifacts. The workspace lacks the actual graph, row lists, baseline tuple, and arbitrary-trade scoring rule. Exact branch-and-bound countermodels reproduce all recorded local facts but give opposite global outcomes:

- Model A: minimum `30811`, no deactivation.
- Model B: minimum `0` at the all-ones 676-selector tuple, with hub/descendant deactivation.

Artifacts:

- [audit.py](/E:/Projects/ErdosProblems/tmp/fanout/r29_gate/d09/audit.py)
- [certificate.json](/E:/Projects/ErdosProblems/tmp/fanout/r29_gate/d09/certificate.json)
- [hashes.txt](/E:/Projects/ErdosProblems/tmp/fanout/r29_gate/d09/hashes.txt)

No files outside `tmp/fanout/r29_gate/d09/` were edited.