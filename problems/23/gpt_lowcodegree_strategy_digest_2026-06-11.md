# Erdos #23: GPT Pro low-codegree strategy digest

Date: 2026-06-11

Source: GPT Pro answer in ChatGPT conversation
`https://chatgpt.com/c/6a2a3a55-da90-83eb-8bbb-9d3a59eb942a`.

## Core recommendation

Do not attack `a(30)=36` by ordinary `C5`-blow-up stability.  After the BCL
high-density reduction, a hypothetical counterexample has `e <= 139`; any
`C5`-homomorphic graph has

`beta(G) <= min_i e(V_i,V_{i+1}) <= e(G)/5 < 37`.

Thus a counterexample must be outside the `C5`-homomorphic class.

The proposed structural reduction is:

1. maximalize the triangle-free graph;
2. use the Wang--Yang--Zhao common-degree theorem to get a nonedge `xy` with
   `1 <= |N(x) cap N(y)| <= 3`;
3. root at this low-codegree nonedge;
4. replace broad rooted 30-vertex SAT by a compressed finite certificate over
   the residual set `R`.

## Verified claim V10: low-codegree root exists in any counterexample

Let `G` be a 30-vertex triangle-free graph with `beta(G) >= 37`.  Greedily add
triangle-free edges until maximal triangle-free.  Adding an edge increases
`e(G)` by one and increases `maxcut(G)` by at most one, hence does not decrease
`beta(G)`.

The BCL high-density consequence still applies to the maximal supergraph:
if it had `e >= 140`, then `beta <= floor(30^2/25)=36`, contradiction.
So the maximalized counterexample has `e <= 139` and `beta >= 37`.

In a maximal triangle-free graph, every nonedge has at least one common
neighbour.  Therefore `delta_2 >= 1`, where

`delta_2(G) = min_{xy notin E(G)} |N(x) cap N(y)|`.

Wang--Yang--Zhao, arXiv:2408.05547, prove that every triangle-free graph with
minimum common degree greater than `floor(n/8)` is homomorphic to `C5`.
For `n=30`, `floor(n/8)=3`, so `delta_2 >= 4` implies `G -> C5`.

If `G -> C5`, deleting the least-populated consecutive class-link makes `G`
bipartite, hence `beta(G) <= e(G)/5 <= 139/5 < 37`, contradiction.

Thus any maximalized counterexample has a nonedge `xy` with

`1 <= |N(x) cap N(y)| <= 3`.

Status: VERIFIED, modulo the cited Wang--Yang--Zhao theorem.

## Verified claim V11: exact low-codegree root partition

Fix a maximal triangle-free counterexample and a nonedge `xy` with

`C = N(x) cap N(y)`, `t = |C| in {1,2,3}`.

Define:

- `A = N(x) \ C`;
- `B = N(y) \ C`;
- `R = V(G) \ ({x,y} union A union B union C)`;
- `a=|A|`, `b=|B|`, `q=|R|`.

Then:

- `a+b+q = 28-t`;
- `A union C` and `B union C` are independent;
- there are no `A-C` or `B-C` edges;
- every `a0 in A` has a neighbour in `B`;
- every `b0 in B` has a neighbour in `A`;
- every `r in R` has a neighbour in `A union C` and in `B union C`;
- for `a0 in A`, `b0 in B`,
  `a0b0 in E(G)` iff `N_R(a0) cap N_R(b0) = empty`;
- if `rr' in E(R)`, then `r,r'` have disjoint neighbourhoods inside each of
  `A`, `B`, and `C`.

These all follow directly from triangle-freeness and maximality.

If the rooted minimum degree is at least `r0`, then `a >= r0-t`,
`b >= r0-t`, and hence

`q <= 28 - 2*r0 + t`.

So in the previously hard branches:

- `r0=8`: `q <= 15`;
- `r0=9`: `q <= 13`.

Status: VERIFIED.

## Verified claim V12: two rooted cut formulae

For `r in R`, define

- `alpha_r = |N(r) cap A|`;
- `beta_r = |N(r) cap B|`.

For a spin assignment `s : R -> {0,1}`, let `E_R^=(s)` be the number of
`R-R` edges whose endpoints receive the same spin.  For `c in C`, let
`n_i(c,s)=|{r in R : rc in E, s(r)=i}|`.

### Opposite-root cut

Put `x,B,R_0` on side 0 and `y,A,R_1` on side 1, choosing each `c in C`
optimally.  The number of uncut edges is

`Psi(s) = E_R^=(s) + sum_{s(r)=0} beta_r + sum_{s(r)=1} alpha_r
          + sum_{c in C} (1 + min(n_0(c,s), n_1(c,s)))`.

Any counterexample must satisfy `min_s Psi(s) >= 37`.

### Same-root cut

Let `p=e(A,B)`.  Put `x,y,R_0` on side 0 and `A,B,R_1` on side 1, again
choosing each `c in C` optimally.  The number of uncut edges is

`Phi(s) = p + E_R^=(s) + sum_{s(r)=1} (alpha_r + beta_r)
          + sum_{c in C} min(2+n_0(c,s), n_1(c,s))`.

Any counterexample must satisfy `min_s Phi(s) >= 37`.

Status: VERIFIED by direct edge accounting.

## Pending finite certificate route

The proposed finite certificate enumerates:

- `t in {1,2,3}`;
- a triangle-free graph `R` on `q <= 28-2*r0+t` vertices;
- for each `c in C`, an independent set `U_c=N_R(c)`;
- integer variables `a_S`, `b_T` for independent subsets `S,T subset R`,
  counting vertices in `A` and `B` by their `R`-neighbourhood type.

It imposes:

- size and edge-count constraints;
- minimum-degree constraints;
- maximality-witness constraints for missing `A-R`, `B-R`, and `R-R` edges;
- all exact rooted cut inequalities `Psi(s) >= 37`, `Phi(s) >= 37`;
- deletion certificates from the known `a(25)=25` and McKay `a(23)=20`
  routes.

The clean missing lemma is:

> Low-codegree reducibility lemma.  In every maximal triangle-free
> 30-vertex graph with `e <= 139`, `beta >= 37`, and a nonedge `xy` with
> `1 <= |N(x) cap N(y)| <= 3`, either `min_s Psi(s) <= 36`, or
> `min_s Phi(s) <= 36`, or a deletion certificate exists.

This lemma plus V10 would prove `a(30)=36`.

Status: PENDING.  Needs either an analytic proof or a new compressed finite
certificate.

## Next action

Implement a local verifier for the low-codegree partition and rooted cut
formulae on concrete graphs, then build toward a compressed `R`-type
enumerator for the hard `r0=8,9` branches.
