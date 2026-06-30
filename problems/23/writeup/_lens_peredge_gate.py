"""INDEPENDENT exact gate for Codex's PER-EDGE LENS lemma (block 09:32):

  C_g(v) := (1/|cyc[g]|) * sum_{Q in cyc[g], v in Q} ( sum_{u in Q} T[u] - N*ell[g] ).
  (Note  (K2T - NT)[v] = sum_g C_g(v),  so R[v] = -sum_g C_g(v).)

  CANDIDATE: if C_g(v) > 0 then g is the SHORT member of a strict lens (f,g) [ell[f]>ell[g], some Pg in
  cyc[g] a contiguous subpath of some Pf in cyc[f] up to reversal] AND v lies on a participating short
  geodesic Pg of g.

Contrapositive => strict-lens-free cut has C_g(v)<=0 for all g,v => K2T<=NT by summing over g.
Independent reimpl of lens detection; reuses only audited struct_for_side.  Exact Fraction.
Battery adds Myc(Grotzsch) N=23 + overloaded blowups (Codex tested census+Grotzsch+H?AFBo] blowups only).
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _wf_deficit_farkas import odd_blowup


def contig_sub(small, big):
    ls, lb = len(small), len(big)
    if ls > lb:
        return False
    for i in range(lb - ls + 1):
        if big[i:i + ls] == small:
            return True
    return False


def short_member_verts(M, ell, cyc):
    """For each bad edge g that is the SHORT member of >=1 strict lens, the set of vertices lying on a
       PARTICIPATING short geodesic Pg (one that embeds in some longer Pf).  Returns dict g -> set."""
    Ms = list(M)
    out = {}
    for f in Ms:
        Lf = ell[f]
        for g in Ms:
            if f == g or ell[g] >= Lf:
                continue
            for Pg in cyc[g]:
                Pgl = list(Pg); Pgr = Pgl[::-1]
                embeds = False
                for Pf in cyc[f]:
                    Pfl = list(Pf)
                    if contig_sub(Pgl, Pfl) or contig_sub(Pgr, Pfl):
                        embeds = True
                        break
                if embeds:
                    out.setdefault(g, set()).update(Pgl)
    return out


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    acc['cuts'] += 1
    N = F(n)
    smv = short_member_verts(M, ell, cyc)
    for g in M:
        Qs = cyc[g]; w = F(1, len(Qs))
        for v in range(n):
            Cg = F(0)
            for Q in Qs:
                if v in Q:
                    Cg += w * (sum(T[u] for u in Q) - N * ell[g])
            if Cg > 0:
                acc['pos'] += 1
                if g in smv and v in smv[g]:
                    acc['covered'] += 1
                else:
                    acc['fail'] += 1
                    if acc['ex'] is None:
                        acc['ex'] = (name, n, ''.join(map(str, side)), g, v, str(Cg),
                                     'g_is_short_member' if g in smv else 'g_NOT_short_member')


def gfam_allmax(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc)


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    acc = dict(cuts=0, pos=0, covered=0, fail=0, ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d: cuts=%d posC=%d covered=%d fail=%d"
              % (nn, acc['cuts'], acc['pos'], acc['covered'], acc['fail']), flush=True)
    grN, grE = mycielski(5, Cn(5)); gfam_allmax("Grotzsch_N11", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Grotzsch+Myc23: cuts=%d posC=%d covered=%d fail=%d %s"
          % (acc['cuts'], acc['pos'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)
    hN, hE = dec("H?AFBo]")
    base_side = [int(c) for c in "111110000"]
    for t in (2, 3):
        nn, EE = vertex_blowup(hN, hE, t)
        side = [base_side[v // t] for v in range(nn)]
        adj = [set() for _ in range(nn)]
        for x, y in EE:
            adj[x].add(y); adj[y].add(x)
        test_cut("Hblow_t%d" % t, nn, adj, side, acc)
    print("after Hblowups: cuts=%d posC=%d covered=%d fail=%d %s"
          % (acc['cuts'], acc['pos'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)
    for q in range(2, 14):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(2,2,2,2,2),(3,3,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 16:
            gfam_allmax("blow%s" % (sizes,), nn, EE, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam_allmax("isl", nn, EE, acc)
    print("after chains+blowups+islands: cuts=%d posC=%d covered=%d fail=%d %s"
          % (acc['cuts'], acc['pos'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)
    rng = random.Random(7); made = 0; tries = 0
    while made < 100 and tries < 50000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.32)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam_allmax("rand%d" % made, nn, EE, acc)
    print("=" * 60)
    print("connected-B max cuts tested:", acc['cuts'], " (random N11/12:", made, ")")
    print("positive C_g(v) entries:", acc['pos'], "  covered (g short-member, v on participating Pg):", acc['covered'])
    print("PER-EDGE LENS LEMMA FAILURES:", acc['fail'], acc['ex'] or '')
    print("VERDICT:", "PER-EDGE LENS LEMMA HOLDS exact incl N=23 + blowups (C_g(v)>0 => g short-member-of-lens thru v)"
          if acc['fail'] == 0 else "FAIL")


if __name__ == "__main__":
    main()
