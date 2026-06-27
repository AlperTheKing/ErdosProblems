import numpy as np
# Single-outlier Chebyshev: given N nonneg reals with fixed sum S (mean=S/N) and
# sum of squares E. Claim: max_i T_i <= mean + sqrt((N-1)/N * (E - S^2/N)).
# Verify by random sampling that this is a VALID upper bound (not just tight at balanced+1outlier).
rng = np.random.default_rng(0)
worst = -1e9
for _ in range(200000):
    N = rng.integers(3, 12)
    T = rng.random(N)**rng.integers(1,4)  # skewed
    S = T.sum(); mean = S/N; E = (T*T).sum()
    bound = mean + np.sqrt(max(0.0,(N-1)/N*(E - S*S/N)))
    gap = T.max() - bound          # must be <= 0
    if gap > worst: worst = gap
print("max (maxT - Chebyshev bound) over 200k random =", worst, "(should be <=0)")

# Now check the EQUIVALENCE used in code: maxT<=K  <==  E <= S^2/N + N/(N-1)*(K-mean)^2
# i.e. invert the Chebyshev bound. Confirm algebra: bound<=K  <=>  (N-1)/N*(E-S^2/N) <= (K-mean)^2
# <=>  E <= S^2/N + N/(N-1)*(K-mean)^2.  (only valid when K>=mean so RHS sqrt-arg sign ok)
