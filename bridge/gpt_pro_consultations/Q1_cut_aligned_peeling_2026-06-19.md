# GPT Pro consultation #1 — the exact Peeling Lemma for Erdős #23

Date: 2026-06-19. Status: **SENT** to GPT-5 Pro Extended ("Kapsamlı Pro").
Chat: https://chatgpt.com/c/6a35992e-d010-83eb-bfb9-4f2f73992720 ("Erdős Problem
23 Lemma", fresh chat — NOT Codex's). Browser 2 (local). Awaiting response; will
append the full reply + independent audit below when generation completes.
Prioritised questions (A) cut-extension >50% and (C) minimal-counterexample
structure. The exact text sent is the brief in §Questions below (4.4k chars).

## Background (self-contained)

For a triangle-free graph `G`, `beta(G) = e(G) - maxcut(G)` = min edges to delete
to make `G` bipartite. `a(N) = max beta` over triangle-free `G` on `N` vertices.
Erdős conjectured `a(N) <= N^2/25`; in particular `a(5n) <= n^2`, sharp via
`C5[n]` (balanced blow-up of C5, parts size n, `beta(C5[n]) = n^2`).

Known exact values (OEIS A389646 + this project): a(5)=1, a(10)=4, a(15)=9,
a(20)=16, a(25)=25, and (Step 1, being verified by exact enumeration) a(30)=36.
Note `a(5n)-a(5(n-1)) = 2n-1` with EQUALITY for every computed n=2..6.

We have a fully proved reduction: **IF**

> **(H2) Peeling Lemma.** For every n>=7 and every triangle-free G on 5n
> vertices, there exists S ⊆ V(G), |S|=5, with `beta(G) <= beta(G-S) + (2n-1)`.

**THEN** `a(5n) <= n^2` for all n (induction; base cases n<=6 from data/Step1;
telescoping `(n-1)^2+(2n-1)=n^2` is exact). We seek to prove (H2), or its weaker
sufficient forms:
- (H2') same but only for ONE beta-extremal G per n;
- (H2'') just `a(5n) <= a(5(n-1)) + 2n-1`.

## Exact claim to attack

(H2): for triangle-free G on 5n vertices (n>=7), some 5-set S has
`beta(G) - beta(G-S) <= 2n-1`. Equivalently `max_{|S|=5} beta(G-S) >= beta(G) - (2n-1)`.

## Verified facts

1. `beta(G-S) <= beta(G)` always (vertex deletion is monotone). So
   `pc(G):=min_{|S|=5}(beta(G)-beta(G-S)) >= 0`.
2. **Tightness.** For `G=C5[n]`, `S`=one vertex per part: `G-S=C5[n-1]`, so
   `pc = n^2-(n-1)^2 = 2n-1` exactly. Constant cannot be lowered to `2n-2`.
3. **Exhaustive n=2 (10 vertices, all 12172 triangle-free graphs):** `pc(G) <= 3`
   for ALL G (zero exceptions); the UNIQUE saturator `pc=3` is the UNIQUE
   beta-extremal graph `C5[2]`; every other graph has `pc <= 2`. Strongly
   suggests C5[n] is the unique binding case.
4. **Extension/upper bound (the only general handle).** For any S and any cut
   (A,B) of G that is optimal on `G-S`, `beta(G) <= beta(G-S) + mu(S)` where
   `mu(S)` = monochromatic edges incident to S in (A,B). Greedy placement gives
   `mu(S) <= floor(m(S)/2)`, `m(S)`=edges meeting S.

## The obstruction (smallest, precise)

On `C5[n]` the graph is `2n`-regular, so EVERY 5-set has `m(S) >= 10n - O(1)`;
the greedy half-cut therefore only yields `mu(S) >= 5n - O(1)`, i.e.
`beta(G) <= beta(G-S) + ~5n` — a factor ~2.5 too weak. YET the true increment is
`2n-1`, achieved because the OPTIMAL global cut of `C5[n]` (A=V0∪V2∪V4,
B=V1∪V3, the single mono super-edge V0×V4) puts the monochromatic mass entirely
on the two "bad parts": with S=one per part, vertices `s1,s2,s3` carry ZERO
mono edges and only `s0∈V0, s4∈V4` carry `2n-1` between them. So the optimal cut
cuts ~80% of the edges meeting S, not 50%.

**Therefore any proof must, for the chosen S, exhibit an optimal cut of `G-S`
(or `G`) in which the 5 removed vertices have almost-monochromatic
neighbourhoods (so they extend at cost <= 2n-1), beating the 50% greedy bound
using triangle-freeness + global cut structure.** We have no general mechanism
to (a) choose such S, or (b) certify mu(S) <= 2n-1, for arbitrary triangle-free
G. All single-vertex / min-degree peeling is local and gives only ~6.25n
increment (telescopes to ~3.1 n^2, worse than BCL's global N^2/23.5).

## Failed / non-competitive approaches

- Greedy half-cut, min-degree peel: rigorous but ~3.1 n^2 (Sec above).
- Naive Zykov/weighted symmetrization toward complete-multipartite: KILLS beta
  (extremal C5[n] is not complete multipartite), wrong extremal object.
- Restriction of the global optimal cut gives only `Delta >= mu(S)` (lower
  bound on the increment), the wrong direction.

## Questions for you

1. **Cut-extension lemma.** Is there a structural condition on a 5-set S in a
   triangle-free graph G (e.g. "each N(s_i) is within `<= t` of being
   monochromatic in some fixed maxcut of G-S") that guarantees an extension with
   `mu(S) <= 2n-1`, AND a counting/averaging argument that such an S always
   exists? Concretely: can one always find 5 vertices whose neighbourhoods are
   simultaneously near-monochromatic in a common near-optimal cut?
2. **Exact stability.** Is there an exact stability theorem of the form
   `beta(G) >= n^2 - t ⟹ G is within edit distance g(t) of C5[n]` with `g`
   explicit (BCL give approximate o(n^2) stability via flag algebras)? Enough to
   run a finite exact cleanup for the inductive step?
3. **Minimal-counterexample structure.** For a minimal counterexample G (min n,
   then min edges, beta = a(5n) >= n^2+1, a(5(n-1)) <= (n-1)^2): what high-min-
   degree / connectivity / no-light-separator properties are forced, and do they
   supply the alignment needed to pick S and bound mu(S) <= 2n-1?
4. **Weighted route done right.** A C5-structure-preserving symmetrization on
   vertex-weighted triangle-free graphs whose extremal object is weighted C5,
   with a proven unweighted conversion at the exact constant.
5. **Honest scope.** Is (H2) (equivalently the exact constant 1/25 in the
   medium-density regime) within reach of current methods, or should we instead
   target a proved partial constant strictly better than 1/23.5 toward 1/25?

## Audit plan

Every suggested lemma will be (a) checked on C5[n] for exact constants, (b)
stress-tested against the n=2 exhaustive data and targeted n=3,4 structured
graphs, (c) checked for the >50%-extraction obstruction above before adoption.
