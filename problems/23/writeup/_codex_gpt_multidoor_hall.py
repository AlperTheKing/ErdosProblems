from _codex_gpt_multidoor_check import names,id,side,adj,n
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary, mask_tuple

st=struct_for_side(n, adj, side); M, ell, T, mu, cyc=st; mask=1<<id['v']; det=terminal_shadow_details(n, adj, side, st, mask)
wit_of_f={f:set() for f in det['cross_m']}
for e,fs in det['witnesses'].items():
    for f in fs: wit_of_f[f].add(e)
print('wit_of_f', {tuple(names[x] for x in f): [tuple(names[y] for y in e) for e in sorted(es)] for f,es in wit_of_f.items()})
Y={tuple(sorted((id['v'],id['b1'])))}; t=6
X={f for f in det['cross_m'] if ell[f]<t and wit_of_f[f] <= Y}
print('Y', [tuple(names[y] for y in e) for e in Y], 'X', [tuple(names[x] for x in f) for f in X], 'sizes', len(Y), len(X))
prefixes={}
for f in det['cross_m']:
    prefixes[f]=crossing_prefixes(mask, f, cyc[f])
mask_u=0
for f in X:
    for e in wit_of_f[f]:
        for pm in prefixes[f].get(e,()): mask_u |= pm
bdu,mdu=edge_boundary(n, adj, side, mask_u)
print('U', [names[i] for i in mask_tuple(n, mask_u)])
print('Bextra', [tuple(names[i] for i in e) for e in sorted(bdu-Y)], 'Mextra', [tuple(names[i] for i in e) for e in sorted(mdu-X)])
print('side-door inequality', len(bdu-Y), '<=', len(mdu-X))
