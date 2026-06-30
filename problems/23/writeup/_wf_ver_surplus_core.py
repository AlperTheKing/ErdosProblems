"""Core battery only (no deep N=12/13 census) -- fast variant of _wf_ver_surplus, unbuffered."""
import _wf_ver_surplus as W
from fractions import Fraction as F
import subprocess
from _h import dec, GENG
from _stark1 import gmins
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords
from _bdef_construct import mycielski, Cn, union_disjoint

acc = {'n': 0, 'viol': 0, 'first_viol': None,
       'min_margin': (F(10**30), '', 0, 0, '', '', '', ''),
       'max_ratio': (F(-1), '', 0, 0),
       'handshake_fail': 0, 'handshake_examples': [],
       'identity_fail': 0, 'identity_examples': [],
       'form_mismatch': 0, 'form_examples': [],
       'badset_mismatch': 0,
       'denom0': 0, 'denom0_nonzero_margin': 0, 'denom0_examples': []}

for L in range(8, 21):
    n, E, side, _ = build_two_lane(L)
    W.chk("two-lane-L%d" % L, n, W.adj_of(n, E), side, acc)
for (Ll, k, gap) in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
    bad = greedy_chords(Ll, k, gap)
    n, E, side, bad = build_k_lane(Ll, k, bad)
    W.chk("klane-L%dk%d" % (Ll, k), n, W.adj_of(n, E), side, acc)
for nn in range(7, 12):
    outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
    for g6 in outg:
        n, E = dec(g6)
        adj, cuts = gmins(n, E)
        for s in cuts:
            W.chk("cen" + g6, n, adj, s, acc)
for cyc in (5, 7, 9):
    for t in range(1, 6):
        n, E = W.blowup([t] * cyc)
        if n > 26:
            continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:1] if cuts else []):
            W.chk("C%d_t%d" % (cyc, t), n, adj, s, acc)
for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],
              [1,6,2,2,6],[4,1,4,1,4],[2,3,1,3,2],[1,1,5,1,1],[5,1,1,1,5]]:
    n, E = W.blowup(parts)
    if n > 26:
        continue
    adj, cuts = gmins(n, E)
    for s in (cuts[:1] if cuts else []):
        W.chk("nu%s" % parts, n, adj, s, acc)
grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])

def bridge(b1, b2, u, v):
    nn, E = union_disjoint(b1, b2); n1 = b1[0]
    return nn, E + [(u, n1 + v)]

for name, (nn, E) in [("Grotzsch", grot), ("Myc(Grotzsch)N23", mycg),
                      ("M(C7)", mycielski(7, Cn(7))), ("M(C9)", mycielski(9, Cn(9))),
                      ("bridge(C7,Grotzsch)", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
                      ("bridge(C9,C9)", bridge((9, Cn(9)), (9, Cn(9)), 0, 0))]:
    adj, cuts = gmins(nn, E)
    for s in cuts[:3]:
        W.chk(name, nn, adj, s, acc)

print("CORE configs=%d viol=%d" % (acc['n'], acc['viol']))
mm = acc['min_margin']
print("MIN margin=%s float=%.6g at %s N=%d beta=%d Gamma=%s V2=%s TVcut=%s TVbad=%s" % (
    mm[0], float(mm[0]), mm[1], mm[2], mm[3], mm[4], mm[5], mm[6], mm[7]))
mr = acc['max_ratio']
print("MAX ratio=%s float=%.10g at %s N=%d beta=%d  151/16=%s -> %s" % (
    mr[0], float(mr[0]), mr[1], mr[2], mr[3], F(151, 16),
    "MATCH" if mr[0] == F(151, 16) else ("EXCEEDS" if mr[0] > F(151, 16) else "below")))
print("handshake_fail=%d identity_fail=%d form_mismatch=%d badset_mismatch=%d" % (
    acc['handshake_fail'], acc['identity_fail'], acc['form_mismatch'], acc['badset_mismatch']))
print("denom0=%d denom0_nonzero_margin=%d" % (acc['denom0'], acc['denom0_nonzero_margin']))
print("denom0_examples=%s" % (acc['denom0_examples'][:5],))
print("FIRST VIOL:", acc['first_viol'])
