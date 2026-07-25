# Degree-seven to degree-eight extension audit

Status: exact method obstruction; no proof route is registered.

## Primary theorem chain

For a minimum-outdegree vertex s, write A=N+(s), B=N++(s), and choose a1 of minimum internal outdegree in A. Lemma 2.4 gives

|A1| <= ceil(delta/2)-1 and delta|A1| <= e(A) <= binom(delta,2).

Lemma 2.5 says that when |A| is odd and |A1|=(|A|-1)/2, D[A] is a regular tournament and |A2|=|A1|. Proposition 2.6 leaves only the middle values of |B|.

Primary source: https://arxiv.org/html/2606.30588v1#S2

## Exact obstruction at delta=8

At delta=7 and |A1|=3,

21 = 7*3 <= e(A) <= binom(7,2) = 21.

All inequalities are equalities, so D[A] is a regular tournament and Lemma 2.5 supplies three internal second neighbours. Theorems 3.1 and 4.1 use this structure.

At delta=8, Lemma 2.4 permits |A1|=3 but gives only

24 = 8*3 <= e(A) <= binom(8,2) = 28.

With m=28-e(A), the exact slack identity is

m + sum_{a in A}(d_A+(a)-3) = (28-e(A))+(e(A)-24) = 4.

The analogous defect at degree seven is zero. Since |A|=8 is even, Lemma 2.5 is also inapplicable. Regularity, tournament structure, and |A2|=3 no longer follow. The failure occurs already in the first surviving branch (|B|,|A1|)=(5,3).

The six surviving degree-eight branches are

(5,3), (6,2), (6,3), (7,1), (7,2), (7,3).

Sections 5 and 6 also hard-code degree seven in their residual systems and trimming equations, so their CP-SAT infeasibility logs do not transfer.

Sources:

- https://arxiv.org/html/2606.30588v1#S3
- https://arxiv.org/html/2606.30588v1#S4
- https://arxiv.org/html/2606.30588v1#S5
- https://arxiv.org/html/2606.30588v1#S6

## Theorem-closing status

A proof only for delta=8 would raise a finite threshold; it does not imply general SSNC. The paper contains no reduction of all counterexamples to degree eight and no parameter-uniform lemma for all delta>=8. Therefore direct substitution 7->8 is closed at the four-defect identity above. This is a proof-method obstruction, not a resolution of SSNC.
