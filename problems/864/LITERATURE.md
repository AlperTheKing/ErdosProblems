# Literature

Status frozen: 2026-07-12. Initial novelty gate complete; repeat before release.

## Primary sources

1. P. Erdos and R. Freud, "On sums of a Sidon-sequence", Journal of Number
   Theory 38 (1991), 196-205.
   DOI: https://doi.org/10.1016/0022-314X(91)90083-N

2. P. Erdos, "Some of my Forgotten Problems in Number Theory",
   Hardy-Ramanujan Journal 15 (1992).
   Record: https://hal.science/hal-01108666/

3. T. F. Bloom, Erdos Problem #864.
   https://www.erdosproblems.com/864

4. OEIS A389182, exact values through N=69.
   https://oeis.org/A389182

5. Exact-extremizer computation discussion:
   https://github.com/teorth/erdosproblems/issues/143

## Verified baselines

- Erdos-Freud lower bound:
  F(N) >= (2/sqrt(3)+o(1))sqrt(N), using B union (N-B) for a Sidon
  B subseteq [1,N/3].

- Elementary split upper bound:
  F(N) <= (sqrt(2)+o(1))sqrt(N).
  If s is the exceptional sum, splitting at s/2 gives two genuine Sidon
  pieces; parity and boundary details still need a written local proof.

- No complete or partial solution is claimed on the official page as of
  2026-07-12.

## Search terms in flight

Sidon set with one exception; almost Sidon; near-Sidon; one repeated sum;
B_2 exceptional representation; restricted additive energy; Sidon stability;
Erdos Problem 840.

Every theorem added here must record its exact hypotheses, constant, and
whether it actually applies to unordered sums with diagonal pairs.

## New exact terminology found during the gate

Forey-Fresan-Kowalski define symmetric Sidon sets; a 2025 preprint on
spectrally indistinguishable pseudorandom graphs defines a partial symmetric
Sidon set with center s by the exact rule

    a+b=c+d implies {a,b}={c,d} or a+b=c+d=s.

Thus every admissible set in Problem 864 is exactly a partial symmetric Sidon
set in Z, with the no-exception case treated as ordinary Sidon.

Primary sources:

- A. Forey, J. Fresan, E. Kowalski, "Sidon sets in algebraic geometry",
  IMRN 2024, arXiv:2301.12878.
- "Spectrally indistinguishable pseudorandom graphs", 2025 preprint,
  Proposition 3.1: the Cayley sum graph of a partial symmetric Sidon set is
  K_{2,3}-free.

No interval-size theorem with the 2/sqrt(3) constant was found in these
sources. The terminology and K_{2,3}-free encoding are relevant attack
surfaces, not a prior resolution.

## Independent novelty verdict

Lanes L04 and L06 independently audited Sidon stability, Problem 840, diagonal conventions, and Pikhurko 2006. No proved theorem forces reflected two-block structure; the transferred quasi-Sidon constant 1.863 is weaker than sqrt(2). The primary-source sweep found no theorem below sqrt(2) for #864. Exact prior terminology is partial symmetric Sidon set, whose Cayley sum graph is K_{2,3}-free. Details: fanout/wave1/L04.md and L06.md.


## Atkinson-Santoro-Urrutia audit

M. D. Atkinson, N. Santoro, and J. Urrutia, "Integer Sets with Distinct Sums and Differences and Carrier Frequency Assignments for Nonlinear Repeaters," IEEE Trans. Commun. 34 (1986), 614-617, DOI 10.1109/TCOM.1986.1096587, treats ordinary distinct-difference sets (Golomb rulers). Its Section II observes the standard equivalence between uniqueness of off-diagonal pair sums and uniqueness of nonzero differences, and proves the optimal span is asymptotic to the square of the number of gaps. It does not require pair sums and positive differences to be mutually disjoint, and it does not allow one arbitrary exceptional sum fibre. Thus it is relevant background for the fully reflected signed-ruler reduction, but it neither resolves that stronger subproblem nor Problem 864.

## Strong 4-independence and Sidon diameter

B. Bajnok and I. Z. Ruzsa, "The independence number of a subset of an
abelian group," Integers 3 (2003), A02, arXiv:1512.03037, define strong
independence with arbitrary integer coefficients, so repeated summands are
included. Their Corollary 14 proves

    s(Z_n,4) <= (1/sqrt(2)+o(1))*sqrt(n).

The value `1/sqrt(3)` is Conjecture 15, not a theorem. Moreover, the valid
integer set `{1,7,11}` is not Sidon modulo 12 because
`1+1 = 7+7 (mod 12)`, so reduction modulo `max(E)+1` cannot transfer the
conjectural cyclic result to the interval problem.

D. Carter, Z. Hunter, and K. O'Bryant, "On the diameter of finite Sidon
sets," Acta Math. Hungar. 175 (2025), 108--126, arXiv:2310.20032, prove

    diam(Z) >= p^2 - 1.96365*p^(3/2) - O(p).

For a same-parity target set this yields only
`max(E) >= (2-o(1))p^2`. The theorem does not use the additional exclusion
between positive differences and pair sums. Full audit: P49.
