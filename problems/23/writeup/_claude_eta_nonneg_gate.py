r"""EXACT-GATE for the C5 density-reserve NONNEGATIVITY eta_X = |V_X|^2/25 - m_X >= 0 (2026-07-08).

The multi-atom C5 density bank (GPT-Pro) needs eta_X = |V_X|^2/25 - m_X >= 0 for the components/cages X where C5 is
spent. This is the LOCAL conjecture on X (m_X <= |V_X|^2/25) and is the CIRCULARITY crux: if eta_X >= 0 must be assumed
it is circular; if it holds by a GRAPH FACT (like the leaf ell<=N) or by induction, it is not.

This gate tests, EXACTLY (Fraction), whether eta_X >= 0 for EVERY K2-support component of EVERY Gamma-min cage:
  m_X = # atoms (bad edges) in the K2-component X,
  V_X = union of geodesic supports,
  eta_X = |V_X|^2 / 25 - m_X.
A component with eta_X < 0 AND positive demand would be a genuine circularity obstruction (the C5 reserve it needs is
itself unproven). A component with eta_X < 0 but Demand = 0 is harmless. If eta_X >= 0 always where demand > 0, the
per-component C5 reserve is graph-nonnegative (like the leaf ell>=5 => eta = ell^2/25 - 1 >= 0). Coverage: census N<=11
Gamma-min + even-cycle+chord N=18..30. Run from problems/23/writeup.
"""
from fractions import Fraction as F
import subprocess
from _claude_residual_hall_gate import residuals, k2_components, even_cycle_chord
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    ell = cd['ell']
    comps = k2_components(n, cd)
    acc['cages'] += 1
    for X in comps:
        VX = X['VX']; atomsX = X['atoms']
        mX = len(atomsX)
        etaX = F(len(VX) ** 2, 25) - mX
        demand = sum(ell[e] ** 2 - 25 for e in atomsX)  # ell>=5 => each term >=0
        acc['comps'] += 1
        if acc['min_eta'] is None or etaX < acc['min_eta']:
            acc['min_eta'] = etaX
        if etaX < 0:
            acc['eta_neg'] += 1
            if demand > 0:
                acc['eta_neg_demand'] += 1
                if acc['ex'] is None:
                    acc['ex'] = dict(name=name, n=n, VX=len(VX), mX=mX, eta=str(etaX), demand=demand,
                                     maxell=max(ell[e] for e in atomsX))


def main():
    acc = dict(cages=0, comps=0, eta_neg=0, eta_neg_demand=0, min_eta=None, ex=None)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            analyze('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cages %d, comps %d, eta<0 %d, eta<0 & Demand>0 %d"
              % (nn, acc['cages'], acc['comps'], acc['eta_neg'], acc['eta_neg_demand']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            analyze('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc)
    print("=" * 92)
    print("C5 DENSITY-RESERVE NONNEGATIVITY GATE  eta_X = |V_X|^2/25 - m_X:")
    print("  cages %d, components %d | min eta_X = %s | eta_X<0 comps: %d | eta_X<0 AND Demand>0: %d"
          % (acc['cages'], acc['comps'], str(acc['min_eta']), acc['eta_neg'], acc['eta_neg_demand']))
    if acc['ex']:
        print("  *** eta_X<0 at a POSITIVE-DEMAND component (circularity-obstruction candidate): %s ***" % (acc['ex'],))
    print("VERDICT: %s" % (
        "eta_X = |V_X|^2/25 - m_X >= 0 on EVERY component with positive demand (min eta=%s) -- the C5 density reserve is"
        " graph-NONNEGATIVE where it is spent (non-circular at component level, like leaf ell>=5). Supports the density ledger."
        % str(acc['min_eta']) if acc['eta_neg_demand'] == 0 else
        "eta_X < 0 at %d positive-demand components -- the C5 density reserve is NEGATIVE where demand exists =>"
        " CIRCULARITY/obstruction candidate (the reserve it needs is itself the unproven local conjecture)." % acc['eta_neg_demand']))


if __name__ == '__main__':
    main()
