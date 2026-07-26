Local progress log for the R9 odd-K5 workflow. (The global protocol asks for appends to
E:\Projects\ErdosProblems\PROGRESS.md; this task forbids writing outside problems/23/round9/,
so the lines are recorded here and were also printed to the caller.)

2026-07-26T02:40 ► R9-ODDK5-SETUP | NEXT: build an exact library (bip, odd-cycle covering LP with two-sided certificates) and calibrate it on the brief's own numbers
2026-07-26T02:55 ✔ R9-ODDK5-SETUP | DID: R9_oddk5_lib.py + selftest | RESULT: 26/26 PASS incl. bip(K5)=4, Lambda(K5)=10/3, psi(subK5,unif)=4/625, Lambda=2/375 | Δ: tooling gated
2026-07-26T03:00 ► R9-SIM | NEXT: prove and machine-check that an odd subdivision preserves bip and Lambda, then simulate arbitrary weighted instances by product weights
2026-07-26T03:20 ✔ R9-SIM | DID: Lemma S + Lemma SIM verified on 12 weighted instances | RESULT: psi(H,x)=bip_c(G) and Lambda(H,x)=Lambda_c(G) exactly in 12/12 | Δ: gap-constant route DEAD
2026-07-26T03:25 ► R9-SRG | NEXT: construct the triangle-free strongly regular graphs from GF(4)/PG(2,4)/S(3,6,22) and compute exact psi and Lambda
2026-07-26T03:40 ✔ R9-SRG | DID: Higman-Sims, M22, Gewirtz, Hoffman-Singleton built and certified | RESULT: Lambda=m/5 exact via pentagon packings; bip(HS)=350 exact; psi/Lambda=35/22 | Δ: record 6/5 -> 35/22
2026-07-26T03:45 ► R9-PETERSEN | NEXT: test the brief's claim that Guenin covers the Petersen graph
2026-07-26T03:55 ✘ R9-PETERSEN | DID: switching at the inner 5-set + contraction; weight w=(1 outer/inner, 5 spokes) | RESULT: tau_w=4 > 10/3=tau*_w, gap 6/5 | Δ: premise (C) of the brief is FALSE
2026-07-26T04:00 ► R9-MINORDER | NEXT: determine the smallest triangle-free graph carrying an odd-K5 minor
2026-07-26T04:15 ✔ R9-MINORDER | DID: parity criterion + 4^10 enumeration + all 1897 triangle-free 9-vertex graphs | RESULT: min order 10, min size 15, unique = Petersen; 0 hits at n=9 | Δ: open class starts at N=10
2026-07-26T04:20 ► R9-SUMS | NEXT: settle how psi behaves under 1-sums and 2-sums
2026-07-26T04:30 ✔ R9-SUMS | DID: 1-sum additivity, bowtie sweep D<=25, 2-sum min-formula | RESULT: bowtie max psi = 1/25 exactly; (p+q)/2 <= W^2/25 falsified by 1/16 > 1/25 | Δ: 2-sum is the only gluing that can gain
2026-07-26T04:35 ✘ R9-PROFILE | DID: exact grid test of my own C5 profile formula | RESULT: f(1/12) = 1/40 > 11/576, formula RETRACTED; corrected f is irrational at rational u | Δ: none
2026-07-26T04:45 ✔ R9-DICHOTOMY | DID: combined accepted psi <= e-4e^2 with Lambda <= e/5 | RESULT: a counterexample needs e in (1/20,1/5) and gap > 1/(5e) in (1,4); every witness here falls short | Δ: hunt directed to dense configurations
2026-07-26T04:55 ✔ R9-AUDIT | DID: R9_oddk5_audit.py, independent re-derivation of every load-bearing number | RESULT: ALL PASS (A1-A5) | Δ: none
