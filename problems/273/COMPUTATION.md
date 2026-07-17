# Computation


## Exact environment

- System Python: exact-integer runtime with OR-Tools `9.14.6206`, PySAT `1.8.dev24`, SciPy `1.14.0`, SymPy `1.14.0`.
- Available PySAT engines include CaDiCaL 103/153/195, Glucose 3/4/4.2, Lingeling, Maple variants, MergeSat3, and Minisat22.

## Reconstructed p >= 3 baseline

Certificate: `baseline/selfridge_divisors_360.json`.

Verifier A:

`python problems/273/verifier_a/verify.py problems/273/baseline/selfridge_divisors_360.json --output problems/273/verifier_a/verification.json --hashes problems/273/verifier_a/verification.sha256`

Results: true LCM 360; 0 uncovered residues; multiplicity histogram `{1:270,2:80,3:10}`. Deleting `0 mod 2` leaves exactly 180 even residues. Certificate SHA-256 `18ae07873d1244003b01c566825e00e90076efe086011ecfeaad2273ad5dc13a`; report SHA-256 `9dc604e8978a42e2f1b5a47cbeed5f4504b7970c79568db2a53381063991ffce`.

Verifier B:

From `problems/273/verifier_b` run

`python -B verifier_b.py baseline_half_cover_certificate.json --log verifier.log`

and

`python -B -m unittest -v test_verifier_b.py`.

Results: independent residual chain `180->90->60->48->24->16->12->6->5->3->1->0`; 8/8 adversarial mutations rejected; manifest check has 0 failures. Certificate SHA-256 `0d61797736913548b708e90224a9f101fa1270c62409b487408a298ca84034b1`.

## Fixed-H0 smooth-period scan

Command:

`python problems/273/search/period_mass/scan_period_mass.py`

Parameters: all 1296 periods `2^a3^b5^c7^e11^f` with inclusive exponent bounds `(8,5,3,2,1)`; admissible `d|L`, `d>=2`, `2d+1` prime, `d notin H0`.

Result: no period has reciprocal mass above 1. Unique maximum is `462476029/598752000` for `L=4191264000`, with 400 admissible divisors. Manifest SHA-256 `9fee15d52930d4c6fa5254ecfd05d7417db5f9f06aed9fb4a78f002c2aa7e909`.

## Infinite five-prime tail

For arbitrary exponents on prime support `{2,3,5,7,11}`, the full eligible H1 mass is at most

`462476029/598752000 + (77/16 - 234403/49500) = 508631341/598752000 < 1`.

Exact gap: `90120659/598752000`.

## Unrestricted bounded-modulus density threshold

Independent exact sieve and SymPy enumerations agree: after excluding H0, reciprocal mass first exceeds 1 at d=140 with 47 candidates. The canonical candidate-list SHA-256 is `1af3c5b9a10674c3cae8256173f4e3c727e0cf6cf7b25cfd5120c1b4e8814473`.


## One-prime support extensions

Commands:

`python problems/273/search/one_prime_extensions/scan_h1_extensions.py`

`python problems/273/search/one_prime_extensions/crosscheck_h1_extensions.py`

Both exact implementations and the SHA-256 manifest replayed successfully. The supports obtained by adjoining one of `17,19,23,29,31,37,41,43,47` to `{2,3,5,7,11}` are globally subcritical for fixed-H0 refinement. For `r=13`, the finite-box mass is `24809923283/27243216000 < 1`, while the tail upper bound is `27911969321/27243216000 > 1`, so this method leaves it open.

## Joint density screen

Commands:

`python problems/273/search/joint_density/joint_density_scan.py`

`python problems/273/search/joint_density/independent_verify.py`

All 1296 periods in the inclusive box `(8,5,3,2,1)` were checked without fixing `H0`. Exactly 296 have reciprocal mass above 2 and a complete two-bin reciprocal partition with both bins above 1. The least is `L=27720`, with 43 candidates and mass `6429/3080`. Independent verification and both manifests pass. This is only a necessary-condition screen.

## Six-prime fixed-H0 elimination

From `problems/273/search/r13_expansion`, run `python prove_subcritical.py` and `python verify_subcritical.py`. Both replay successfully. The decisive box is `(8,5,3,2,2,6)` and the exact full-support upper bound is `216370454467826777/222534738762336000 < 1`. The verifier checks 16,188 prime/composite records. Manifest SHA-256: `f3cfb5b2b29765bbf36b9b5bc16fa2af906012e4afede06fc364f38b032b65a8`.

## Restricted joint obstruction at 27720

