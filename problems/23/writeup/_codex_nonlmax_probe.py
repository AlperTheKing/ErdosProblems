from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, gamma_of, residuals
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _h import Bconn

n, edges, _ = h_blowup(2)
adj = adj_from_edges(n, edges)
side = [int(c) for c in '011111111111000000']
st = struct_for_side(n, adj, side)
M, ell, T, mu, cyc = st
seed = sum(1<<i for i in (2,12,13))
S = sum(1<<i for i in (1,2,12,13))
for name, mask in [('seed', seed), ('S', S)]:
    det = terminal_shadow_details(n, adj, side, st, mask)
    print(name, 'delta', boundary_delta(n, adj, side, mask), 'Bconn2', Bconn(n, adj, flip_side(side, mask)), 'gamma2', gamma_of(n, adj, flip_side(side, mask)))
    print('det', None if det is None else {k:det[k] for k in ['psi','cross_lengths','lambda_lengths','cross_m','bdy_b']})
    if det:
        for e, fs in sorted(det['witnesses'].items()): print(' ', e, 'lam', min(ell[f] for f in fs), 'fs', fs)
print('R2', residuals(n, adj, side)[2])
print('bad lengths', {f:ell[f] for f in M})
