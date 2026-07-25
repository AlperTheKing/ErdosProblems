"""H5: exact CP-SAT certification of the champion graphs at N = 49, 51, 74, 76
(plus the C5[10] N=50 control).  Every number printed is re-verified by direct counting.

usage: python h5_certify.py [model] [max_time_seconds]
"""
import sys, json, time
from h5_core import (adj_from_edges, edges_from_adj, is_triangle_free, triangle_witness,
                     certify, g6, cut_value, from_g6)


def c5_blowup(parts):
    n = sum(parts)
    blocks, s = [], 0
    for p in parts:
        blocks.append(list(range(s, s + p)))
        s += p
    edges = [(u, v) for i in range(5) for u in blocks[i] for v in blocks[(i + 1) % 5]]
    return n, adj_from_edges(n, edges)


CASES = [
    ("C5[10,10,10,10,10]  N=50 control", [10, 10, 10, 10, 10], 100),
    ("C5[10,10,10,10,9]   N=49",         [10, 10, 10, 10, 9],  90),
    ("C5[9,10,9,10,11]    N=49",         [9, 10, 9, 10, 11],   90),
    ("C5[11,10,10,10,10]  N=51",         [11, 10, 10, 10, 10], 100),
    ("C5[14,15,14,15,16]  N=74",         [14, 15, 14, 15, 16], 210),
    ("C5[16,15,15,15,15]  N=76",         [16, 15, 15, 15, 15], 225),
]


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "xor"
    tmax = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
    out = []
    for label, parts, expect in CASES:
        n, adj = c5_blowup(parts)
        t0 = time.time()
        r = certify(n, adj, label=label, workers=48, max_time=tmax, model=model,
                    heur_restarts=200)
        r["seconds"] = round(time.time() - t0, 1)
        r["expected_bip"] = expect
        r["matches_structural_formula"] = (r["bip"] == expect)
        # independent structural value: bip of a blow-up = min_i n_i n_{i+1}
        r["min_adjacent_part_product"] = min(parts[i] * parts[(i + 1) % 5] for i in range(5))
        print(f"    -> status={r['status']} bip={r['bip']} expected={expect} "
              f"formula={r['min_adjacent_part_product']} "
              f"25bip={25*r['bip']} N^2={n*n} "
              f"{'VIOLATION' if r['violates'] else 'consistent'} ({r['seconds']}s)",
              flush=True)
        out.append(r)
    with open("h5_certificates.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    print("\nwrote h5_certificates.json")


if __name__ == "__main__":
    main()
