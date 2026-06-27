import numpy as np
# Crux reality check: the exact identities (sumT=Gamma, sum(N-T)=N^2-Gamma) hold for ANY shortest-geodesic
# routing TRIVIALLY (h_e vertices per geodesic). They do NOT constrain the SPREAD at all.
# So AMI is NOT implied by the identities. Construct a load vector with the SAME sum but AMI VIOLATED:
rng=np.random.default_rng(1)
viol=0; ex=None
for _ in range(200000):
    N=int(rng.integers(6,30))
    # pick Gamma<=N^2 (so conjecture-consistent) but concentrate load to break 2O<=U
    G=int(rng.integers(N, N*N))  # Gamma in valid range
    # build T summing to G with one big spike
    T=np.zeros(N)
    spike=min(G, rng.uniform(N, 2*N))
    T[0]=spike
    rem=G-spike
    if rem<0: continue
    T[1:]=rem/(N-1)
    if abs(T.sum()-G)>1e-6: continue
    O=np.maximum(0,T-N).sum(); U=np.maximum(0,N-T).sum()
    if 2*O>U+1e-9:
        viol+=1
        if ex is None: ex=(N,G,round(spike,2),round(O,3),round(U,3))
print("AMI-violating load vectors with sumT=Gamma<=N^2:",viol,"/200000  example(N,G,spike,O,U)=",ex)
print("=> identities alone do NOT imply AMI; AMI needs the routing STRUCTURE (geodesic flatness from CD). Crux is real.")
