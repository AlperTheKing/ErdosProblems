"""fam2 -- EXHAUSTIVE tier-0 census, r=5 (len(nu)==5), |nu| <= NMAX.

Decision path is the mandated LP-free instrument: every triple goes through
tier0_screen.screen_triples (exact profile from engine A, exact Newton
interpolation, two held-out points, exact h*).  NOTHING is filtered by an LP
oracle or a simplex test.

The ONLY enumeration restriction is lam subset nu and mu subset nu, which is
an exact theorem (c(nu;lam,mu) != 0 => lam,mu subset nu); it is audited
separately by fam2_audit_containment.py.
"""
import sys, os, json, time, argparse
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0")
from fam2_enum import parts_exact5, triples_for_nu
import tier0_screen as T

CHUNK = 3000


def lattice_violations(h, d):
    """Inequalities that are THEOREMS for lattice polytopes.  Any violation
    certifies that Q is NOT a lattice polytope."""
    v = []
    if d >= 1:
        if h[d] > h[1]:
            v.append("hstar_d_gt_hstar_1")
        # Hibi lower bound: if there is an interior lattice point then
        # h*_1 <= h*_i for 1 <= i <= d-1
        if h[d] > 0:
            for i in range(1, d):
                if h[i] < h[1]:
                    v.append("hibi_lower_%d" % i)
                    break
    # Stanley monotonicity: sum_{j<=i} h*_j <= sum_{j>=s-i} h*_j , s=deg h*
    s = max([j for j in range(len(h)) if h[j] != 0] or [0])
    pre = 0
    for i in range(0, s + 1):
        pre += h[i]
        suf = sum(h[s - i:s + 1])
        if pre > suf:
            v.append("stanley_%d" % i)
            break
    if any(x < 0 for x in h):
        v.append("hstar_negative")
    return v


def new_agg():
    return {
        "n_triples": 0,
        "status": Counter(),
        "d": Counter(),
        "d_c": Counter(),
        "d_margin": Counter(),        # margin = h*_1 - h*_d
        "d_hsum": Counter(),
        "d_h1": Counter(),
        "d_hd": Counter(),
        "min_margin": None, "min_margin_trip": None,
        "min_margin_d2": None, "min_margin_d2_trip": None,
        "min_margin_d4": None, "min_margin_d4_trip": None,
        "max_hd": None, "max_hd_trip": None,
        "max_hd_d4": None, "max_hd_d4_trip": None,
        "n_h1_zero": 0,
        "n_h1_zero_by_d": Counter(),
        "max_hd_given_h1_zero": None, "max_hd_given_h1_zero_trip": None,
        "n_nonlattice_cert": 0,
        "nonlattice_kinds": Counter(),
        "n_moment_inconsistent": 0,
        "n_audit_fail": 0,
        "hits": [],
        "anomalies": [],
    }


def merge(a, b):
    a["n_triples"] += b["n_triples"]
    for k in ("status", "d", "d_c", "d_margin", "d_hsum", "d_h1", "d_hd",
              "n_h1_zero_by_d", "nonlattice_kinds"):
        a[k].update(b[k])
    for k in ("n_h1_zero", "n_nonlattice_cert", "n_moment_inconsistent",
              "n_audit_fail"):
        a[k] += b[k]
    for k in ("min_margin", "min_margin_d2", "min_margin_d4"):
        if b[k] is not None and (a[k] is None or b[k] < a[k]):
            a[k] = b[k]; a[k + "_trip"] = b[k + "_trip"]
    for k in ("max_hd", "max_hd_d4"):
        if b[k] is not None and (a[k] is None or b[k] > a[k]):
            a[k] = b[k]; a[k + "_trip"] = b[k + "_trip"]
    if b["max_hd_given_h1_zero"] is not None and (
            a["max_hd_given_h1_zero"] is None or
            b["max_hd_given_h1_zero"] > a["max_hd_given_h1_zero"]):
        a["max_hd_given_h1_zero"] = b["max_hd_given_h1_zero"]
        a["max_hd_given_h1_zero_trip"] = b["max_hd_given_h1_zero_trip"]
    a["hits"].extend(b["hits"])
    a["anomalies"].extend(b["anomalies"])
    return a


def clip(x, lo=-64, hi=64):
    if x is None: return None
    return x if lo <= x <= hi else ("<%d" % lo if x < lo else ">%d" % hi)


