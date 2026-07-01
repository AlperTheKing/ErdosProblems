"""Claude INDEPENDENT exact cross-gate of Codex's NO-TWO-HOLE RESIDUAL CORRIDOR lemma (18:41Z):
for every residual component (A,B) and every f in A, f misses at most one exit e in B (row_miss<=1).

Independence: cross_m/bdy_b/witnesses come from MY from-scratch witness_structure (_pl_gate); only the
stage0 matching (min_cost_stage0) and residual components are Codex's shared algorithm. Tests BOTH the raw
find_seedmoat switch AND the inclusion-minimalized switch.

Battery (exhaustive, ultracode): census N<=11, H-blowups t=2 allmax + t=3..6 inherited, Mycielski chain
(C5 / Grotzsch / Myc(Grotzsch) N=23 apex), glued islands (gmin), and RANDOM triangle-free N=12..16 with R[v]<0.
Reports row_miss histogram + the FIRST two-hole counterexample (row_miss>=2) if any. EXACT counts.
Run from E:/Projects/ErdosProblems/problems/23/writeup."""
import sys, subprocess, random
from collections import Counter
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all, loads
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components
from _codex_minimalized_sidecap_gate import minimalize
from _codex_selected_minimality_gate import mask_of, vertices_of
from _codex_k2t_switch_probe import adj_from_edges
from _bdef_construct import Cn, mycielski, union_disjoint, add_edges, is_triangle_free, blow_g


