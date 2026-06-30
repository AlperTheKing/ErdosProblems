"""ROW-LRS decomposition (EXACT). LRS <= ROW-LRS already validated (chain).
ROW-LRS per bad edge f:  A_f + m <= N + N^2/25,   A_f = (1/ell_f) sum_v p_f(v) T(v) = (O ell)_f/ell_f.

We split A_f to find what a proof must charge:
  A_f = sum_v p_f(v) T(v) / ell_f.
  Self term: O_ff = sum_v p_f(v)^2; cross: sum_{g!=f} O_fg ell_g.
Candidate sub-lemmas (hunt counterexamples on the gate):
  (S1) A_f <= N            (is the averaged load along f at most N?)   -- if TRUE, ROW-LRS needs only m<=N^2/25 ... NO that's Erdos. So expect S1 FALSE sometimes (A_f>N) and the slack matters.
  (S2) A_f <= N + (N^2/25 - m)        (= ROW-LRS itself)
  (S3) PATH-LRS: for EACH shortest geodesic P of f, (1/ell_f) sum_{v in P} T(v) + m <= N + N^2/25.  (PATH-LRS=>ROW-LRS since A_f=avg over geos of path-sums/ell_f; actually A_f = (1/ell_f) sum_v p_f(v)T(v) and p_f(v)=avg indicator => A_f = avg_P (1/ell_f sum_{v in P} T(v)). So PATH-LRS=>ROW-LRS by averaging.)
  (S4) sum_{v in P} T(v) <= ell_f * N + ell_f*(N^2/25 - m)   (path form)
  (S5) Decompose sum_{v in P} T(v) = ell_f*N + (overload on P) - (underload on P). Track O_P=sum_{v in P}max(T-N,0), U_P=sum_{v in P}max(N-T,0). PATH-LRS <=> O_P - U_P <= ell_f*(N^2/25 - m).
Report exact min margins + first violations + how slack (N^2/25 - m) is consumed.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane

def per_edge(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    if not M: return None
    N = F(n); m = len(M); slack = N*N/F(25) - m
    out = []
    for f in M:
        Ps = cyc[f]; k = len(Ps); lf = ell[f]
        # p_f(v)
        pf = {}
        for P in Ps:
            for v in P: pf[v] = pf.get(v, F(0)) + F(1, k)
        Af = sum(pf[v]*T[v] for v in pf) / lf
        # path forms
        path_marg = []
        for P in Ps:
            psum = sum(T[v] for v in P)
            # PATH-LRS margin: N + N^2/25 - m - psum/ell_f  >=0
            pm = (N + slack) - psum/lf
            path_marg.append(pm)
        s1 = N - Af                       # S1: A_f<=N margin (may be <0)
        s2 = (N + slack) - Af             # ROW-LRS margin
        s3 = min(path_marg)               # PATH-LRS margin (worst path)
        out.append(dict(f=f, ell=lf, Af=Af, s1=s1, s2=s2, s3=s3))
    return dict(M=M, N=n, m=m, slack=slack, rows=out)

def configs():
    def adj_of(n, E):
        a = [set() for _ in range(n)]
        for x, y in E: a[x].add(y); a[y].add(x)
        return a
    for L in range(8, 21, 2):
        n, E, side, _ = build_two_lane(L); yield ("two-lane-L%d" % L, n, adj_of(n, E), side)
    for nn in range(7, 12):
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
    for cyc in (5, 7, 9):
        for t in range(1, 6):
            n, E = blowup([t]*cyc)
            if n > 26: continue
            adj, cuts = gmins(n, E)
            if cuts: yield ("C%d[%d]" % (cyc, t), n, adj, cuts[0])
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n, E = blowup(parts)
        if n > 26: continue
        adj, cuts = gmins(n, E)
        if cuts: yield ("nu%s" % parts, n, adj, cuts[0])
    grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])
    for name, (nn, E) in [("Grotzsch", grot), ("Myc(Grotzsch)N23", mycg),
                          ("M(C7)", mycielski(7, Cn(7))), ("M(C9)", mycielski(9, Cn(9)))]:
        adj, cuts = gmins(nn, E)
        for s in cuts[:2]: yield (name, nn, adj, s)

if __name__ == "__main__":
    print("=== ROW-LRS / PATH-LRS decomposition (EXACT) ===", flush=True)
    agg = {k: {'min': F(10**12), 'at': None, 'viol': 0, 'first': None}
           for k in ['S1:Af<=N', 'S2:ROW-LRS', 'S3:PATH-LRS']}
    # also track: how often A_f>N (S1 violated) and is it ALWAYS covered by slack
    n_AfgtN = 0; n_rows = 0; n_cfg = 0
    # track worst case where A_f>N: is overload there <= slack?
    for name, n, adj, side in configs():
        if not Bconn(n, adj, side): continue
        pe = per_edge(n, adj, side)
        if pe is None: continue
        n_cfg += 1
        for r in pe['rows']:
            n_rows += 1
            if r['s1'] < 0: n_AfgtN += 1
            for key, val in [('S1:Af<=N', r['s1']), ('S2:ROW-LRS', r['s2']), ('S3:PATH-LRS', r['s3'])]:
                a = agg[key]
                if val < a['min']: a['min'] = val; a['at'] = (name, str(r['f']), r['ell'])
                if val < 0:
                    a['viol'] += 1
                    if a['first'] is None:
                        a['first'] = (name, n, pe['m'], str(r['f']), 'Af=' + str(r['Af']), 'slack=' + str(pe['slack']))
    print("  configs=%d  per-edge rows=%d  rows with A_f>N (S1 fails)=%d (%.2f%%)" %
          (n_cfg, n_rows, n_AfgtN, 100.0*n_AfgtN/max(n_rows, 1)), flush=True)
    for k in ['S1:Af<=N', 'S2:ROW-LRS', 'S3:PATH-LRS']:
        a = agg[k]
        flag = "HOLDS" if a['viol'] == 0 else "VIOLATED(%d)" % a['viol']
        print("  %-14s min=%s  at=%s  %s" % (k, str(a['min'])[:28], a['at'], flag), flush=True)
        if a['first']: print("      first viol: %s" % (a['first'],), flush=True)
