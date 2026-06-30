"""Self-test: confirm the overlap detector fires on KNOWN interior-overlap layouts
(from _M_tailswitch_gate), and that those overlap-bearing cuts are NON-global-max
(explaining why a global-max-only scan reports zero). Pure exact arithmetic."""
import sys
from _M_tailswitch_gate import build_pd
from _wf_mhunt_0 import adj_of, find_overlaps_on_cut, cutsize, hill_max_size

# Use SMALL layouts (pend=8 => n=18) so we can also do an exact check fast.
for name, pend, chords in [("crossing", 8, [(0, 4), (2, 6)]),
                            ("nested", 8, [(0, 6), (2, 4)])]:
    n, E = build_pd(pend, chords)
    adj = adj_of(n, E)
    s = [v % 2 for v in range(n)]
    ovs = find_overlaps_on_cut(n, adj, s)
    cs = cutsize(n, adj, s)
    hm = hill_max_size(n, adj, restarts=2000, seed=7)  # heuristic max (lower bound on true)
    isnonmax = cs < hm
    print(f"{name}: n={n} parity-cutsize={cs} heur-max>={hm} parity-is-nonmax={isnonmax} overlaps_on_parity={len(ovs)}")
    for ov in ovs[:3]:
        f, P, c1, c2, g1, g2 = ov
        print(f"   detected overlap: f={f} chord1={c1} chord2={c2}")
    sys.stdout.flush()
