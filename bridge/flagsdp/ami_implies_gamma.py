#!/usr/bin/env python3
"""Check: does AMI  [ sum_v max(0,T(v)-N) <= N^2 - Gamma ]  imply Gamma <= N^2,
given the identity sum_v T(v) = Gamma?  And is AMI strictly weaker than the full
vertex-load bound max_v T(v) <= N + (N^2-Gamma)?  Verify the algebra symbolically-numerically.

Derivation under test:
  Let P={v:T(v)>N}, |P|=p.  sum_{v in P}(T(v)-N) <= N^2-Gamma  (AMI).
  Gamma = sum_v T(v) = sum_{P}T + sum_{Q}T <= [N p + (N^2-Gamma)] + N(N-p) = N^2 + N^2 - Gamma.
  => 2 Gamma <= 2 N^2 => Gamma <= N^2.   (independent of which routing, as long as AMI holds.)

We confirm on random nonneg vectors T with sum=Gamma satisfying AMI that Gamma<=N^2 always,
and we look for a vector T (sum=Gamma) that satisfies AMI but VIOLATES the full max-bound, to
confirm AMI is STRICTLY WEAKER (so an aggregation proving only AMI would still suffice for #23,
but would not reprove the full GPI)."""
import numpy as np
rng=np.random.default_rng(0)
viol=0; weaker_witness=None
for trial in range(200000):
    N=rng.integers(5,12)
    # random nonneg T
    T=rng.random(N)*rng.integers(1,3*N)
    Gamma=T.sum()
    ami = np.maximum(0.0,T-N).sum()
    if ami <= N*N - Gamma + 1e-9:   # AMI satisfied
        if Gamma > N*N + 1e-6:
            viol+=1
        # is full max-bound violated while AMI holds?
        if T.max() > N + (N*N-Gamma) + 1e-6 and weaker_witness is None:
            weaker_witness=(N,round(Gamma,3),round(T.max(),3),round(N+(N*N-Gamma),3))
print(f"AMI-satisfying random vectors: Gamma>N^2 violations = {viol}  (expect 0 => AMI => Gamma<=N^2)")
print(f"AMI-holds-but-full-max-bound-violated witness = {weaker_witness}  (non-None => AMI strictly weaker than full GPI)")
