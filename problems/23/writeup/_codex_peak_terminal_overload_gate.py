"""Gate the peak terminal-overload selector.

For each connected-B maximum cut and each vertex v with K2T residual R[v]<0,
compute the exact terminal-overload quantities

    Omega_{L,-}(v), Omega_{L,+}(v)

from the row atoms, choose the peak normalized bundle Omega/(L*m_L), form the
corresponding prefix/suffix union S, and test whether S is neutral,
B-connected after flipping, terminal-shadow valid, and has Psi>0.

This tests the proposed "peak terminal-overload lemma" directly.  It is a
diagnostic gate, not a proof artifact.
"""

import argparse
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_bundle_moat_gate import brute_maxcut_sides


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def peak_bundle(n, st, v):
    _M, ell, T, _mu, cyc = st
    bundles = {}
    mass = Counter()
    for f, paths in cyc.items():
        L = ell[f]
        mu = F(1, len(paths))
        for path in paths:
            if v not in path:
                continue
            idx = path.index(v)
            mass[L] += mu
            for sign, interval in (
                ("-", path[: idx + 1]),
                ("+", path[idx:]),
            ):
                key = (L, sign)
                if key not in bundles:
                    bundles[key] = {"omega": [F(0) for _ in range(n)], "mask": 0}
                for x in interval:
                    bundles[key]["omega"][x] += mu
                    bundles[key]["mask"] |= 1 << x

    best = None
    rows = []
    for (L, sign), data in bundles.items():
        m = mass[L]
        if m <= 0:
            continue
        omega = data["omega"]
        omega_sum = sum(omega[x] * (T[x] - n) for x in range(n))
        Omega = omega_sum - F(m, 2) * (T[v] - n)
        score = Omega / (L * m)
        rows.append((score, Omega, L, sign, data["mask"], m))
        if best is None or score > best[0] or (score == best[0] and (L, sign, data["mask"]) < (best[2], best[3], best[4])):
            best = (score, Omega, L, sign, data["mask"], m)
    return best, sorted(rows, reverse=True)


def scan_cut(name, n, adj, side, acc):
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
        acc["neg"] += 1
        best, rows = peak_bundle(n, st, v)
        if best is None:
            acc["fail"] += 1
            acc["status"]["no-peak"] += 1
            if acc["first"] is None:
                acc["first"] = (name, n, "".join(map(str, side)), v, str(rv), "no-peak")
            continue
        score, Omega, L, sign, mask, m = best
        if Omega <= 0:
            acc["fail"] += 1
            acc["status"]["nonpositive-peak"] += 1
            if acc["first"] is None:
                acc["first"] = (name, n, "".join(map(str, side)), v, str(rv), "peak", str(score), str(Omega), L, sign)
            continue

        peak_rows = [row for row in rows if row[0] == score]
        row_statuses = []
        status = "no-good-peak"
        for _score, _Omega, L0, sign0, mask0, m0 in peak_rows:
            delta = boundary_delta(n, adj, side, mask0)
            if delta != 0:
                st0 = "nonneutral"
                psi0 = None
            elif not Bconn(n, adj, flip_side(side, mask0)):
                st0 = "disconnect"
                psi0 = None
            else:
                det = terminal_shadow_details(n, adj, side, st, mask0)
                if det is None:
                    st0 = "not-terminal"
                    psi0 = None
                elif det["psi"] <= 0:
                    st0 = "nonpositive-psi"
                    psi0 = det["psi"]
                else:
                    st0 = "ok"
                    psi0 = det["psi"]
            row_statuses.append((st0, L0, sign0, mask0, delta, psi0, m0, _Omega))
            if st0 == "ok":
                status = "ok"

        acc["status"][status] += 1
        acc["peak_L"][(L, sign)] += 1
        if status != "ok":
            acc["fail"] += 1
            if acc["first"] is None:
                acc["first"] = dict(
                    name=name,
                    n=n,
                    side="".join(map(str, side)),
                    v=v,
                    R=str(rv),
                    status=status,
                    score=str(score),
                    Omega=str(Omega),
                    L=L,
                    sign=sign,
                    m=str(m),
                    S=mask_tuple(n, mask),
                    peak_status=[
                        (st0, l0, sg0, mask_tuple(n, ma0), de0, ps0, str(mm0), str(om0))
                        for st0, l0, sg0, ma0, de0, ps0, mm0, om0 in row_statuses
                    ],
                    top=[(str(s), str(o), l, sg, mask_tuple(n, ma), str(mm)) for s, o, l, sg, ma, mm in rows[:6]],
                )


def scan_graph_allmax(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    args = parser.parse_args()

    acc = {"neg": 0, "fail": 0, "first": None, "status": Counter(), "peak_L": Counter()}
    for nn in range(args.min_n, args.max_n + 1):
        before = acc["neg"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph_allmax("cen%d" % nn, n, edges, acc)
            if acc["first"] is not None:
                break
        print("N=%d neg=%d fail=%d" % (nn, acc["neg"] - before, acc["fail"]), flush=True)
        if acc["first"] is not None:
            break

    if args.h2_allmax and acc["first"] is None:
        n, edges, _side = h_blowup(2)
        adj = adj_from_edges(n, edges)
        _best, sides = brute_maxcut_sides(n, adj)
        before = acc["neg"]
        for side in sides:
            scan_cut("H?AFBo][2]-allmax", n, adj, side, acc)
            if acc["first"] is not None:
                break
        print("H2-allmax neg=%d fail=%d" % (acc["neg"] - before, acc["fail"]), flush=True)

    for t in range(2, args.h_inherited + 1):
        if acc["first"] is not None:
            break
        n, edges, side = h_blowup(t)
        before = acc["neg"]
        scan_cut("H?AFBo][%d]-inherited" % t, n, adj_from_edges(n, edges), side, acc)
        print("H%d-inherited neg=%d fail=%d" % (t, acc["neg"] - before, acc["fail"]), flush=True)

    print("=" * 72)
    print("negative vertices:", acc["neg"])
    print("status:", dict(acc["status"]))
    print("peak_L:", dict(acc["peak_L"]))
    print("fail:", acc["fail"], acc["first"] or "")
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
