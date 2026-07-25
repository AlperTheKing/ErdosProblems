"""Q5 (a)+(b): exact bip, exact tau* (odd-cycle covering LP) with two-sided
rational certificates, on C5[n] n=1..5 and the four named extremal graphs."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *

NAMED = [
    ("N12a", "K?ABBBwerwBw"),
    ("N12b", "K?BD@g]Qvo^?"),
    ("N13", "L??ED@_~?~^_Fw"),
    ("N14", "M?AE@bH{AYN_LgBs?"),
]


def report(name, n, adj, do_bip=True):
    E = edges_of(n, adj)
    tf = is_triangle_free(n, adj)
    line = f"{name}: N={n} |E|={len(E)} tri-free={tf}"
    b = None
    if do_bip:
        t0 = time.time()
        b, S = bip_exact(n, adj)
        line += f" bip={b} (cut mask {S}, {time.time()-t0:.1f}s)"
    t0 = time.time()
    r = tau_star(n, adj)
    ts = r["value"]
    line += f" tau*={ts} ({float(ts):.6f}) rounds={r['rounds']} {time.time()-t0:.1f}s"
    w = {e: Fraction(1) for e in E}
    okc, infoc = verify_cover(n, adj, r["cover"])
    okp, totp = verify_packing(n, adj, r["packing"], w)
    assert okc, ("cover fail", infoc)
    assert okp, ("packing fail", totp)
    assert totp == ts, ("packing value mismatch", totp, ts)
    line += f" [cover+packing certified exactly, both = {ts}]"
    if b is not None:
        line += f" GAP bip-tau* = {Fraction(b) - ts}"
        line += f" ; N^2/25 = {Fraction(n*n,25)} ({n*n/25:.4f})"
    print(line, flush=True)
    return b, ts, r


if __name__ == "__main__":
    print("=== C5[n] ===")
    for k in range(1, 5):            # n=5 (N=25) handled in C++
        n, adj = blowup_C5(k)
        b, ts, r = report(f"C5[{k}]", n, adj)
        assert b == k * k, ("bip(C5[n]) != n^2", k, b)
        assert ts == k * k, ("tau*(C5[n]) != n^2", k, ts)
    print()
    print("=== named extremal graphs ===")
    store = {}
    for name, g6 in NAMED:
        n, adj = g6_decode(g6)
        b, ts, r = report(name, n, adj)
        store[name] = (n, adj, b, ts, r)
    print()
    print("=== exact optimal fractional covers (support) ===")
    for name in store:
        n, adj, b, ts, r = store[name]
        supp = {e: v for e, v in r["cover"].items() if v != 0}
        print(f"{name}: |supp(z)|={len(supp)} values={sorted(set(supp.values()))}")
        print(f"   z = {supp}")
        print(f"   packing y ({len(r['packing'])} cycles) = "
              f"{[(c, str(v)) for c, v in r['packing']]}")