def do_nu(nu):
    agg = new_agg()
    trips = triples_for_nu(nu)
    agg["n_triples"] = len(trips)
    for i in range(0, len(trips), CHUNK):
        block = [(list(l), list(m), list(v)) for (l, m, v) in trips[i:i + CHUNK]]
        recs = None
        for attempt in range(10):
            try:
                recs = T.screen_triples(block); break
            except (PermissionError, OSError):
                time.sleep(0.5 * (attempt + 1))
        if recs is None:
            recs = T.screen_triples(block)   # last try, let it raise
        for r in recs:
            st = r["status"]
            agg["status"][st] += 1
            if st in ("SATURATION_ANOMALY", "HELDOUT_MISMATCH", "SIZE_MISMATCH"):
                agg["anomalies"].append(r)
                continue
            if st != "OK":
                continue
            d = r["d"]; c = r["c"]; h = r["hstar"]
            agg["d"][d] += 1
            agg["d_c"][(d, clip(c, 0, 64))] += 1
            agg["d_hsum"][(d, clip(r["hstar_sum"], 0, 64))] += 1
            if not (r["hstar_roundtrip_ok"] and r["heldout_ok"] and
                    r["hstar_tail_zero"] and r["hstar_1_identity_ok"] and
                    r["interior_check_ok"] and r["hstar_0_is_1"]):
                agg["n_audit_fail"] += 1
                agg["anomalies"].append(r)
            if not r["moment_criteria_consistent"]:
                agg["n_moment_inconsistent"] += 1
                agg["anomalies"].append(r)
            trip = [r["lam"], r["mu"], r["nu"]]
            if d >= 1:
                h1 = r["hstar_1"]; hd = r["hstar_d"]
                marg = h1 - hd
                agg["d_margin"][(d, clip(marg))] += 1
                agg["d_h1"][(d, clip(h1))] += 1
                agg["d_hd"][(d, clip(hd, 0, 64))] += 1
                if agg["min_margin"] is None or marg < agg["min_margin"]:
                    agg["min_margin"] = marg; agg["min_margin_trip"] = trip
                if agg["max_hd"] is None or hd > agg["max_hd"]:
                    agg["max_hd"] = hd; agg["max_hd_trip"] = trip
                if d >= 2 and (agg["min_margin_d2"] is None or marg < agg["min_margin_d2"]):
                    agg["min_margin_d2"] = marg; agg["min_margin_d2_trip"] = trip
                if d >= 4:
                    if agg["min_margin_d4"] is None or marg < agg["min_margin_d4"]:
                        agg["min_margin_d4"] = marg; agg["min_margin_d4_trip"] = trip
                    if agg["max_hd_d4"] is None or hd > agg["max_hd_d4"]:
                        agg["max_hd_d4"] = hd; agg["max_hd_d4_trip"] = trip
                if h1 == 0:
                    agg["n_h1_zero"] += 1
                    agg["n_h1_zero_by_d"][d] += 1
                    if agg["max_hd_given_h1_zero"] is None or hd > agg["max_hd_given_h1_zero"]:
                        agg["max_hd_given_h1_zero"] = hd
                        agg["max_hd_given_h1_zero_trip"] = trip
            viol = lattice_violations(h, d)
            if viol:
                agg["n_nonlattice_cert"] += 1
                for v in viol: agg["nonlattice_kinds"][v] += 1
            if r["TIER0"] or r["JACKPOT"] or r["NEG"] or viol:
                rr = dict(r); rr["lattice_violations"] = viol
                agg["hits"].append(rr)
    return agg


def ser(agg):
    o = dict(agg)
    for k in ("status", "d", "n_h1_zero_by_d", "nonlattice_kinds"):
        o[k] = {str(a): b for a, b in agg[k].items()}
    for k in ("d_c", "d_margin", "d_hsum", "d_h1", "d_hd"):
        o[k] = {"%s|%s" % (a[0], a[1]): b for a, b in agg[k].items()}
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=26)
    ap.add_argument("--nmin", type=int, default=5)
    ap.add_argument("--workers", type=int, default=28)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    nus = []
    for N in range(a.nmin, a.nmax + 1):
        nus.extend(parts_exact5(N))
    nus.sort(key=lambda x: -sum(x))
    print("nu count", len(nus), flush=True)

    import multiprocessing as mp
    t0 = time.time()
    total = new_agg()
    done = 0
    with mp.Pool(a.workers) as pool:
        for agg in pool.imap_unordered(do_nu, nus, chunksize=1):
            merge(total, agg)
            done += 1
            if done % 50 == 0 or done == len(nus):
                print("%d/%d nu  triples=%d  %.0fs  min_margin=%s max_hd=%s hits=%d"
                      % (done, len(nus), total["n_triples"], time.time() - t0,
                         total["min_margin"], total["max_hd"], len(total["hits"])),
                      flush=True)
    with open(a.out, "w") as f:
        json.dump(ser(total), f, indent=1)
    print("WROTE", a.out, "elapsed %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
