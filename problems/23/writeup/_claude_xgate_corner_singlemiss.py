"""Claude INDEPENDENT cross-gate of Codex's two residual-Hall atoms (2026-06-30 ASKs),
on the KILLER battery Codex's census-N<=10-only runs do NOT cover:
  * Myc(Grotzsch) N=23 apex cut  (the construction that killed k2),
  * glued islands C5+Myc(C7) etc (the constructions that killed ZMU / O-K-SUPPORT),
  * extended H-blowups t=2 allmax + t=3..5 inherited,
  * census N=11 (one order beyond Codex).
Plus an EXACT machinery-independence check: my own witness_structure (_pl_gate, reimplemented
from scratch) must reproduce Codex terminal_shadow_details cross_m/bdy_b/witnesses on the SAME switch S.

Atoms:
  (SM) component-local single-miss  [_codex_rare_exit_complement_gate.gate]:
        per residual component (A,B): |A|=|B|, row_miss<=1, col_miss<=n-2  => Hall.
  (CO) replacement-exit corner      [_codex_replacement_exit_gate.gate]:
        residual e, longer F1-edge f (e not a witness of f): exists e' witnessed by f with
        outside(e')=outside(e) OR inside(e')=inside(f) OR e'=(inside(e),outside(f)).
All exact (integer/combinatorial); reuses Codex's gate LOGIC (the precise claim) but feeds it my battery.
Run from E:/Projects/ErdosProblems/problems/23/writeup."""
import sys, subprocess
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\writeup")
from collections import Counter
from _h import GENG, dec, maxcut_all, Bconn, loads
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import best_seed_moat_mask, h_blowup, residuals
from _codex_rare_exit_complement_gate import gate as sm_gate
from _codex_replacement_exit_gate import gate as co_gate
from _pl_gate import witness_structure
from _bdef_construct import Cn, mycielski, union_disjoint, add_edges, is_triangle_free


def my_vs_codex(n, adj, side, st, mask, det):
    Sset = set(i for i in range(n) if (mask >> i) & 1)
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return "mine-None"
    crossM, bdyB, wit = res
    if tuple(sorted(crossM)) != tuple(sorted(det["cross_m"])):
        return "DIFFER cross_m"
    if tuple(sorted(bdyB)) != tuple(sorted(det["bdy_b"])):
        return "DIFFER bdy_b"
    my_w = {}
    for (f, e) in wit:
        my_w.setdefault(e, set()).add(f)
    cx_w = {e: set(fs) for e, fs in det["witnesses"].items()}
    for e in det["bdy_b"]:
        if my_w.get(e, set()) != cx_w.get(e, set()):
            return "DIFFER witnesses %r" % (e,)
    return "agree"


def scan_cut(name, n, adj, side, acc, max_add=1):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            acc["no_switch"] += 1
            continue
        _seed, mask, _psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        acc["tested"] += 1
        mc = my_vs_codex(n, adj, side, st, mask, det)
        acc["mach"][mc if mc in ("agree", "mine-None") else mc.split()[0] + " " + mc.split()[1]] += 1
        if mc.startswith("DIFFER") and acc["mach_ex"] is None:
            acc["mach_ex"] = (name, n, "".join(map(str, side)), v, mc)
        ok_sm, st_sm, info_sm = sm_gate(st, det)
        acc["sm_status"][st_sm] += 1
        if not ok_sm and acc["sm_first"] is None:
            acc["sm_first"] = dict(name=name, n=n, side="".join(map(str, side)), v=v, status=st_sm, info=info_sm)
        ok_co, st_co, info_co = co_gate(st, det, mask)
        acc["co_status"][st_co] += 1
        if not ok_co and acc["co_first"] is None:
            acc["co_first"] = dict(name=name, n=n, side="".join(map(str, side)), v=v, status=st_co, info=info_co)


def scan_allmax(name, n, edges, acc, max_add=1):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_add)


def scan_gmin(name, n, edges, acc, max_add=1):
    info = loads(n, edges)
    if info is None:
        print("  [%s] loads()=None (no gamma-min) -- skipped" % name, flush=True)
        return
    scan_cut(name, n, info["adj"], info["side"], acc, max_add)


