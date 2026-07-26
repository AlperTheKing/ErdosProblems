Round-9 progress log (kept here because the task forbids writing outside problems/23/round9/;
format follows the standing PROGRESS protocol).

[2026-07-26T02:34+03:00] > SETUP | NEXT: build exact psi engine (min over all 2^(n-1) bipartitions, Fraction/int64) and calibrate on known values
[2026-07-26T02:45+03:00] v SETUP | DID: R9_thmD_lib.py + R9_thmD_selftest.py | RESULT: 50/50 checks pass incl. bip(MTF14)=7, 92 pentagons, blow-up identity, Petersen 1/32 | D: none
[2026-07-26T02:50+03:00] > AUDIT-T1 | NEXT: exhaustive+random+hill-climb search for a Theorem D counterexample over every pentagon of every test graph
[2026-07-26T03:00+03:00] v AUDIT-T1 | DID: R9_thmD_audit.py | RESULT: 5157802 exact instances, 20 graphs, 503 pentagons, 0 violations; max of 25M-(q-r)^2-25re = 0 exactly | D: none
[2026-07-26T03:05+03:00] > AUDIT-T2 | NEXT: verify proof steps L1-L4 incl. the proof's own bipartition, on purpose-built adversaries + random triangle-free graphs
[2026-07-26T03:12+03:00] v AUDIT-T2 | DID: R9_thmD_adversarial.py | RESULT: 0 failures; L3 (R_j independent, N(R_j)^T subset T_j,T_{j+2},T_{j+3}) holds everywhere | D: Theorem D confirmed TRUE
[2026-07-26T03:18+03:00] v REFINED | DID: R9_thmD_refined.py | RESULT: refined per-cut bound F_i verified, 163320 cut-level checks, 0 failures | D: opens the constant-improvement route
[2026-07-26T03:25+03:00] v OPT | DID: R9_thmD_opt.py relaxation scan | RESULT: first-order ceiling of the per-cut method is eta = 1/5; R_0-vertices are the binding term | D: none
[2026-07-26T03:32+03:00] v THM-F | DID: R9_thmD_thmF.py | RESULT: radius 1/13 -> 4/25 PROVED (exact Lipschitz grid on [0,4/25], min phi/rho = 0.15687), 22920 instances 0 failures, sharp radius of the chain 0.16311797 | D: Task-2 bullet 1 answered
[2026-07-26T03:40+03:00] v THM-E | DID: R9_thmD_thmE.py | RESULT: master inequality psi <= min_i (y_i y_{i+1} + BAD_i) verified, 545651 exact weight vectors, 0 failures | D: blow-up formulation obtained
[2026-07-26T03:52+03:00] x RETRACTION | DID: audited my own corollary "BAD_i = 0 for some i => psi <= 1/25" | RESULT: FALSE, witness y=(1/6,1/4,1/6,1/4,1/6) gives min over any 4 cuts = 1/24 > 1/25 | D: withdrew all coverage claims (Wagner/Andrasfai/n<=10)
[2026-07-26T04:00+03:00] v THM-E2 | DID: R9_thmD_thmE2.py | RESULT: correct unconditional criterion = BAD_i = 0 for ALL i = homomorphism H -> C5; 3900 partition instances 0 failures | D: honest scope of Theorem E fixed
[2026-07-26T04:08+03:00] v RESIDUAL | DID: exhaustive min-BAD over all blow-ups/assignments/cuts | RESULT: Wagner [0,1,1,1,0], G11 [0,3,3,3,0], G14 [0,6,6,6,0], Grotzsch 1, MTF14 1, Petersen 2 (all 12 pentagons) | D: residual identified exactly
[2026-07-26T04:14+03:00] v NECESSITY | DID: R9_thmD_necessity.py | RESULT: triangle-freeness load-bearing, smallest witness g6 Ehf? with x=(2/5,2/5,0,0,0,1/5): psi=2/25 > 41/625; deficiency refinement 25300 checks 0 failures | D: none
[2026-07-26T04:20+03:00] v F3 | DID: R9_thmD_F3check.py | RESULT: 199787 exact (rho,z,K) triples, 0 failures, equality at rho=0 balanced | D: last unchecked step of Theorem F closed
