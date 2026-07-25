"""Exact CP-SAT certification of an arbitrary graph6 string (or file of them).

usage: python h5_certify_g6.py <g6 or @file> [max_time] [model]
Prints, for each graph: triangle-freeness, |E|, the CP-SAT status, the proven maximum cut
(re-counted directly from the returned 2-colouring), bip, and 25*bip vs N^2.
"""
import sys, json
from h5_core import from_g6, certify, edges_from_adj


def main():
    arg = sys.argv[1]
    tmax = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
    model = sys.argv[3] if len(sys.argv) > 3 else "xor"
    if arg.startswith("@"):
        strings = [l.strip() for l in open(arg[1:]) if l.strip()]
    else:
        strings = [arg]
    out = []
    for s in strings:
        n, adj = from_g6(s)
        r = certify(n, adj, label=s[:24], workers=48, max_time=tmax, model=model,
                    heur_restarts=400)
        r["g6"] = s
        print(f"   status={r['status']} m={r['m']} maxcut={r['maxcut']} bip={r['bip']} "
              f"25bip={25*r['bip']} N^2={n*n} "
              f"{'*** VIOLATION ***' if r['violates'] else 'consistent'}", flush=True)
        out.append(r)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
