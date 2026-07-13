# Completion-charge question

Pure additive-combinatorics question for Erdos Problem 864. Please give one
complete proof or one explicit exact counterexample; do not give a survey.

Let A be a finite set of integers, translated so min(A)=0 and max(A)=L.
Unordered sums include diagonals. Assume exactly one sum value sigma has at
least two representations and every other unordered sum has at most one. Put

`P=A intersect (sigma-A)`, `R=A\P`,

`|P|=c=2p+delta`, with `delta in {0,1}`, and `|R|=u`.

Let D be the support of positive differences of A. Reflect the residual
virtually and set `F=A union (sigma-R)`. For each unordered pair `i<=j` from
R define the positive label

`d_ij=|r_i+r_j-sigma|`.

For `d>0` put `a_d=1` if `d in D` and
`q_d=#{i<=j:d_ij=d}`. Admissibility implies `q_d<=2`. Define

`beta=sum_d max(0,a_d+q_d-1)`.

Let h_S be the number of missing integer sum labels in `[0,2L]`. Exact
counting gives

`h_S=2L-[2p(p+delta)+cu+binom(u+1,2)]`.

Question: is `2 beta <= h_S` always true?

Evidence: exhaustive exact enumeration of every endpoint-normalized
admissible set with `L<=55` checked 35,776,005 sets and found no failure;
18,800,840 cases were outside the easy proved range `u<=2c-5`.

Useful exact reformulation. Let

`h_D=L-|D|`,

`D_R={positive differences having a representation touching R}`,

so `|D_R|=cu+binom(u,2)` and

`h_S=2h_D+|D_R|-u`.

Let

`v=sum_{d in D} q_d`,

`w=#{d notin D:q_d=2}`.

Then `beta=v+w`, so the target is

`2v+2w+u <= |D_R|+2h_D`.

Exact enumeration through `L<=22` found that

`2v<=|D_R|`, `v+u<=|D_R|`, `w<=h_D`

always hold, but these three alone do not algebraically imply the target.
The tempting companion `v+2w<=2h_D` is false for
`A={0,1,3,7,8}`, `sigma=8`. A natural matching through sums formed with
missing reflected points is also false for `A={0,1,3,6,10}` and
`A={0,4,6,7,12}`.

Please either:

1. prove `2beta<=h_S` by a concrete injection or double count that uses the
   full sum-uniqueness condition, with every step written out; or
2. give an explicit admissible counterexample and verify
   `sigma,P,R,beta,h_S` exactly.

Do not assume the desired inequality, and retain diagonal virtual pairs
`i=j`.
