from _bdef_construct import is_triangle_free
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _satzmu_conn import struct_for_side
from _h import maxcut_all, Bconn
from _codex_k2t_switch_signature_gate import terminal_shadow_details

names = ['v','u1','u2','u3','a1','a2','p1','p2','p3','b1','b2','b3','c1','c2','q1','q2','q3']
id = {x:i for i,x in enumerate(names)}
L = {'v','u1','u2','u3','a1','a2','p1','p2','p3'}
side = [0 if x in L else 1 for x in names]
B = []
def add(u,v): B.append((id[u], id[v]))
for i in [1,2,3]: add('v', f'b{i}')
for j in [1,2]:
    add('b1', f'a{j}'); add(f'a{j}', f'c{j}'); add(f'c{j}', f'u{j}')
for i in [1,2,3]:
    add(f'b{i}', f'p{i}'); add(f'p{i}', f'q{i}'); add(f'q{i}', 'u3')
M = [(id['v'],id['u1']), (id['v'],id['u2']), (id['v'],id['u3'])]
edges = B + M
n=len(names)
adj=adj_from_edges(n, edges)
print('n edges', n, len(edges), 'tri', is_triangle_free(n, edges), 'Bconn', Bconn(n, adj, side))
cut = sum(1 for u,v in edges if side[u]!=side[v])
mx = max(sum(1 for u,v in edges if s[u]!=s[v]) for s in maxcut_all(n, adj))
print('cut', cut, 'max', mx, 'num max sides', len(maxcut_all(n, adj)))
st=struct_for_side(n, adj, side)
print('st is None?', st is None)
if st:
    Mst, ell, T, mu, cyc = st
    print('Mst', [(names[u],names[v]) for u,v in Mst], 'ell', {tuple(names[x] for x in k):v for k,v in ell.items()})
    mask=1<<id['v']
    det=terminal_shadow_details(n, adj, side, st, mask)
    print('delta', boundary_delta(n, adj, side, mask), 'det', None if det is None else {k:det[k] for k in ['psi','cross_m','bdy_b','cross_lengths','lambda_lengths']})
    if det:
        for e,fs in sorted(det['witnesses'].items()): print('e', tuple(names[x] for x in e), 'fs', [tuple(names[x] for x in f) for f in set(fs)], 'rawcount', len(fs))
        e1=tuple(sorted((id['v'],id['b1'])))
        Y={e1}
        X={f for f in det['cross_m'] if set(det['witnesses_inv'][f]) <= Y} if False else None
