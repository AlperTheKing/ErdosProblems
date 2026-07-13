# Exact certificate schema

For relation `R` on demands `D` and sources `S`, the maximum fractional matching LP has variables `x[d,s]>=0`, demand and source sums at most one, and objective `sum x`. Its rational dual minimizes `sum a[d]+sum b[s]` subject to nonnegative weights and `a[d]+b[s]>=1` on every edge.

Here `R(d,s)` depends on `d` only through `owner(d)`. For owners `U`, put `A={d: owner(d) in U}` and `N=N(A)`. The canonical integral dual is `a=0` on A and 1 off A, and `b=1` on N and 0 off N. Its objective is `|D|-|A|+|N|`; it is strict exactly when `|A|>|N|`.

If any demand set A0 is deficient, saturating it to all demands whose owner occurs in A0 leaves its neighborhood unchanged and cannot decrease its size. Thus owner shores are complete. `check_dual.py` reconstructs this 0/1 dual, checks every constraint, and parses all supplied numbers with Fraction.