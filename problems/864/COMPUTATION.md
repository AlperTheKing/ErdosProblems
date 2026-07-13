# Computation

Goal: exact proof discovery and falsification, never finite-N extrapolation.

Immediate engine:
- exact admissibility checker for unordered pairs including diagonals;
- branch-and-bound maximum search;
- exceptional-sum symmetry and incremental updates;
- reproduce OEIS A389182 through N=69;
- extend witnesses and record structural statistics;
- independent verifier for every emitted witness.

Acceptance arithmetic: integers/rationals only.
Limits: 64 CPU workers, 192 GB RAM.

## 2026-07-12 exact engines

- solve_cpsat.py models unordered pairs a<=b, including diagonals. The only symmetry break is translation to min(A)=1. Status OPTIMAL is required for a finite optimum claim.
- verify_census.py is standard-library only; 13 self-tests include diagonal collisions and an exhaustive [1,8] subset cross-check.
- solve_bnb.cpp is an independent C++20 branch-and-bound with a fresh literal admissibility check and proof-complete/timeout distinction.

Verified results:

- CP-SAT certified N=1..55; all 55 values match OEIS A389182.
- Independent verifier accepted all 55 candidate records.
- Strict local rebuild of C++ BnB certified F(55)=12 and the new point F(70)=14.
- C++ BnB certified F(100)=16 in 229.875259 seconds using 32 threads and 221447050 nodes. A witness is {1,3,6,17,23,24,32,36,64,68,76,77,83,94,97,99}; its unique repeated sum is 100 with multiplicity 8, and it is reflection-closed about 100.

These finite values are discovery/falsification data only and do not imply the asymptotic theorem.


## 2026-07-12 OEIS extension

The independent C++ BnB returned proof-complete values at the endpoints

    F(70)=F(80)=14,
    F(81)=F(85)=15,
    F(86)=F(100)=16.

Since F is nondecreasing, these six endpoint equalities certify every term from N=70 through N=100. The proposed b-file is `compute/b389182_1_100.txt`; reproduction and submission text are in `compute/OEIS_SUBMISSION.md`. An independent line audit of the C++ proof search is still required before submission.
