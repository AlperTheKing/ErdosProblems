# Exact global scoped-score optimizer

Files `optimizer.py` and `run.py` implement an integer-only row-choice schema,
literal semantic-row orbit quotient, exact active-component recomputation, and
complete terminal certificate/replay. The cut state is conservatively the full
choice prefix. The only global lower bound claimed is 0, valid because input
cost tables are checked nonnegative; stronger additive partial bounds are not
valid in general because later rows can deactivate a component.

Certificate format `exact-scoped-opt-v1` contains SHA-256 bindings for input and
quotient, raw-to-orbit maps, every quotient terminal score, lexicographically
first optimum, active/off-support/score-term decomposition, and lower-bound
name. Verification independently regenerates the canonical certificate.

R29's wall and handoff omit the 676 x 680 row database and canonical labels.
Aggregate counts do not determine intersections or component deactivation, so
an exact compressed 2943 instance cannot be reconstructed from the required
materials without inventing data.
