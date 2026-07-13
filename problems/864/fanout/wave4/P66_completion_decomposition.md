# P66: exact decomposition of the reflected-completion defect

## Setup

Let `A subset [0,L]` be admissible and let `sigma` be its unique repeated
unordered sum. Put

`P=A intersect (sigma-A)`, `R=A\P`,

`|P|=c=2p+delta`, `|R|=u`, with `delta in {0,1}`. Let `D=D^+(A)` and let
`D_P,D_R` be the disjoint supports of differences represented inside `P`
and by a pair touching `R`. Then

`|D_P|=p(p+delta)`,

`|D_R|=cu+binom(u,2)`.

For each unordered residual pair `i<=j`, put

`d_ij=|r_i+r_j-sigma|`.

Let `q_d` be the number of residual pairs with label `d`. Define

`v=sum_{d in D}q_d`,

`w=#{d notin D:q_d=2}`,

`a=#{d notin D:q_d=1}`,

and `h_D=L-|D|`. The P56 completion defect is `beta=v+w`.

## Lemma 1: virtual labels avoid core differences

For every `d in D_P`, one has `q_d=0`.

### Proof

Choose core points `x<y` with `y-x=d`. Since `P` is reflected about
`sigma/2`, the two values

`sigma+d=(sigma-x)+y`,

`sigma-d=x+(sigma-y)`

are unordered pair sums represented entirely inside `P`. If a residual pair
had folded label `d`, its sum would be one of `sigma-d,sigma+d`, giving a
second representation of a sum different from `sigma`. This contradicts
admissibility. Hence `q_d=0`.

In particular, every term counted by `v` lies on a label in `D_R`.

## Lemma 2: doubled missing labels are difference holes

One has `q_d<=2` for every `d`, and

`w<=h_D`.

### Proof

Every residual pair sum is different from `sigma`, since otherwise both
endpoints would belong to `P`. It also has a unique representation by
admissibility. For fixed `d>0`, the only possible residual pair sums are
`sigma-d` and `sigma+d`, so `q_d<=2`.

If `q_d=2`, both of these sums lie in `[0,2L]`. Therefore

`d<=min(sigma,2L-sigma)<=L`.

When also `d notin D`, this is a missing positive-difference label in
`[1,L]`. Distinct values of `d` give distinct holes, proving `w<=h_D`.

## Exact reduction

The virtual-pair count is

`binom(u+1,2)=v+a+2w`.

Also

`|D_R|-u=binom(u+1,2)+u(c-2)`

and the exact sum-hole identity is

`h_S=2h_D+|D_R|-u`.

Consequently

`2beta<=h_S`

is equivalent, after substituting `beta=v+w`, to the single inequality

`v<=a+u(c-2)+2h_D`.                                      (P66-main)

The stronger pair

`w<=h_D`,

`2v+w+u<=|D_R|+h_D`

also implies the target. Both statements have zero failures on all
30,899,206 residual cases of span at most 55. The first is Lemma 2; the
second, equivalently

`v-w<=a+u(c-2)+h_D`,

remains unproved.

## Exact gate

`compute/p66/decomposition_mixed_L55.json` records the complete span-55
census. It also shows why the earlier split was wrong: `2v<=|D_R|` fails
136 times, first for

`A={0,1,13,19,21,24,28,38}`,

where `(v,w,h_D,|D_R|)=(13,0,11,25)`.
