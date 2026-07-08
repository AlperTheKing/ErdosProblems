r"""DENSITY-vs-HARDNESS gate (2026-07-08). Tests the arXiv-scan strategic angle: is gap#1's hardness (multi-atom
congestion / near-tightness of beta) concentrated at HIGH edge-density (-> 0.4, the C5[t] extremal), so that the
MEDIUM-density band [0.2486, 0.3197] (where Balogh-Clemen-Lidicky have NOT proven the conjecture, and where WE would
need gap#1) has genuine SLACK and the impure-balanced-neutral-lens is absent?

BCL (arXiv 2103.14179): conjecture PROVEN for edge-density <= 0.2486 OR >= 0.3197. C5[t] extremal density -> 2/5 = 0.4.
If a full delta=0 proof only needs the medium band, and the hard gap#1 structures live at high density, then our
charging route restricted to the medium band never meets the deficient cage.

For each census triangle-free Gamma-min MAX cut (N<=11), compute:
  density d = 2 e / (N(N-1));  band = low(<=0.2486) / medium(0.2486..0.3197) / high(>=0.3197);
  tightness t = beta / (N^2/25) = 25 beta / N^2  (beta = e - maxcut; conjecture <=> t <= 1; extremal t=1);
  multi-atom min-max cut-edge load L* (congestion, <=25 target) over ell=5 K2-components.
Report, PER BAND: max tightness t, max multi-atom L*, and whether any medium-band graph is near-tight (t close to 1)
or high-congestion (L* large). VERDICT: if near-tight/high-congestion cluster in HIGH band and medium band is slack,
the strategic angle is SUPPORTED (restrict gap#1 to medium band => easier). EXACT rational. Run from problems/23/writeup.
"""
import subprocess
from fractions import Fraction as F
from _claude_residual_hall_gate import residuals, k2_components
from _claude_multiatom_congestion_probe import min_max_load
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def band_of(d):
    if d <= F(2486, 10000):
        return 'low'
    if d >= F(3197, 10000):
        return 'high'
    return 'medium'


def main():
    print("DENSITY-vs-HARDNESS gate: is gap#1 hardness (tightness beta/(N^2/25), multi-atom congestion L*) concentrated")
    print("at HIGH density (C5[t]=0.4), leaving the OPEN medium band [0.2486,0.3197] with slack?")
    print("=" * 100)
    acc = {b: dict(n=0, max_t=F(0), max_t_ex=None, max_L=0.0, max_L_ex=None, near_tight=0) for b in ('low', 'medium', 'high')}
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            e = len(E)
            cuts = maxcut_all(n, adj)
            if not cuts:
                continue
            mc = max(sum(1 for x in range(n) for y in adj[x] if x < y and side[x] != side[y]) for side in cuts)
            beta = e - mc
            d = F(2 * e, n * (n - 1))
            t = F(25 * beta, n * n) if beta > 0 else F(0)
            b = band_of(d)
            acc[b]['n'] += 1
            if t > acc[b]['max_t']:
                acc[b]['max_t'] = t; acc[b]['max_t_ex'] = (g6, n, float(d), beta)
            if t >= F(9, 10):
                acc[b]['near_tight'] += 1
            # multi-atom congestion on the Gamma-min max cut
            bst = gmin(n, adj, cuts)
            if bst is None:
                continue
            side = bst[0]
            if not Bconn(n, adj, side):
                continue
            cd = residuals(n, adj, side)
            if cd is None or not cd['ell']:
                continue
            for X in k2_components(n, cd):
                five = [a for a in X['atoms'] if cd['ell'][a] == 5]
                if len(five) < 2:
                    continue
                L, bx, ells = min_max_load(n, adj, side, cd, five)
                if L is not None and L > acc[b]['max_L']:
                    acc[b]['max_L'] = L; acc[b]['max_L_ex'] = (g6, n, float(d), len(five))
        print("  through N=%d: " % nn + " | ".join(
            "%s d n=%d maxT=%.3f maxL*=%.2f nearTight(t>=.9)=%d" % (b, acc[b]['n'], float(acc[b]['max_t']), acc[b]['max_L'], acc[b]['near_tight'])
            for b in ('low', 'medium', 'high')), flush=True)
    print("=" * 100)
    for b in ('low', 'medium', 'high'):
        a = acc[b]
        print("BAND %-6s: graphs %d | max tightness beta/(N^2/25) = %.4f @ %s | max multi-atom L* = %.3f @ %s | near-tight(t>=0.9) %d"
              % (b, a['n'], float(a['max_t']), a['max_t_ex'], a['max_L'], a['max_L_ex'], a['near_tight']))
    print("=" * 100)
    med, hi = acc['medium'], acc['high']
    angle_ok = float(med['max_t']) < float(hi['max_t']) and med['near_tight'] == 0
    print("VERDICT: %s" % (
        "STRATEGIC ANGLE SUPPORTED (on census N<=11): the MEDIUM band [0.2486,0.3197] has strictly LOWER max tightness "
        "(%.3f) than HIGH (%.3f) and ZERO near-tight graphs => medium-density triangle-free graphs have genuine slack; "
        "the near-tight/deficient regime (where the impure lens lives) is a HIGH-density phenomenon. Combining our gap#1 "
        "charging route (medium band only) with BCL (density outside [0.2486,0.3197]) is a viable route to break the wall."
        % (float(med['max_t']), float(hi['max_t']))
        if angle_ok else
        "MIXED: medium-band max tightness %.3f (near-tight %d), high-band %.3f. The hardness is NOT cleanly high-density-"
        "only on census; the medium-band restriction does not obviously remove the lens. Re-examine at larger N / note "
        "census is small (max density limited by N)." % (float(med['max_t']), med['near_tight'], float(hi['max_t']))))


if __name__ == '__main__':
    main()
