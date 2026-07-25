"""H2_validate.py -- cross-check the fast numpy evaluator against the exact
reference implementation of H2_core (second independent implementation)."""
import numpy as np
from fractions import Fraction
from H2_core import edges, arcbound, arcbound_fast, total_W
from H2_opt import make, all_F, arcbound_np

rng = np.random.default_rng(12345)
bad = 0
for trial in range(400):
    m = int(rng.integers(5, 34))
    w = rng.integers(0, 6, size=m)
    if w.sum() == 0:
        continue
    E = edges(m)
    exact_ref = arcbound(list(int(t) for t in w), E, m)      # O(m^2 |E|) reference
    exact_fast = arcbound_fast(list(int(t) for t in w), E, m)  # incremental exact
    a, b = make(m)
    num = arcbound_np(w.astype(float), m, a, b)
    if exact_ref != exact_fast or abs(num - exact_ref) > 1e-7 * max(1, abs(exact_ref)):
        bad += 1
        print("MISMATCH", m, list(w), exact_ref, exact_fast, num)
print(f"validated 400 random cases, mismatches = {bad}")

# also check W and the reported ARCBOUND on the named uniform cases
for m in [5, 8, 11, 14, 17, 20, 23, 25, 29]:
    E = edges(m)
    w = [1] * m
    a, b = make(m)
    print(m, arcbound_fast(w, E, m), arcbound_np(np.ones(m), m, a, b), total_W(w, E))