`problems/273/search/joint_27720` contains the human `d=5` obstruction and an independent exhaustive tree certificate. Replays report 5,095 nodes, 3,384 prunes, zero leaves, and 5/5 rejected mutations. Certificate SHA-256: `fea71f091b253b75e3d147ea8dbb44710f568076cea29ace886cbdc687899948`; manifest SHA-256: `518c862afd491a27738d951e05d68ee82e3a2b3d3ee33dad7f89b1767c64f276`.

## Joint overlap-capacity sweep

`problems/273/search/overlap_batch/screen_all.py` ran all 296 density-passing periods with 16 processes and a 30-second cutoff per period. Statuses were 132 `INFEASIBLE`, 29 `UNKNOWN`, and 135 `OPTIMAL` allocations. An independent exact verifier checked every one of the 135 exported allocations. The least capacity-feasible period was `L=138600`; a 32-worker rerun classified the smaller `L=110880` target as overlap-infeasible. Solver `INFEASIBLE` rows are search guidance until accompanied by independent certificates.

## Mandatory-anchor and local-overlap audit

`problems/273/search/mandatory_pair_audit` independently reproduces the 1296-period census. The ordered-pair lemma kills 135 density-passing periods and the stronger single-mandatory-anchor lemma kills 136. For `L=55440`, two independent exact implementations enumerate 5760 mandatory configurations, retain 420 after local redundancy, and rule out all 420 with combined-union upper bound at most `104063/55440`. Manifest SHA-256: `8ed8d624b4b68e1a723a1f26955ba205539f617b1289cd5fec6b3009e4c94a12`.

## Exact Farkas certificate at 55440

`problems/273/search/joint_55440` supplies eight nonnegative rational Farkas rays for the eight mandatory placements. The standard-library verifier, five tests, and independent CP-SAT model all pass. Certificate SHA-256: `9d15a82c2ddff0bf3ae19220abf2125166ae1329ef0325de0e701da9220949f1`.

## First allocation at 138600

The first 12-modulus side exported by the capacity model is exactly infeasible. A full-period CP-SAT model reports `INFEASIBLE`; independently, `verify_fixed_a_obstruction.py` checks the three-parity pigeonhole proof over all eight parity assignments and finds zero survivors.

## Exact two-branch certificate at 110880

`problems/273/search/joint_110880` contains a solver-independent rational certificate and verifier. Replay returns `VERDICT=INFEASIBLE`, rejects 13/13 mutations, and verifies manifest SHA-256 `1994273d8a6358fee7a45b37b5447a770201465d6b45b83140530653d7f211a8`.

## Baseline subset minimization

`problems/273/search/minimal_baseline_halfcover` checks all 2048 subsets of H0 and independently proves the 11 single-deletion cases infeasible in 396679 nodes. Only the full 11-modulus set covers. All 13 artifact hashes replay.

## Exact four-branch certificate at 83160

`problems/273/search/joint_83160` contains a generated rational capacity certificate and an independent standard-library verifier. Certificate SHA-256: `465ae00cbe384a0473c1f4fd6802d4ac60b1446dc70a33308285c712b53fdd18`.

## Exact q=6 obstruction at 138600

Run `python problems/273/search/joint_138600_agent/verify_obstruction.py`, `python problems/273/search/joint_138600_agent/verify_obstruction_independent.py`, and `python problems/273/search/joint_138600_agent/verify_hashes.py`. The replays return PASS with excess 116778, forced incidences 179730 and 133056, gaps 62952 and 16278, and a valid 27-file SHA-256 manifest.

## Extended support and quotient screens

problems/273/search/support_discovery scans 10368 periods on support {2,3,5,7,11,13,17,19} with inclusive caps (8,5,3,2,1,1,1,1). Exact Miller-Rabin generation and an independent SymPy/direct-incidence replay agree: 3402 periods have mass above two. The mandatory-anchor screen eliminates 918; its independent Fraction replay validates every witness. Results SHA-256 is f8c450e6ba729795e3bd28030f73a955687214c694f7c13f9df077f995d92f2a.

problems/273/search/q6_screen_audit runs scan_q6.py and verify_q6.py. Replays give 1296 periods, 296 mass-supercritical, 166 q=6 kills, 19 additional q=30 branch-6 kills, and 111 survivors. The least survivor is 831600. Manifest SHA-256 is a3617c48c6b31ccba254a56945c9792c71759e1e0fa61b1e8248ef14104fe713.

## Exact restricted obstructions after 138600

problems/273/search/joint_166320 contains two exact quotient verifiers and a seven-file manifest. Replays return 71 candidates, 16 q=24 cases, and contradiction gap 47016. Manifest SHA-256 is f721f7a5985fef5e6f4a4dee04b3d8dc5c46b5ebaee95459719a472cf610694c.

