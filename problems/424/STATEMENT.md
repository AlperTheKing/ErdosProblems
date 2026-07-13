# Erdos Problem 424

Start with a_1 = 2, a_2 = 3. Repeatedly extend the sequence by appending ALL
possible values a_i * a_j - 1 with i != j (each new element joins the pool and
can be used in later products).

Equivalently (frozen convention, matching FormalConjectures/ErdosProblems/424.lean):

    A_0 = {2, 3}
    A_{n+1} = A_n  union  { x*y - 1 : x, y in A_n, x != y }
    G = union_n A_n   (the set of integers that eventually appear)

QUESTION (open, either direction): does G have positive (natural) density?

- Proof side: show d_lower(G) > 0 (or full density statement).
- Disproof side: show d(G) = 0 (or upper density 0), machine-checkable argument.

First elements: 2, 3, 5, 9, 14, 17, 26, 27, 33, ... (OEIS A5244).

Official source: https://www.erdosproblems.com/424
OEIS: https://oeis.org/A5244
Also: Ben Green, Open Problem 63 (open-problems list).
Formalization target: formal-conjectures FormalConjectures/ErdosProblems/424.lean
(erdos_424 : answer(sorry) <-> generatedSet.HasPosDensity).

Conventions frozen 2026-07-12: x != y refers to DISTINCT INDICES in the original
phrasing; the FC set-based formalization uses distinct VALUES (x != y as numbers).
Any proof intended for the FC PR must match the FC semantics (distinct values);
note 2*2-1 etc. are excluded in both readings for the initial segment since
duplicates only arise if a value repeats, which sets ignore. If a semantic gap
between "distinct indices" and "distinct values" ever becomes load-bearing,
surface it immediately (it changes the generated set).
