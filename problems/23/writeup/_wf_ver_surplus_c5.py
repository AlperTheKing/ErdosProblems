from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _stark1 import gmins

n, E = 5, [(0,1),(1,2),(2,3),(3,4),(4,0)]
adj, cuts = gmins(n, E)
for s in cuts[:1]:
    st = struct_for_side(n, adj, s)
    if st is None:
        print('no struct'); continue
    M, ell, T, mu, cyc = st
    N = F(n); beta = len(M); Gamma = sum(F(ell[f])**2 for f in M)
    V2 = sum((t-N)**2 for t in T); sumTTmN = sum(t*(t-N) for t in T)
    print('C5 t=1: M=', M, 'ell=', [ell[f] for f in M], 'Gamma=', Gamma, 'beta=', beta)
    print('  T=', [str(t) for t in T])
    print('  sum_v T=', sum(T), ' Gamma=', Gamma, ' handshake_ok=', sum(T) == Gamma)
    print('  identity V2+N(Gamma-NN)==sumTTmN :', V2+N*(Gamma-N*N) == sumTTmN, V2+N*(Gamma-N*N), sumTTmN)
    print('  N2/25-beta=', F(n*n,25)-beta, ' rhs=Gamma*(.)=', Gamma*(F(n*n,25)-beta))
