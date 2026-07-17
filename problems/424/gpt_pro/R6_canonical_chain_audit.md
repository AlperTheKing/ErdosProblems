# CX-R6 audit

Status: **exact reduction verified; theorem still open**.

The independent replay `R6_canonical_chain_audit.py` reconstructs the least
grounded closure, obstruction ranks, hard holes, canonical parents, and every
term in identities (3) and (4). It checks every pair `(X,d)` through the stated
limit. The remaining inequality (5) is deliberately not assumed.

The reduction is useful because it separates the two unpaid boundary types:
rank exits `R` and coordinate exits `C`. It does not supply the injection or
potential needed to dominate them by splitless roots `E`, seed-3 starts `J`,
and one dummy. Consequently R6 is not a proof of the ranked-prefix theorem and
does not close Problem 424.

