# Independent C++ raw-adjacency audit contract

Status: **DUAL-COMPILER CALIBRATION PASS; NO PRODUCTION SEARCH RUN**.

The source engine/audit_unrestricted19_raw.cpp is independent of the
production stochastic engine. It accepts only a JSON object with two keys:

    {"n":19,"out_neighbors":[[...],...,[...]]}

Rows must be sorted and duplicate-free. The parser rejects missing or unknown
keys, wrong row counts, out-of-range labels, loops, and digons. Orders 1
through 63 are supported so that exhaustive small-order calibration uses the
same compiled code as order 19.

## Literal ledger

For each source v, the auditor constructs a 64-bit direct mask D_v. It then
forms the raw length-two reach mask by OR-ing D_u over every u in D_v and
defines the new second mask by deleting v and D_v. The remaining off-diagonal
vertices are the literal unreachable set. Thus the reported d1 and d2 are
exactly

    d1(v) = |N+(v)|,
    d2(v) = |{w != v : w notin N+(v), some u has v->u->w}|.

It also builds incoming masks independently and reports, for every ordered
pair (v,w), the exact number

    c(v,w) = |N+(v) intersect N-(w)|

of length-two witnesses.

## Two zero-equivalent energies

The exact row penalty is

    max(0, d2-d1+1).

For the smooth witness row energy, consider every eligible target w distinct
from v that is not a direct out-neighbor. Put

    need = max(0, n-2*d1),

sort the eligible counts c(v,w), and sum the `need` smallest counts. This is
the search energy published by the frozen stochastic engine. The auditor also
reports the redundant diagnostic

    witness_mass = sum over new-second w of c(v,w)(c(v,w)+1)/2.

Both quantities are positive exactly on non-strict rows. Therefore each
global sum is zero if and only if every vertex satisfies d2<d1. The sole
counterexample acceptance predicate additionally requires n=19 and minimum
outdegree at least eight. The smooth energy is search guidance;
it cannot itself bypass raw literal replay.

## Cross-calibration

The test engine/tests/test_audit_unrestricted19_raw.py sends JSON Lines to two
separately compiled binaries:

- GCC C++20 with -O2 -Wall -Wextra -Wpedantic -Werror;
- Clang C++20 with the same flags.

A Python-set reference independently reconstructs direct, second,
unreachable, and witness-count data. The calibration covers every labelled
oriented graph at each n from 1 through 4:

    1 + 3 + 27 + 729 = 760 states,

plus 19 deterministic order-19 states, one for every positive missing-pair
count q=1,...,19 and cycling through regular, skew, and mixed start profiles.
The two C++ binaries and the Python reference agree on all 779 full ledgers.

Adversarial controls reject loops, digons, duplicate and unsorted rows,
unknown or missing keys, bad row counts, and n outside the bit-mask range.
A redundant-witness fixture independently checks witness counts, triangular
witness mass, exact penalty, and smooth energy.

The auditor has no search or mutation code and cannot launch production.
