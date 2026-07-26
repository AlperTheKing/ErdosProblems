R9 / discharging-with-a-global-potential — progress log (protocol format; kept inside
round9/ because the task scope forbids writing outside this directory).

[2026-07-26T02:35+03:00] ► R9-ORIENT | NEXT: read APPROACH_REGISTRY + round3 band results to avoid re-deriving the dense half
[2026-07-26T02:40+03:00] ✔ R9-ORIENT | DID: read APPROACH_REGISTRY.md, round3/G12.md | RESULT: dense half |E|>=N^2/5 => bip<=N^2/25 already published (EFPS 1988, round3/audit_G12.md:38) | Δ: MS-deficit idea pre-empted
[2026-07-26T02:45+03:00] ► R9-LIB | NEXT: build exact library (graph6, 11 mandated witnesses, bip, psi, subset DP, pentagons, sigma)
[2026-07-26T02:52+03:00] ✔ R9-LIB | DID: R9_discharge_lib.py self-test | RESULT: all 11 witnesses reproduce known bip (N14 bip=7 |E|=32, Petersen 3, Grotzsch 4, Wagner 2, Gamma11 4) | Δ: none
[2026-07-26T02:55+03:00] ► R9-T1 | NEXT: prove potential=DP-value theorem and compute V(G)=min over orderings of sum floor(d_i/2)
[2026-07-26T03:05+03:00] ✔ R9-T1 | DID: R9_discharge_dp.py | RESULT: Phi*(C5[2]) = 4-6 = -2 < 0; V>=(|E|-N)/2 kills the mechanism on 7 of 11 witnesses | Δ: amortised deletion + ANY potential DEAD
[2026-07-26T03:06+03:00] ✔ R9-T4b | DID: K_{m,m} DP | RESULT: V(K_{7,7})=18 vs bip=0; sup V/N^2 >= 1/8 | Δ: mechanism cannot prove any constant below 1/8
[2026-07-26T03:08+03:00] ✔ R9-T2 | DID: exact-cost DP on 10 witnesses | RESULT: U=bip identically | Δ: exact-cost and edge-deletion variants are circular
[2026-07-26T03:12+03:00] ✔ R9-T5 | DID: exhaustive removal-vector scan on C5[n], n<=12 (371292 vectors at n=12) | RESULT: only balanced peels (j,j,j,j,j) fit the budget, all exactly tight | Δ: needed pentagon-peel cost 2n-1 vs greedy 5n
[2026-07-26T03:20+03:00] ✔ R9-Q1 | DID: R9_discharge_local.py gate of C5[7,7,12,7,12] class cut {c0,c2} | RESULT: sigma=(19,19,14,0,0)>=0, 25*mono=2100>2025, min improving switch 11=0.2444N | Δ: no global potential rescues local-cut discharging (F(G)>=84>81)
[2026-07-26T03:30+03:00] ✔ R9-Q3 | DID: pentagon census of the 11 witnesses | RESULT: C7 has bip=1 and ZERO induced pentagons; mass form fails on Petersen/Grotzsch/C7/N14 | Δ: pentagon charging DEAD
[2026-07-26T03:45+03:00] ✔ R9-Q2 | DID: R9_discharge_radius.py exact locality scan N=10..45 | RESULT: max radius 13/45=0.2889N at C5[0,9,12,7,17]; maximisers are P4-blow-ups | Δ: any local rule must certify stability against >= C(N,0.29N) switching sets
[2026-07-26T03:55+03:00] ✔ R9-MS | DID: R9_discharge_msline.py, 3300 exact rational weightings | RESULT: psi+(4/5)W<=1/5 zero violations, margin 0 on every C5[n]; psi<=W/5 FALSE at N14 (7>32/5) | Δ: candidate is exactly the published dense half, adds nothing
[2026-07-26T04:05+03:00] ✔ R9-CENSUS | DID: R9_discharge_census.py on 11212 triangle-free graphs (n=9,10) | RESULT: V>=bip and V>=(|E|-N)/2 asserted, 0 failures; mechanism confined to |E|<=2N^2/25+N | Δ: potential buys only min-degree -> average-degree, additive O(1)
[2026-07-26T04:15+03:00] ✔ R9-VERIFY | DID: R9_discharge_verify.py | RESULT: sigma-identity exact on 11 witnesses; A19 target 434 vs 446 false by 12; step (*) holds at all 7000+ subgraphs for Phi*=f-V | Δ: every quoted number gated
[2026-07-26T04:20+03:00] ✔ R9-REPORT | DID: wrote R9_discharge.md | RESULT: mechanism dead in all three shapes; no new bound on bip | Δ: none for the conjecture
