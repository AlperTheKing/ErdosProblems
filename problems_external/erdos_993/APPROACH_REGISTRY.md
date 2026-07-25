# Erdős Problem 993 — Approach Registry

## Problem

For a finite graph G, let i_k(G) be the number of independent vertex sets of size k. Erdős Problem 993 asks whether the sequence (i_0(G),...,i_alpha(G)) is unimodal whenever G is a tree or a forest.

## Current status and novelty gate

- Live status checked on 2026-07-23: FALSIFIABLE / open.
- Exhaustive tree searches are public through order 29.
- A public bush-tree search produced 4,445 non-log-concave trees of order at most 60. Its reported forest search used only the 80 most extreme members.
- Audit found 54 distinct omitted polynomials from the published T_{3,m,n} and T*_{3,m,n} families. The frozen union has 4,499 entries.
- Any claimed hit must pass a fresh live novelty search before announcement.

## DIRECT ROUTE R1 — full-catalog forest-product refutation

1. **Exact final deliverable.** An explicit finite forest F, given by canonical component adjacency lists and graph encodings, whose exact independence sequence has indices a<b<c with i_a(F)>i_b(F)<i_c(F). Supply the full coefficient ledger and acceptance by two independently implemented exact verifiers.

2. **Current frontier finite certificate.** An unordered pair, allowing repetition, among the frozen union of 4,499 public bush and published-family non-log-concave tree polynomials whose exact product is nonunimodal. There are 4,499*4,500/2=10,122,750 pairs.

3. **Logical bridge.** Independence polynomials multiply under disjoint union: I(T1 disjoint-union T2;x)=I(T1;x)I(T2;x). Therefore a nonunimodal product gives an explicit forest counterexample and disproves the forest form of Problem 993. Since the statement asserts the property for every tree or forest, that certificate resolves the conjecture negatively.

4. **Next falsifiable action.** Freeze and hash the exact 4,499-entry union; independently reproduce its component polynomials, the two order-26 examples, and the published top-80 no-hit. After parser/verifier calibration, run an exact native C++ all-pairs product scan with direct valley detection. Recompute every raw hit from adjacency data using a separate tree-DP/product verifier and an independent forest deletion-recurrence verifier.

5. **Exit condition.** Stop immediately on a doubly verified explicit hit. If all 10,122,750 pairs are exact NO_HIT, record only that restricted catalog result and terminate R1. Do not cascade to triples, larger catalogs, or order-30 tree enumeration without a new audited direct bridge.

## Arithmetic and audit constraints

- Pair forests have at most 120 vertices, so every coefficient is below 2^120; unsigned __int128 arithmetic is exact.
- Check unimodality on the complete sequence including i_0=1, rejecting any later increase after the first strict decrease.
- Independently audit component identity, multiplicity, coefficient order, integer parsing, and convolution bounds.
- A bounded NO_HIT is not a proof of the conjecture.
