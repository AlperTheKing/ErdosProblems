
## [CODEX 2026-07-13T10:57:00+03:00, C26 AGGREGATED ENERGY]
TYPE: EXACT FINITE GATE / SPEC AMBIGUITY
1. Exact report: problems/424/fanout/wave3/C26_rd_aggregated_energy.md; probe and verifier: compute/wave3/C26_rd_aggregated_energy/.
2. Ray (3,2,1): (N,E) at K=2,3,4 are (1296,1298), (560088,562936), (212529321,213839845); max E/N=1.006166320928.
3. Ray (2,1,1): exact through K=6; terminal (N,E)=(307692465,308755831), E/N=1.003455937733.
4. No finite gate-(E) falsifier. K=5 for ray321 has exact N=32848227720, but direct expansion exceeds the 192 GB cap; streaming is required.
5. R2 ambiguity: the (2,1,1),k=1 block splits 6/6. Either color is valid and changes E3 2796->2806 and E4 171943->172823. Fix a canonical tie rule.
6. Fresh compilation, support/membership/color replays, eight hashes, and all energy identities pass. Finite ratios are not an asymptotic claim.

## [CODEX 2026-07-13T11:11:30+03:00, C28 R-D MASS K5]
TYPE: EXACT FINITE GATE
1. Exact packed residue-split DP proves |D_{15,10,5}|=330159210305 for ray (3,2,1), k=5.
2. M=6046617600000 and sqrt(30)|D|/M=0.299069097824444...; this extends the sequence without an observed collapse.
3. Peak memory 17.47 GB across 64 workers versus 755.8 GB naive. Three exact runs agree; 110 independent literal-set checks pass.
4. Report: problems/424/fanout/wave3/C28_exact_mass_gate.md; code/result/verifier: compute/wave3/C28_interval_dp/. Finite point only, no asymptotic gate-(M) claim.

## [CODEX 2026-07-13T11:26:00+03:00, C29 CRITICAL CARRY TRANSFORM]
TYPE: EXACT LEMMA / NEW REDUCED F2 FRONTIER
1. Report: problems/424/fanout/wave3/C29_offset_mass_gate.md. For inverse offsets, phi(d)=d+28/59 satisfies T phi<=phi exactly, equality iff d=28 mod30.
2. Doob kernel K(d,dprime)=(30/31)phi(dprime)/phi(d) is substochastic and gives exact path identity R_v(d)(31/30)^(-n)phi(0)/phi(d).
3. For canonical v_k=(15k,10k,6k), gate (M) follows from the explicit uniform local limit Pr_d[X_31k=0,N=v_k] <= C phi(0)/(phi(d)sqrt(k)).
4. This is now one concrete Markov-renewal/ballot frontier, not the original support conjecture. Equality state is one residue class mod30; all other states have exact killing.
5. Verified: 1,000,001 integer potential checks, 87,491 multiplicities, 53,722 paths, all 3^14 rewrite words, and exact D through k=5. No LL proof or falsifier yet.
