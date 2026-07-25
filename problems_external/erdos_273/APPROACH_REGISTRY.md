# Erdős Problem 273 — Approach Registry

## Problem

Find a finite covering system of distinct congruences
\[
  a_i \pmod {m_i}\qquad(1\le i\le t)
\]
such that every integer belongs to at least one class and, for every \(i\),
\(m_i+1\) is a prime at least \(5\).

The current public page is `https://www.erdosproblems.com/273`.  On
2026-07-23 it reports OPEN, no claimed partial or complete solutions, no
comments, and no listed current workers.  Erdős and Graham record a nearby
construction due to Selfridge when the excluded prime \(3\) is allowed.

## DIRECT ROUTE A — finite covering certificate

1. **Exact final deliverable.**  A canonical list of pairwise distinct
   congruences \((a_i,m_i)\), primality certificates for every \(m_i+1\), and
   two independent exhaustive verifications that the classes cover all
   residues modulo \(\operatorname{lcm}(m_1,\ldots,m_t)\).

2. **Current frontier finite certificate.**  Find one assignment of one
   residue \(a_m\pmod m\) to each selected distinct modulus
   \(m\in\{p-1:p\ge5\text{ prime}\}\) whose union is all of \(\mathbb Z\).

3. **Logical bridge.**  Membership in a congruence class is periodic modulo
   the least common multiple \(L\).  Therefore coverage of all residues
   \(0,\ldots,L-1\), together with distinctness and the primality checks,
   is exactly a positive answer to Problem 273.

4. **Next falsifiable action.**  Implement a native exact-cover/SAT engine and
   two independently written verifiers.  First require it to reconstruct a
   cover from the \(m+1\) prime divisors of \(360\) when \(m=2\) is allowed
   (the Selfridge calibration).  Only after that audit may it search a fixed,
   predeclared \(p\ge5\) modulus family.

5. **Exit condition.**  Kill this computational lane if the Selfridge
   calibration fails, either verifier disagrees, or the first predeclared
   modulus family has reciprocal mass below \(1\) or is certified UNSAT.
   Such an exit is only a failure of this lane; it is not a negative solution
   of Problem 273, and it does not authorize an automatic cascade over larger
   least common multiples.

## Required audits

- The moduli are pairwise distinct and all exceed \(2\).
- Every \(m_i+1\) is proved prime, not merely reported probable prime.
- Exactly one residue is associated with each selected modulus.
- Coverage is checked on the full period \(L\), including residue \(0\).
- The certificate is replayed from the raw list by two independent parsers.
- A solver objective, lower bound, timeout, or bounded UNSAT instance is not
  a solution.


## Live-gate correction and fixed production family — 2026-07-23

The live forum has one comment, not zero. It reports a bounded BBMST exclusion for the 149 moduli with p <= 877 and explicitly leaves existence open. The first production family is fixed as L=55440 with all 43 divisors m >= 4 for which m+1 is prime. Its reciprocal mass is 1.04366883116883 and it contains p=55441. No larger L is authorised by this route.
