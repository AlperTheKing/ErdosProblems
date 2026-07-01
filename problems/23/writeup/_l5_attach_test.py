"""Independent cross-gate of Codex's BOUNDARY-COMPATIBILITY result (21:32): enumerate every one-edge
triangle-free attachment to the stretched L=7 (and L=9) nested core, find the gamma-min connected-B
max cut(s), and report any attachment for which the intended terminal bad edges f0=(s,t),f1=(u,v) are
gamma-min-bad AT THEIR INTENDED LENGTHS (L, L+2). Prediction (Codex): none survive at L/(L+2); the only
'survivors' collapse to shorter lengths (the S2 shorter-parent-row contradiction). EXACT. From problems/23/writeup."""
from _h import gmin, maxcut_all, Bconn
from _codex_k2t_switch_probe import adj_from_edges
from _bdef_construct import is_triangle_free
from _l5forcing_gate import build, edge


def run(L):
    n, E, side, f0, f1, adj, bip = build(L)
    Eset = set(edge(*e) for e in E)
    total = 0
    survive_true = []      # intended bad at intended lengths (L, L+2)  -> boundary-compat FAIL
    survive_collapsed = []  # intended bad but lengths collapsed (<L)    -> S2 shorter-parent
    for a in range(n):
        for b in range(a + 1, n):
            if edge(a, b) in Eset:
                continue
            E2 = E + [(a, b)]
            if not is_triangle_free(n, E2):
                continue
            total += 1
            adj2 = adj_from_edges(n, E2)
            cuts = maxcut_all(n, adj2)
            r = gmin(n, adj2, cuts)
            if r is None:
                continue
            sd, G, M, ell = r
            Ms = set(M)
            if f0 in Ms and f1 in Ms:
                l0, l1 = ell.get(f0), ell.get(f1)
                if {l0, l1} == {L, L + 2}:
                    survive_true.append((edge(a, b), G, (l0, l1)))
                else:
                    survive_collapsed.append((edge(a, b), G, (l0, l1)))
    print("L=%d: one-edge triangle-free attachments tested=%d" % (L, total))
    print("  intended {f0,f1} gamma-min-bad AT lengths (L,L+2) [boundary-compat FAIL]:", len(survive_true), survive_true[:4])
    print("  intended {f0,f1} gamma-min-bad but COLLAPSED lengths [S2 shorter-parent]:", len(survive_collapsed), survive_collapsed[:6])
    print("  VERDICT:", "BOUNDARY-COMPAT HOLDS (no attachment preserves the L/(L+2) core; blockers collapse to shorter rows)"
          if not survive_true else "*** boundary-compat FAIL: an attachment preserves the %d/%d core ***" % (L, L + 2))


if __name__ == '__main__':
    run(7)
    run(9)
