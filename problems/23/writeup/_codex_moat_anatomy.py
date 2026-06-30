"""Analyze one-vertex moat rescues for the widened selector."""

from _codex_bundle_moat_gate import brute_maxcut_sides, best_moat_completion, mask_tuple
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi
from _h import Bconn
from _satzmu_conn import struct_for_side


def edge(u, v):
    return (u, v) if u < v else (v, u)


def delta_parts(n, adj, side, seed, z):
    zmask = 1 << z
    full = seed | zmask
    b_seed = boundary_delta(n, adj, side, seed)
    b_z = boundary_delta(n, adj, side, zmask)
    b_full = boundary_delta(n, adj, side, full)
    internal_b = 0
    internal_m = 0
    for u in range(n):
        if not ((seed >> u) & 1):
            continue
        if z not in adj[u]:
            continue
        if side[u] == side[z]:
            internal_m += 1
        else:
            internal_b += 1
    return b_seed, b_z, b_full, internal_b, internal_m


def bconn_after(n, adj, side, mask):
    return Bconn(n, adj, flip_side(side, mask))


def main():
    n, edges, _ = h_blowup(2)
    adj = adj_from_edges(n, edges)
    best, sides = brute_maxcut_sides(n, adj)
    rows = []
    for side in sides:
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        R = residuals(n, adj, side)
        for v, r in enumerate(R):
            if r >= 0:
                continue
            for seed in length_bundle_half_switches(st[1], st[4], v):
                if not ((seed >> v) & 1):
                    continue
                cand = best_moat_completion(n, adj, side, st, seed, 1)
                if cand is None:
                    continue
                added, negpsi, full, psi = cand
                if added != 1:
                    continue
                z = next(i for i in range(n) if ((full >> i) & 1) and not ((seed >> i) & 1))
                psi_seed = terminal_shadow_psi(n, adj, side, st, seed)
                rows.append((
                    ''.join(map(str, side)), v, str(r), z,
                    mask_tuple(n, seed),
                    delta_parts(n, adj, side, seed, z),
                    bconn_after(n, adj, side, seed),
                    psi_seed,
                    psi,
                ))
                break
    print('rows', len(rows))
    for row in rows[:80]:
        print(row)


if __name__ == '__main__':
    main()
