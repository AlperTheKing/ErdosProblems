"""Exhaustive exact gate for small abstract 5-layer PMS profiles.

This complements `_codex_pms_matrix_random_gate.py` by enumerating all edge
subsets for every positive layer-size profile up to a requested total N,
subject to a cap on the number of optional edges.

The model is the OC-PMS five-layer abstraction:

  A0 -- A1 -- A2 -- A3 -- A4,  bad edges A4--A0.

The distinguished row uses vertex 0 in each layer; its four B-edges and bad
closing edge are forced.  All other admissible edges are optional.

For each instance:
  * every bad edge must have at least one length-4 B-path;
  * full cut-domination delta_M(S) <= delta_B(S) is checked for all S;
  * the PMS inequality is checked exactly.

This does not encode gamma-tie; it gates the cut-domination-only matrix
version.  A failure is a genuine counterexample to that stronger abstraction.
"""

from itertools import product
from fractions import Fraction as F
import sys

from _codex_pms_matrix_random_gate import edge_key, offsets, vid, pms_margin, cut_dominated


def compositions(n, k, minimum=1):
    if k == 1:
        if n >= minimum:
            yield (n,)
        return
    for first in range(minimum, n - minimum * (k - 1) + 1):
        for rest in compositions(n - first, k - 1, minimum):
            yield (first,) + rest


def profile_edges(sizes):
    off = offsets(sizes)
    fixed_B = set()
    fixed_M = {edge_key(vid(off, 4, 0), vid(off, 0, 0))}
    for layer in range(4):
        fixed_B.add(edge_key(vid(off, layer, 0), vid(off, layer + 1, 0)))

    opt_B = []
    for layer in range(4):
        for i in range(sizes[layer]):
            for j in range(sizes[layer + 1]):
                e = edge_key(vid(off, layer, i), vid(off, layer + 1, j))
                if e not in fixed_B:
                    opt_B.append(e)

    opt_M = []
    for i in range(sizes[4]):
        for j in range(sizes[0]):
            e = edge_key(vid(off, 4, i), vid(off, 0, j))
            if e not in fixed_M:
                opt_M.append(e)

    return off, fixed_B, fixed_M, opt_B, opt_M


def run(nmax=10, max_optional=18):
    acc = {
        "profiles": 0,
        "profiles_skipped": 0,
        "instances": 0,
        "path_ok": 0,
        "cd_ok": 0,
        "fail": 0,
        "first_fail": None,
        "min_margin": None,
        "min_ex": None,
    }

    for n in range(5, nmax + 1):
        for sizes in compositions(n, 5):
            off, fixed_B, fixed_M, opt_B, opt_M = profile_edges(sizes)
            opt = opt_B + opt_M
            acc["profiles"] += 1
            if len(opt) > max_optional:
                acc["profiles_skipped"] += 1
                continue
            b_count = len(opt_B)
            total = 1 << len(opt)
            for mask in range(total):
                B = set(fixed_B)
                M = set(fixed_M)
                for k, e in enumerate(opt):
                    if (mask >> k) & 1:
                        if k < b_count:
                            B.add(e)
                        else:
                            M.add(e)
                acc["instances"] += 1
                margin_data = pms_margin(sizes, off, B, M)
                if margin_data[0] is None:
                    continue
                margin, detail = margin_data
                acc["path_ok"] += 1
                ok, cutmask, db, dm = cut_dominated(n, B, M)
                if not ok:
                    continue
                acc["cd_ok"] += 1
                if acc["min_margin"] is None or margin < acc["min_margin"]:
                    acc["min_margin"] = margin
                    acc["min_ex"] = (sizes, len(B), len(M), detail, str(margin))
                if margin < 0:
                    acc["fail"] += 1
                    acc["first_fail"] = (
                        sizes,
                        sorted(B),
                        sorted(M),
                        detail,
                        str(margin),
                    )
                    return acc
        print(
            "done N=%d profiles=%d skipped=%d instances=%d path_ok=%d cd_ok=%d min=%s"
            % (
                n,
                acc["profiles"],
                acc["profiles_skipped"],
                acc["instances"],
                acc["path_ok"],
                acc["cd_ok"],
                acc["min_margin"],
            ),
            flush=True,
        )
    return acc


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    max_optional = int(sys.argv[2]) if len(sys.argv) > 2 else 18
    acc = run(nmax, max_optional)
    print("PMS 5-layer exhaustive matrix gate")
    for key in [
        "profiles",
        "profiles_skipped",
        "instances",
        "path_ok",
        "cd_ok",
        "fail",
    ]:
        print(key, acc[key])
    print("min_margin", acc["min_margin"], acc["min_ex"])
    if acc["first_fail"]:
        print("FIRST_FAIL", acc["first_fail"])
    print("VERDICT", "FAIL" if acc["fail"] else "no failure in exhaustive small profiles")
