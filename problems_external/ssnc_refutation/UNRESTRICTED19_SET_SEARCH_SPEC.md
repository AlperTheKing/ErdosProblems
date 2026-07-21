# Independent unrestricted order-19 set-search prototype

Status: **CALIBRATED PROTOTYPE; NO PRODUCTION SEARCH RUN**.

This specification implements the registered UNRESTRICTED ORDER-19
STOCHASTIC REFUTATION route without importing search_local.cpp, its state
representation, or its score. The executable is
engine/search_unrestricted19_set.py.

## Direct deliverable and bridge

The only success artifact is a raw, canonical 19-row adjacency list for an
oriented graph with minimum outdegree at least eight such that, for every
vertex v,

|N++(v)| < |N+(v)|,

where the second neighbourhood is new-only:

N++(v) = {w != v : w notin N+(v), and some u has v -> u -> w}.

A hit is exposed only after the unchanged adjacency rows agree under the
set replay and a separate Boolean-matrix/triple-loop replay. Thus a verified
hit is directly the registered counterexample deliverable. A failed search
is only NO_HIT, never an UNSAT claim.

## Independent state representation

For every unordered pair {a,b}, a<b, the mutable state stores one trit:

- +1 means a -> b;
- -1 means b -> a;
- 0 means the pair is missing.

Consequently loops and digons are unrepresentable internally. Raw adjacency
parsing separately rejects loops, digons, duplicate targets, unsorted rows,
and out-of-range labels.

The search domain is not tied to a missing graph, degree sequence, incidence
system, symmetry class, or construction family. Its three legal mutations
are reversal of a present arc, deletion of a present arc, and either
orientation of a missing pair. A reversal or deletion is allowed only when
the old source has outdegree greater than eight. Therefore every accepted
mutation preserves minimum outdegree eight. Insertions always preserve it.

Writing q for the number of missing pairs, every state satisfies

sum_v (d+(v)-8) = 19-q,

so the invariant itself enforces 0 <= q <= 19; q is free to change during
the walk.

## Exact score

The search scorer converts the trits to direct Python sets. It unions the
out-neighbour sets of every direct middle vertex, then explicitly removes
the source and all direct out-neighbours. For row v, put

g_v = |N++(v)| - |N+(v)|.

Its contribution is zero if g_v<0, and 1+g_v^2 otherwise. Hence

E(D) = sum over v with g_v>=0 of (1+g_v^2)

is a nonnegative integer and

E(D)=0 iff |N++(v)|<|N+(v)| for every v.

The walk uses a deterministic-seed Metropolis rule with a linearly decreasing
temperature. Equal and improving moves are accepted; a rejected move is
reverted exactly at the pair-state level.

## Diverse deterministic starts

Every start begins with the cyclic 19-tournament and is then altered only by
legal pair transitions. The profiles are:

- regular: no preliminary reversal;
- skew: 11 deterministic-seed legal reversals;
- mixed: 97 deterministic-seed legal reversals.

Afterward exactly q legal arcs are deleted. Calibration covers

q in {0,3,7,12,16,19}

and all three profile types. Starts have exactly the requested q, minimum
outdegree eight, and total outdegree 171-q.

## Independent replay oracle

The final-boundary oracle does not use the trit scorer. It builds a Boolean
adjacency matrix directly from raw sorted rows and, for every ordered
source-target pair, checks all possible middle vertices with explicit nested
loops. It independently recomputes direct, new-second, and unreachable
sets, all row degrees, and strictness.

A raw hit is returned only if:

1. the trit state has minimum outdegree eight;
2. the set score is exactly zero;
3. the matrix oracle accepts the unchanged raw rows;
4. the two full ledgers agree; and
5. the matrix objective is also zero.

Non-hits return no adjacency list and no ledger.

## Calibration contract

The nonproduction command is:

    python engine/search_unrestricted19_set.py --calibrate --walk-steps 80

It performs:

- all 3^6=729 labelled oriented graphs on four vertices, comparing every
  set ledger with the matrix/triple-loop ledger;
- 500 deterministic mutation/revert checks;
- six bounded 80-step walks from the stated q and profile cases;
- exact validation of all initial missing counts, degree totals, and minimum
  degrees.

The unit suite additionally checks parser rejection, strict versus non-strict
inequality, the exact zero set of the score, deterministic replay, 500
successive domain-preserving mutations, insertion/deletion q accounting,
and the rule that a non-hit exposes no candidate.

The CLI deliberately has no production mode. Before any production run, an
independent final audit must review this source and its calibration artifacts.
