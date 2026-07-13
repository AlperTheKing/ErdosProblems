# Worker 4 result

PASS. `verifier_b.py` independently reconstructs the all-anchor tuple from the canonical R29 graph, then derives tuple incidence, active components, hub obligations, all four source patterns, exact capacities, and all eight owner-shore inequalities. It imports no worker implementation.

Exact counts:

- hub demand: 6,651 each; 19,953 total half-slots
- sameFirst: 17,325 new half-slots
- commonBad: 0 new half-slots
- rowCompanion: 2,600 new half-slots
- old three-pattern reach: 19,925; deficiency 28
- outsideAttachment: 676 eligible singleton vertices per owner, 456,300 ordered pairs, switch loss 8 for every pair, 912,600 new half-slots
- four-pattern reach: 932,525 half-slots
- maximum deficiency over all eight owner shores: 0
- reserved ordered cells: `(0,55)`, `(1,2929)`, `(2,2930)`

Replay: `python verifier_b.py` from this directory. The command exits 0 and rewrites `certificate_b.json` deterministically.

SHA-256:

- `verifier_b.py`: `36af058890f56c3035d9500bbce85a8c0b3b54c5eed0eba7ec6d3b4ab0491dc4`
- `certificate_b.json`: `e684855e288a63b48ed9e90bbc62a08e262f2e023c404c0e4cdbfaafe59de6f1`

All accounting uses integers and `fractions.Fraction`; no floating-point operations occur.