problems/273/search/joint_221760 contains two exact q=6 verifiers. Replays return 68 candidates, 24 anchor cases, and gaps 85224 and 16356. Manifest SHA-256 is d0e2e2f4220d992b2dc0c76722bd002cab746401d64fe1b4c270ce6e8a558179.

problems/273/search/joint_support_13 verifies all 840 periods in caps (6,4,2,1,1,1), 28689 candidate occurrences, and the L=32760 mandatory-5 certificate. Six mutations are rejected. Manifest SHA-256 is 119b59c9701448d568309458a56b6eaf095ee7b5383add5919c859e32b671e56.

## Verified refinement gadget

The archived GPT-Pro checker is problems/273/gpt_pro/001_erdos273_refinement_check.py; the independent checker is problems/273/search/refinement_105525/verify_independent.py. Both verify the d=105525 five-child identity over the full period 1266300 and all six successor primes. Certificate SHA-256 is d6ddaef59241a0afa2380cdc9a8faa6ff2c89e877e1a908f072b8860d593f792.

## Later exact joint-period certificates

problems/273/search/joint_360360 verifies 384 q=24 cases, 368 direct eliminations, and 16 capacity cuts. Final 21-file manifest SHA-256: 8d8f483dfd7d14be481910eea4544a2324aca9d95970801b3f5aa90bb847efbf.

problems/273/search/joint_831600 verifies 4862 q=120 states and gap 289/55440. Manifest SHA-256: 7fc517bdb5f4871145ca089eb3107416b3b6669d8ba0e22d45e30a46ef68cd30.

problems/273/search/joint_997920 verifies 4862 q=120 states and gap 29/2376. Manifest SHA-256: 8964d9e4a74c5098bd4ded43bb6820be06487da94a0fc8e7e7052e8b2493cf58.

problems/273/search/joint_1108800 verifies 4862 q=120 states and gap 1693/73920. Manifest SHA-256: e6cdb6dd82f61f661fdecf61d59528d8ea21f48473666ae5815fc075ef8ea6d5.

## Baseline-collision refinement census

problems/273/search/quotient_refinement_census scans 28512 parent-period pairs for the 11 H0 parents on quotient support {2,3,5,7,11,13}. Independent SymPy replay passes. The d=15,Q=13860 mandatory-pair certificate, d=90,Q=49140 mandatory-union certificate, and all ranking/search logs are hashed in a 25-file manifest with SHA-256 880f9ce37ce58cf4e658203ec292b710a143409519239db256ec6ff7f9aed436.

problems/273/search/baseline_refinement_gadgets contains the exact 37688965-state d=3,Q=420 tree and independent CP-SAT replay. Manifest SHA-256: df2f2a13...66129.

problems/273/search/d90_q196560_exact contains two exact candidate/capacity verifiers for the normalized-q=3 deficit of 310 residues. Manifest SHA-256: 77cc4f9e78516d9e256b327eaec0d40df42c98b19e1db6bb0c897a37560aea6e.

## Extended q=30 and later exact certificates

problems/273/search/support_discovery/verify_q30_extended.py independently replays 3402 rows using SymPy candidates, integer weights, and direct q=30 quotient unions. It confirms 1273 prior q=6 kills, 340 additional q=30 kills, 1789 survivors, and least survivor 360360. The 16-file manifest SHA-256 is a22207a3bf9b8f3df727da3e7d2b8b61a7422e673c19934f1ab33c1af7dfbf50.

problems/273/search/joint_655200 checks 91 candidates and 4862 q=120 states; exact gap 45989/655200. Manifest SHA-256: 50710b2159edb9b53189103b3886c66105fa0d0db27ad9f9829b7b2db2f914e1.

problems/273/search/joint_720720 checks 96 candidates and 150722 q=120 states after adding anchor 15; exact gap 41/1092. Two independent verifiers and the scope audit pass. Manifest SHA-256: 65fb7832a5a4a7c50298b28a518a899b86c901851630b15053bca10ae78d16fc.

problems/273/search/joint_1247400 checks 101 candidates and 4862 q=120 states; exact gap 4847/311850. Manifest SHA-256: 49883317317d927cbe48f8ec8b24598549fc8f58bec05d1b15095da6d614a1bf.

problems/273/search/joint_1330560 checks 98 candidates and 4862 q=120 states; exact gap 883/55440. Manifest SHA-256: 0887718ca0fbb6a142efd8d0e1083ab61193b39f6aa7b85f27d3d58ed02628af.

problems/273/search/d90_next_refinement independently checks all 602 q=3 rows and both q=9 verifiers at Q=393120. The screen kills 320 rows; the Q=393120 minimum gap is 135486. Manifest SHA-256: 7a77d998f5f704c15e36a3463c920495f59706f8a45f95c6359ceca6335f0cea.
