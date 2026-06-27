import numpy as np
# Adversarial check of the strategy's algebraic claims:
# CLAIM A: AMI (sum max(0,T-N) <= N^2-Gamma) with sum T = Gamma  =>  max_v T(v) <= N+(N^2-Gamma).
#   single term <= sum of overloads <= N^2-Gamma, so T(v)-N<=N^2-Gamma => T(v)<=N+(N^2-Gamma). TRUE trivially.
# CLAIM B: AMI => Gamma <= N^2.  Partition P={T>N},Q. Gamma=sumT = sum_P T + sum_Q T
#   <= [N|P| + (N^2-Gamma)] + N|Q| = N*N + (N^2-Gamma) = 2N^2-Gamma => 2Gamma<=2N^2 => Gamma<=N^2. TRUE.
# So AMI (at a routing) => both. But CRUX: does AMI need to hold at the SAME routing whose maxT we bound?
# The vertex-load theorem only needs EXISTENCE of a routing with maxT<=K. AMI is sufficient *if* it holds
# for SOME routing. The strategy verifies AMI for the UNIFORM routing. Good enough? YES for Gamma<=N^2
# (claim B uses only sumT=Gamma + AMI, both hold for uniform). So uniform-AMI => Gamma<=N^2 alone.
# => The ENTIRE conjecture (S=V GPI) reduces to: uniform-routing AMI.  That is the real target.
rng=np.random.default_rng(0)
bad=0
for _ in range(500000):
    N=rng.integers(5,40); 
    T=rng.uniform(0,2.0,size=N)*N   # random load vector
    # enforce sumT = Gamma with Gamma free; test the IMPLICATION not AMI itself
    G=T.sum()
    O=np.maximum(0,T-N).sum(); 
    # if AMI holds (O<=N^2-G) does Gamma<=N^2?
    if O<=N*N-G+1e-9:
        if G>N*N+1e-6: bad+=1
print("CLAIM B counterexamples (AMI true but Gamma>N^2):",bad,"/500000")