def new_acc():
    return dict(tested=0, no_switch=0, bad_terminal=0, mach=Counter(), mach_ex=None,
                sm_status=Counter(), sm_first=None, co_status=Counter(), co_first=None)


def report(label, acc):
    print("=" * 70)
    print("BATTERY:", label)
    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("machinery mine-vs-codex:", dict(acc["mach"]), "| ex:", acc["mach_ex"])
    print("SM single-miss status:", dict(acc["sm_status"]), "| first FAIL:", acc["sm_first"] or "NONE")
    print("CO corner       status:", dict(acc["co_status"]), "| first FAIL:", acc["co_first"] or "NONE")
    sm_ok = acc["sm_first"] is None
    co_ok = acc["co_first"] is None
    mach_ok = acc["mach_ex"] is None
    print("VERDICT  SM:", "PASS" if sm_ok else "FAIL",
          " CO:", "PASS" if co_ok else "FAIL",
          " MACHINERY:", "AGREE" if mach_ok else "DIFFER", flush=True)
    return sm_ok, co_ok, mach_ok


def island_battery():
    out = []
    isl = (5, Cn(5))
    # the documented k2/ZMU-killer family + variants
    n, E = union_disjoint(isl, mycielski(7, Cn(7))); n, E = add_edges((n, E), [(0, 5)])
    out.append(("C5+MycC7 bridge N=%d" % n, n, E))
    n, E = union_disjoint((7, Cn(7)), mycielski(5, Cn(5))); n, E = add_edges((n, E), [(0, 7)])
    out.append(("C7+Grotzsch bridge N=%d" % n, n, E))
    n, E = union_disjoint(isl, mycielski(5, Cn(5))); n, E = add_edges((n, E), [(0, 5)])
    out.append(("C5+Grotzsch bridge N=%d" % n, n, E))
    n, E = union_disjoint(isl, isl); n, E = add_edges((n, E), [(0, 5)])
    out.append(("C5+C5 bridge N=%d" % n, n, E))
    return [(nm, nn, EE) for (nm, nn, EE) in out if is_triangle_free(nn, EE)]


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--phase", default="killers", choices=["killers", "census11", "all"])
    p.add_argument("--max-add", type=int, default=1)
    args = p.parse_args()

    if args.phase in ("killers", "all"):
        # ---- glued islands (gmin single cut) ----
        accI = new_acc()
        for nm, nn, EE in island_battery():
            print("  island %s ..." % nm, flush=True)
            scan_gmin(nm, nn, EE, accI, args.max_add)
        report("GLUED ISLANDS (gmin)", accI)

        # ---- Myc(Grotzsch) N=23 apex cut (documented) ----
        accM = new_acc()
        E5 = Cn(5); n11, E11 = mycielski(5, E5); n23, E23 = mycielski(n11, E11)
        if is_triangle_free(n23, E23):
            side_str = "10101101011001000000001"
            side = [int(c) for c in side_str]
            adj = adj_from_edges(n23, E23)
            print("  Myc(Grotzsch) N=23 apex cut Bconn=%s" % Bconn(n23, adj, side), flush=True)
            scan_cut("Myc23-apex", n23, adj, side, accM, args.max_add)
            # also probe ALL single-vertex-derived gmin? too big; also try gmin-of-allmax is infeasible (2^22).
        report("MYC(GROTZSCH) N=23 apex", accM)

        # ---- extended H-blowups: t=2 allmax, t=3..5 inherited ----
        accH = new_acc()
        n, edges, _s = h_blowup(2); scan_allmax("H2-allmax", n, edges, accH, args.max_add)
        for t in range(3, 6):
            n, edges, side = h_blowup(t)
            scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, accH, args.max_add)
        report("H-BLOWUPS t=2 allmax + t=3..5 inherited", accH)

    if args.phase in ("census11", "all"):
        accC = new_acc()
        cnt = 0
        for g6 in subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6); scan_allmax("cen11", nn, edges, accC, args.max_add); cnt += 1
        print("  census N=11 graphs scanned:", cnt, flush=True)
        report("CENSUS N=11 (allmax)", accC)


if __name__ == "__main__":
    main()
