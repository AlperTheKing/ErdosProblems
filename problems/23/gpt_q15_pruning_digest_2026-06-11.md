# GPT Pro q=15 pruning digest

Date: 2026-06-11

Context: Erdos #23, target `a(30)=36`, low-codegree root route.

## Main upgrade

Root at a nonedge `xy` of minimum nonedge-codegree:

`t = |N(x) cap N(y)| = delta_2(G)`.

Then every nonedge in `G` has at least `t` common neighbours.  In the q=15
branch this forces:

`delta(G) >= 8`, `t=3`, `|C|=3`, `|A|=|B|=5`, `|R|=15`,
and therefore `delta_2(G)=3`.

This is certificate-safe because any q=15 branch after the low-codegree
reduction can be re-rooted at a minimum-codegree nonedge.  If the minimum
codegree is 1 or 2, the same graph moves to the smaller `t=1` or `t=2`
branch.

## Pure `(R,U_i)` lemmas to verify/implement

Let `C={c_1,c_2,c_3}` and `U_i=N_R(c_i)`.

1. `U_i` is independent, and every `r in R \ U_i` has at least 3 neighbours
   in `U_i`.

   Reason: `c_i r` is a nonedge with at least 3 common neighbours; those
   common neighbours must lie in `U_i`.

2. `|U_i| >= 6`.

   Reason: `deg(c_i)=2+|U_i| >= 8`.

3. `U_i cap U_j` is nonempty for `i != j`.

   Reason: `c_i c_j` is a nonedge.  It already has common neighbours `x,y`;
   minimum codegree 3 requires at least one more in `R`.

4. Type-count availability:

   If a vertex has label set `J` and `i notin J`, it needs three neighbours in
   `U_i`, and those neighbours can only have labels `K` with `i in K` and
   `K cap J = empty`.

5. Scalar q=15 feasibility:

   There must exist `15 <= p <= 25` such that

   - `p + e_R >= 37`;
   - `max(2*l(p), L_deg) <= 123 - p - U - e_R`,

   where

   `l(p)=max(45-U, 35-p, 34-e_R, 0)`,

   `L_deg=sum_r max(2(3-w(r)), 8-d_R(r)-w(r), 0)`.

6. Paired rooted-cut inequalities for every `W subset R`:

   `2*partial(W) <= e_R + 55 - U - p + 2*m(W)`,

   `2*partial(W) <= p + e_R + 49 - U + g(W)+g(R\W)`.

   These should be checked with the same existential `p`.

## Next certificate

Implement a pure `(R,U_i)` SAT/CEGAR filter before introducing A/B types:

- variables for the triangle-free graph `R`;
- variables for membership in `U_1,U_2,U_3`;
- hard constraints 1--4 above;
- model checker for scalar feasibility and paired rooted-cut inequalities.

If this pure layer kills q=15, run the same support-multiplicity framework on
the `t=2,q=14` extremal branch.  If not, pass surviving `(R,U_i)` patterns to
the A/B-type demand-cover ILP.

Status: GPT-derived, not yet fully verified.  Lemmas 1--3 are hand-checked;
the scalar and paired inequalities need independent local verifier checks.