def check_switch(name, n, adj, side, st, Sset, acc, tag):
    M, ell, T, mu, cyc = st
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        acc['no_wit'] += 1
        return
    crossM, bdyB, wit = res
    Fedges = tuple(sorted(crossM)); Eedges = tuple(sorted(bdyB))
    if not Fedges or len(Fedges) != len(Eedges):
        acc['skip_unbalanced'] += 1
        return
    witnesses = {}
    for (f, e) in wit:
        witnesses.setdefault(e, set()).add(f)
    for e in Eedges:
        witnesses.setdefault(e, set())
    if any(not witnesses[e] for e in Eedges):
        acc['skip_emptywit'] += 1
        return
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in Eedges}
    min_len = min(ell[f] for f in Fedges)
    min_lam = min(lamb.values())
    F0 = tuple(f for f in Fedges if ell[f] == min_len)
    F1 = tuple(f for f in Fedges if ell[f] > min_len)
    if not F1:
        acc['skip_no_F1'] += 1
        return
    E0 = tuple(e for e in Eedges if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        acc['stage0_none'] += 1
        return
    rem = tuple(e for e in Eedges if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    acc['tested'] += 1
    for cl, cr in components(F1, rem, adj1):
        cr = tuple(cr)
        for f in cl:
            misses = [e for e in cr if e not in adj1[f]]
            acc['row_miss'][len(misses)] += 1
            if len(misses) >= 2:
                acc['two_hole'] += 1
                if acc['first'] is None:
                    acc['first'] = dict(name=name, tag=tag, n=n, side=''.join(map(str, side)),
                                        S=sorted(Sset), f=f, misses=misses, cr=cr)


def process_cut(name, n, adj, side, acc, max_add=1):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    K2 = build_K2(n, M, cyc)
    R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=max_add)
        if got is None:
            continue
        seed, moat, _drop = got
        smask0 = mask_of(set(seed) | set(moat))
        check_switch(name, n, adj, side, st, set(vertices_of(smask0, n)), acc, 'raw')
        smask = minimalize(n, adj, side, st, gamma0, smask0, v)
        check_switch(name, n, adj, side, st, set(vertices_of(smask, n)), acc, 'min')


def process_allmax(name, n, edges, acc, max_add=1):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        process_cut(name, n, adj, side, acc, max_add)


def process_gmin(name, n, edges, acc, max_add=1):
    info = loads(n, edges)
    if info is None:
        return
    process_cut(name, n, info['adj'], info['side'], acc, max_add)


def rand_trifree(n, rng):
    """A random maximal-ish triangle-free graph on n vertices."""
    adj = [set() for _ in range(n)]
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    rng.shuffle(pairs)
    E = []
    for a, b in pairs:
        if adj[a] & adj[b]:
            continue  # would create triangle
        adj[a].add(b); adj[b].add(a); E.append((a, b))
    return n, E


def new_acc():
    return dict(tested=0, no_wit=0, skip_unbalanced=0, skip_emptywit=0, skip_no_F1=0,
                stage0_none=0, two_hole=0, row_miss=Counter(), first=None)


def report(label, acc):
    print('=' * 64)
    print('BATTERY:', label)
    print('switches tested:', acc['tested'], '| no_wit:', acc['no_wit'],
          'skip_unbal:', acc['skip_unbalanced'], 'skip_emptywit:', acc['skip_emptywit'],
          'skip_no_F1:', acc['skip_no_F1'], 'stage0_none:', acc['stage0_none'])
    print('row_miss histogram:', sorted(acc['row_miss'].items()))
    print('TWO-HOLE rows:', acc['two_hole'], '| first:', acc['first'] or 'NONE')
    print('VERDICT:', 'NO-TWO-HOLE HOLDS' if acc['two_hole'] == 0 and acc['tested'] > 0 else
          ('FAIL -- two-hole found' if acc['two_hole'] else 'no switches tested'), flush=True)


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if phase in ('census', 'all'):
        acc = new_acc()
        for nn in range(5, 12):
            for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
                n, E = dec(g6); process_allmax('cen%d' % nn, n, E, acc)
            print('  census N=%d done: tested=%d two_hole=%d' % (nn, acc['tested'], acc['two_hole']), flush=True)
        report('CENSUS N<=11 (raw+min switches)', acc)

    if phase in ('h2only', 'hblow', 'all'):
        acc = new_acc()
        n, E = vertex_blowup(*dec('H?AFBo]'), 2); process_allmax('H2x', n, E, acc)
        if phase != 'h2only':
            from _codex_length_tier_matching_gate import h_blowup
            for t in range(3, 7):
                n, E, side = h_blowup(t); process_cut('H%d-inh' % t, n, adj_from_edges(n, E), side, acc)
        report('H2x N=18 allmax (no-two-hole)' if phase == 'h2only' else 'H-BLOWUPS t=2 allmax + t=3..6 inherited', acc)

    if phase in ('myciel', 'all'):
        acc = new_acc()
        E5 = Cn(5); n11, E11 = mycielski(5, E5)
        process_allmax('Grotzsch-N11', n11, E11, acc)   # N=11 maxcut feasible
        n23, E23 = mycielski(n11, E11)
        if is_triangle_free(n23, E23):
            side = [int(c) for c in '10101101011001000000001']
            process_cut('Myc23-apex', n23, adj_from_edges(n23, E23), side, acc)
        report('MYCIELSKI CHAIN (Grotzsch allmax + Myc23 apex)', acc)

    if phase in ('islands', 'all'):
        acc = new_acc()
        variants = []
        variants.append(('C5+MycC7',) + add_edges(union_disjoint((5, Cn(5)), mycielski(7, Cn(7))), [(0, 5)]))
        variants.append(('C7+Grotzsch',) + add_edges(union_disjoint((7, Cn(7)), mycielski(5, Cn(5))), [(0, 7)]))
        variants.append(('C5+Grotzsch',) + add_edges(union_disjoint((5, Cn(5)), mycielski(5, Cn(5))), [(0, 5)]))
        variants.append(('C5+C5',) + add_edges(union_disjoint((5, Cn(5)), (5, Cn(5))), [(0, 5)]))
        for nm, nn, EE in variants:
            if is_triangle_free(nn, EE):
                process_gmin(nm, nn, EE, acc)
        report('GLUED ISLANDS (gmin)', acc)

    if phase in ('random', 'all'):
        acc = new_acc()
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260630
        rng = random.Random(seed)
        for nn in range(12, 17):
            samples = 400 if nn <= 14 else 120
            for _ in range(samples):
                n, E = rand_trifree(nn, rng)
                process_allmax('rand%d' % nn, n, E, acc)
                if acc['first'] is not None:
                    break
            print('  random N=%d done: tested=%d two_hole=%d' % (nn, acc['tested'], acc['two_hole']), flush=True)
            if acc['first'] is not None:
                break
        report('RANDOM TRIANGLE-FREE N=12..16 with R<0', acc)


def blowbase(baseN, t, shard, nshard):
    """Blow up every connected tri-free base graph on baseN vertices by t (i.i.d.), run no-two-hole.
    shard/nshard split the base-graph list across parallel workers."""
    acc = new_acc()
    g6s = subprocess.run([GENG, '-tc', str(baseN)], capture_output=True, text=True).stdout.split()
    cnt = 0
    for idx, g6 in enumerate(g6s):
        if idx % nshard != shard:
            continue
        n0, E0 = dec(g6)
        nn, EE = blow_g(n0, E0, t)
        process_allmax('b%d.%d' % (baseN, t), nn, EE, acc)
        cnt += 1
        if acc['first'] is not None:
            break
    print('blowbase baseN=%d t=%d shard=%d/%d processed=%d' % (baseN, t, shard, nshard, cnt), flush=True)
    report('BLOWUP base N=%d x t=%d (shard %d/%d)' % (baseN, t, shard, nshard), acc)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'blowbase':
        # argv: blowbase baseN t shard nshard
        bN = int(sys.argv[2]); t = int(sys.argv[3]); sh = int(sys.argv[4]); ns = int(sys.argv[5])
        blowbase(bN, t, sh, ns)
    else:
        main()
