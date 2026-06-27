#!/usr/bin/env python3
"""AMI: sum_v max(0,T(v)-N) <= N^2-Gamma.  Full max-bound: max_v T(v) <= N+(N^2-Gamma).
Since max_v(T(v)-N) <= sum_v max(0,T(v)-N), AMI => max-bound TRIVIALLY (single term <= sum).
So AMI is at least as strong as the vertex-load theorem. Confirm, and also check the converse
(max-bound => AMI?) is FALSE in general (so AMI is STRICTLY stronger as a statement)."""
import numpy as np
rng=np.random.default_rng(1)
ami_implies_max_fail=0; max_holds_ami_fails=None
for _ in range(300000):
    N=rng.integers(5,12)
    T=rng.random(N)*rng.integers(1,3*N)
    Gamma=T.sum()
    ami = np.maximum(0.0,T-N).sum()
    maxb = T.max()
    AMI = ami <= N*N-Gamma+1e-9
    MAXB = maxb <= N+(N*N-Gamma)+1e-9
    if AMI and not MAXB: ami_implies_max_fail+=1
    if MAXB and not AMI and max_holds_ami_fails is None:
        max_holds_ami_fails=(N,round(Gamma,3),round(ami,3),round(N*N-Gamma,3))
print(f"AMI true but max-bound false: {ami_implies_max_fail}  (expect 0 => AMI => max-bound)")
print(f"max-bound true but AMI false witness: {max_holds_ami_fails}  (non-None => AMI strictly stronger)")
