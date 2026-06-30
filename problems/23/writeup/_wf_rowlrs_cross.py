"""ROW-LRS cross-term decomposition (EXACT), SMALL battery (census N<=10 + two-lane + C5/C7[t] + Myc N23)
to keep it fast. A_f = O_ff + (1/ell_f) sum_{g!=f} O_fg ell_g.
We test the split:
   self_f   = O_ff                         (<= ell_f)
   cross_f  = (1/ell_f) sum_{g!=f} O_fg*ell_g   (>=0)
   A_f = self_f + cross_f.
Candidate proof sub-lemmas:
   (C1) self_f <= ell_f                    (KNOWN)
   (C2) cross_f <= N - ell_f + (N^2/25 - m)   <=> ROW-LRS given C1? NO: ROW-LRS is self+cross<=N+slack.
        Since self<=ell_f, ROW-LRS follows from cross_f <= N + slack - ell_f. Test if THAT holds.
   (C3) A_f <= N  (S1) and when it fails, by how much vs slack.
Report exact mins + first violations.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane

def rows(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    if not M: return None
    N = F(n); m = len(M); slack = N*N/F(25) - m
    P = {}
    for f in M:
        k = len(cyc[f]); d = {}
        for Pp in cyc[f]:
            for v in Pp: d[v] = d.get(v, F(0)) + F(1, k)
        P[f] = d
    out = []
    for f in M:
        self_f = sum(P[f][v]**2 for v in P[f])          # O_ff
        cross_f = F(0)
        for g in M:
            if g == f: continue
            common = set(P[f]) & set(P[g])
            Ofg = sum(P[f][v]*P[g][v] for v in common)
            cross_f += Ofg*ell[g]
        cross_f = cross_f / ell[f]
        Af = self_f + cross_f
        out.append(dict(f=f, ell=ell[f], self_f=self_f, cross_f=cross_f, Af=Af,
                        c2=(N + slack - ell[f]) - cross_f, c3=N - Af))
    return dict(N=n, m=m, slack=slack, rows=out)

def configs():
    def adj_of(n, E):
        a = [set() for _ in range(n)]
        for x, y in E: a[x].add(y); a[y].add(x)
        return a
    for L in range(8, 17, 2):
        n, E, side, _ = build_two_lane(L); yield ("two-lane-L%d" % L, n, adj_of(n, E), side)
    for nn in range(7, 11):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6); adj, cuts = gmins(n, E)
            for s in cuts: yield ("cen%s" % g6, n, adj, s)
    def blowup(parts):
        mm = len(parts); off = [0]*(mm+1)
        for i in range(mm): off[i+1] = off[i]+parts[i]
        nn = off[mm]; EE = []
        for i in range(mm):
            j = (i+1) % mm
            for a in range(off[i], off[i+1]):
                for b in range(off[j], off[j+1]): EE.append((min(a, b), max(a, b)))
        return nn, sorted(set(EE))
    for cyc in (5, 7):
        for t in range(1, 5):
            n, E = blowup([t]*cyc)
            if n > 26: continue
            adj, cuts = gmins(n, E)
            if cuts: yield ("C%d[%d]" % (cyc, t), n, adj, cuts[0])
    grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])
    for name, (nn, E) in [("Grotzsch", grot), ("Myc(Grotzsch)N23", mycg)]:
        adj, cuts = gmins(nn, E)
        for s in cuts[:1]: yield (name, nn, adj, s)

if __name__ == "__main__":
    print("=== ROW-LRS cross-term decomposition (EXACT, small battery) ===", flush=True)
    agg = {k: {'min': F(10**12), 'at': None, 'viol': 0, 'first': None}
           for k in ['C1:self<=ell', 'C2:cross<=N+slack-ell', 'C3:A<=N']}
    nrow = 0; ncfg = 0; n_c3fail = 0
    for name, n, adj, side in configs():
        if not Bconn(n, adj, side): continue
        r = rows(n, adj, side)
        if r is None: continue
        ncfg += 1
        for rr in r['rows']:
            nrow += 1
            if rr['c3'] < 0: n_c3fail += 1
            for key, val in [('C1:self<=ell', rr['ell']-rr['self_f']),
                             ('C2:cross<=N+slack-ell', rr['c2']),
                             ('C3:A<=N', rr['c3'])]:
                a = agg[key]
                if val < a['min']: a['min'] = val; a['at'] = (name, str(rr['f']), rr['ell'])
                if val < 0:
                    a['viol'] += 1
                    if a['first'] is None:
                        a['first'] = (name, n, r['m'], 'self=%s' % rr['self_f'], 'cross=%s' % rr['cross_f'], 'slack=%s' % r['slack'])
    print("  configs=%d rows=%d  rows with A_f>N (C3 fails)=%d" % (ncfg, nrow, n_c3fail), flush=True)
    for k in ['C1:self<=ell', 'C2:cross<=N+slack-ell', 'C3:A<=N']:
        a = agg[k]
        flag = "HOLDS" if a['viol'] == 0 else "VIOLATED(%d)" % a['viol']
        print("  %-24s min=%s  at=%s  %s" % (k, str(a['min'])[:26], a['at'], flag), flush=True)
        if a['first']: print("      first viol: %s" % (a['first'],), flush=True)
