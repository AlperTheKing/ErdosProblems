# Literature audit

## Authoritative formulations

- P. Erdos, *Problems and results on combinatorial number theory III*,
  Number Theory Day (1977), pp. 43--72, asks the positive-density question
  attributed to Hofstadter. Full primary-source hypothesis audit is pending.
- P. Erdos and R. Graham, *Old and New Problems and Results in
  Combinatorial Number Theory* (1980), p. 84. The later ``almost all''
  wording cannot be true because the closure omits every integer congruent
  to 1 modulo 3.
- R. K. Guy, *Unsolved Problems in Number Theory*, problem E31.
- B. Green, *100 Open Problems*, problem 63, states the least set containing
  2 and 3 and closed under `a1*a2-1`, and says the answer is probably yes.
- OEIS [A005244](https://oeis.org/A005244) records the increasing sequence
  and a b-file through 10,000 terms.
- T. F. Bloom, [Erdos Problem 424](https://www.erdosproblems.com/424),
  records the distinct-input convention `i != j` and the open status.

## Precise working statement

Let `A` be the least subset of the positive integers containing 2 and 3 and
satisfying `xy-1 in A` for every pair of distinct `x,y in A`. Determine
whether

    liminf_{X -> infinity} |A intersect [1,X]| / X > 0.

No complete or partial solution is currently accepted here. The novelty
search remains open until the wave-1 primary-source reports are audited.

