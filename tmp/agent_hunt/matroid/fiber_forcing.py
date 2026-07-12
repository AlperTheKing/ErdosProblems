"""Fiber-intersection forced-tail-separator test (R50 sec 3-5 mechanism), exact.

For each zero-vector (owner v, active x0):
  fiber(y) = { (atom i, row) : i nonincident to v, v not in row, x0 in row, y in row }
  (y ranges over the t-1 support neighbours of v).
  A tail edge e in delta(x0) minus {vx0} is FIBER-FORCED if some y has fiber(y)
  nonempty and every row in fiber(y) uses e. (Then e is selected in EVERY profile
  realization: pair y must be covered by a fiber row, all of which carry e.)
Verdict FULL_BLANKET: every tail edge at x0 is fiber-forced -> active component of v
  is exactly {v, x0} in every realization -> intrinsic scope-vacuity with a pure
  row-family certificate (T5ForcedTailSeparator exists for this circuit).
"""

from __future__ import annotations

import json

from fixtures import load_all, adjacency, norm
from profiles import owner_table


def fiber_report(circ, v, x0):
    adj = adjacency(circ.n, circ.support)
    support_nbrs = [y for y in adj[v] if y != x0]
    incident = {i for i, a in enumerate(circ.atoms) if v in (a["u"], a["v"])}
    fibers = {}
    for y in support_nbrs:
        fib = []
        for i, a in enumerate(circ.atoms):
            if i in incident:
                continue
            for r in a["rows"]:
                if v not in r and x0 in r and y in r:
                    fib.append((i, r))
        fibers[y] = fib
    tail_edges = [norm(x0, z) for z in adj[x0] if z != v]
    forced = {}
    for e in tail_edges:
        witnesses = []
        for y, fib in fibers.items():
            if fib and all(e in {norm(r[k], r[k + 1]) for k in range(4)}
                           for _, r in fib):
                witnesses.append(y)
        forced[e] = witnesses
    full = all(forced[e] for e in tail_edges)
    return {
        "owner": v, "active": x0,
        "tailEdges": [list(e) for e in tail_edges],
        "fiberSizes": {str(y): len(fib) for y, fib in fibers.items()},
        "fiberForced": {str(e): ys for e, ys in forced.items()},
        "verdict": "FULL_BLANKET" if full else "NOT_FULLY_FORCED",
    }


def main():
    out = {}
    for name, c in load_all().items():
        if c.n == 0 or name == "r34deg":
            continue
        tab = owner_table(c)
        recs = []
        for w, actives in tab.items():
            for x, vec in actives.items():
                if vec == (0, 0, 0, 0):
                    recs.append(fiber_report(c, w, x))
        out[name] = recs
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
