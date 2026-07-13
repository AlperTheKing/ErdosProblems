Completed the cable-variant lane.

Key results:

- Exhaustively enumerated 673 triangle-free, max-cut-bipartition-compatible tree cables with 3–6 edges.
- Tested all 4,728 topology/seed-placement pairs using integer arithmetic.
- The R29 six-edge cable is record 671.
- Its unique trade-stable internal seed set is exactly `{a,zL,zR}`.
- Proved the structural persistence invariant: rigid selection of every cable vertex plus permanent off-row-support cable edges keeps the hub component active under arbitrary simultaneous selector trades.
- Supplied explicit falsifiers when either seed coverage or off-supportness is removed.
- The actual 2943 global scoped score cannot be evaluated: its graph serialization and 676 selector row banks are absent. No claim of global minimality or persistent Hall failure was made.

Artifacts:

- [REPORT.md](E:\Projects\ErdosProblems\tmp\fanout\adversarial_search_cable\REPORT.md)
- [enumerate_cables.py](E:\Projects\ErdosProblems\tmp\fanout\adversarial_search_cable\enumerate_cables.py)
- [results.json](E:\Projects\ErdosProblems\tmp\fanout\adversarial_search_cable\results.json)

Report SHA-256: `6F07315CA5068FD44EF00B84E98598FFF60E340F66BC633036908F2A7D1AFBAF`