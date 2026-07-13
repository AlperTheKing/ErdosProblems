# Lane 06 exact MicroDemand gate

Verdict: PASS; integer arithmetic only.

Coverage: 2 graphs, 2 canonical/global-minimum tuples, 2 HitNeed-positive tuples recomputed, 0 HitNeed-zero inherited, 2 exact flows, 12 owner shores, 0 skipped inputs. N=3892 permanent-Free distance identities cover every row choice exactly.

N=2943 recovered one-copy demand 19953, old reach 19925, and 216 new keys. Production demand is 20025, reach 20141, exact flow 20025, full-shore margin 116.

N=3892 has collision (4:0, 8:0), HitNeed (4:1, 8:1), MicroDemand (4:25, 8:25), exact flow 50. Certified shore margins: 0,18,13,31. Its 81 disjoint sources satisfy dB=58, dM=0 and are permanently Free.

Replay: `python r29_gate.py`; `python n3892_gate.py`; `python gate.py`; `python verify.py`.
