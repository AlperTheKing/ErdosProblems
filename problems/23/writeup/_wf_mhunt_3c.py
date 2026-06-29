"""Family #3 CENSUS backstop: exhaustive triangle-free census N<=13, EXACT global max cut.
For every triangle-free graph, compute ALL global-max cuts (maxcut_all), and for each connected-B
global-max cut check for a P-contained interior-overlap. This is the definitive small-N verification
that lemma (M) holds on GLOBAL maxima (the engineered family lives at larger N but census is exhaustive)."""
import sys, subprocess
sys.path.insert(0, "E:/Projects/ErdosProblems/problems/23/writeup")
from _h import dec, GENG, maxcut_all, Bconn
from _satzmu_conn import struct_for_side

def overlaps_on_cut(n, adj, s):
    if not Bconn(n, adj, s):
        return None
    st = struct_for_side(n, adj, s)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    out = []
    for f in M:
        if len(cyc[f]) != 1:
            continue
        P_f = cyc[f][0]
        pos = {x: i for i, x in enumerate(P_f)}; Pset = set(P_f)
        chords = []
        for g in M:
            if g == f:
                continue
            for Q in cyc[g]:
                if set(Q) <= Pset:
                    pp = sorted(pos[v] for v in Q)
                    if pp[-1] - pp[0] == len(pp) - 1:
                        chords.append((pp[0], pp[-1])); break
        for i in range(len(chords)):
            for j in range(i + 1, len(chords)):
                a1, b1 = chords[i]; a2, b2 = chords[j]
                if a1 > a2:
                    a1, b1, a2, b2 = a2, b2, a1, b1
                if a2 < min(b1, b2):
                    out.append((f, tuple(P_f), (a1, b1), (a2, b2)))
    return out

def run(nmax=13):
    print(f"=== _wf_mhunt_3c: triangle-free census GLOBAL-MAX interior-overlap scan N<=({nmax}) ===", flush=True)
    grand_cex = 0; grand_connB = 0; grand_graphs = 0
    for nn in range(5, nmax + 1):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        cex = 0; connB = 0; ngraphs = 0
        for g6 in outg:
            n, E = dec(g6)
            adj = [set() for _ in range(n)]
            for a, b in E:
                adj[a].add(b); adj[b].add(a)
            ngraphs += 1
            cuts = maxcut_all(n, adj)
            for s in cuts:
                ov = overlaps_on_cut(n, adj, s)
                if ov is None:
                    continue
                connB += 1
                if ov:
                    cex += 1
                    print(f"  *** COUNTEREX N={n} g6={g6} side={''.join(map(str,s))} ov={ov}", flush=True)
        grand_cex += cex; grand_connB += connB; grand_graphs += ngraphs
        print(f"  N={nn}: graphs={ngraphs} connB-globalmax-cuts={connB} interior-overlap-COUNTEREX={cex}", flush=True)
    print(f"\n  GRAND TOTAL: graphs={grand_graphs} connB-globalmax-cuts={grand_connB} COUNTEREX={grand_cex}", flush=True)
    print(f"  === {'LEMMA (M) HOLDS on all global maxima in census' if grand_cex==0 else 'COUNTEREXAMPLE FOUND'} ===", flush=True)

if __name__ == "__main__":
    import sys as _s
    run(int(_s.argv[1]) if len(_s.argv) > 1 else 13)
