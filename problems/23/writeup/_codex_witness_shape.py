"""Shape statistics for completed-switch terminal witness graphs."""

from collections import Counter, defaultdict

from _h import Bconn
from _satzmu_conn import struct_for_side
from _codex_bundle_moat_gate import brute_maxcut_sides, best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, residuals
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def components(det):
    cross = list(det['cross_m'])
    exits = list(det['bdy_b'])
    adj = defaultdict(set)
    for e, fs in det['witnesses'].items():
        for f in fs:
            adj[('F', f)].add(('E', e))
            adj[('E', e)].add(('F', f))
    seen = set()
    comps = []
    for node in [('F', f) for f in cross] + [('E', e) for e in exits]:
        if node in seen:
            continue
        stack = [node]
        seen.add(node)
        comp = []
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(comp)
    return comps, adj


def main():
    n, edges, _ = h_blowup(2)
    adjg = adj_from_edges(n, edges)
    _best, sides = brute_maxcut_sides(n, adjg)
    comp_hist = Counter()
    degree_hist = Counter()
    edge_count_hist = Counter()
    all_comp_examples = []
    switches = 0
    for side in sides:
        if not Bconn(n, adjg, side):
            continue
        st = struct_for_side(n, adjg, side)
        if st is None:
            continue
        R = residuals(n, adjg, side)
        for v, r in enumerate(R):
            if r >= 0:
                continue
            best = None
            for seed in length_bundle_half_switches(st[1], st[4], v):
                if not ((seed >> v) & 1):
                    continue
                cand = best_moat_completion(n, adjg, side, st, seed, 1)
                if cand is None:
                    continue
                if best is None or cand < best:
                    best = (seed, cand)
            if best is None:
                continue
            seed, (added, _negpsi, mask, psi) = best
            det = terminal_shadow_details(n, adjg, side, st, mask)
            comps, wadj = components(det)
            switches += 1
            for comp in comps:
                fs = [x[1] for x in comp if x[0] == 'F']
                es = [x[1] for x in comp if x[0] == 'E']
                m = sum(1 for f in fs for e in es if ('E', e) in wadj[('F', f)])
                comp_hist[(len(fs), len(es), m)] += 1
                degs_f = tuple(sorted(len(wadj[('F', f)]) for f in fs))
                degs_e = tuple(sorted(len(wadj[('E', e)]) for e in es))
                degree_hist[(degs_f, degs_e)] += 1
                if len(all_comp_examples) < 20:
                    all_comp_examples.append(( ''.join(map(str, side)), v, added, psi, len(fs), len(es), m, degs_f, degs_e, fs, es))
    print('switches', switches)
    print('component hist')
    for k, c in comp_hist.most_common():
        print(c, k)
    print('degree hist')
    for k, c in degree_hist.most_common(20):
        print(c, k)
    print('examples')
    for ex in all_comp_examples:
        print(ex)


if __name__ == '__main__':
    main()
