"""Exact aggregate/max-cut audit for the archived R29 description.

No floating point.  The traffic-block quotient exhausts all switches up to
permutations of the 26 leaves on each shore.  The other four bounds are the
standard odd-cycle bound, the archived circuit deficit, and |E|.
"""
from itertools import product
import json

T = 26


def traffic_loss(hr, hcl, hcr, p, q):
    """Loss of the displayed cut after a switch in the t=t=26 traffic block.

    p,q are the numbers of switched left/right leaves.  Each leaf has exactly
    t private length-3 lock arms.  Conditional on its endpoints, each arm can
    lose at most/ exactly one cut edge when the leaf is switched relative to
    the common anchor.  The formula is therefore exact after optimizing all
    internal lock vertices.
    """
    lock_loss = T * (p + q)
    blue_core_delta = (hr != hcl) + (hr != hcr)
    blue_core_delta += (T - p if hcl else p)
    blue_core_delta += (T - q if hcr else q)
    bad_gain = p * (T - q) + (T - p) * q
    return lock_loss + int(blue_core_delta) - bad_gain


def main():
    minimum = None
    minimizers = []
    checked = 0
    for hr, hcl, hcr in product((0, 1), repeat=3):
        for p in range(T + 1):
            for q in range(T + 1):
                loss = traffic_loss(hr, hcl, hcr, p, q)
                checked += 1
                state = [hr, hcl, hcr, p, q]
                if minimum is None or loss < minimum:
                    minimum, minimizers = loss, [state]
                elif loss == minimum:
                    minimizers.append(state)
    assert checked == 8 * 27 * 27
    assert minimum == 0

    edge_counts = [4786, 3380, 15, 235, 6]
    upper_bounds = [4110, 2704, 12, 207, 6]
    deficits = [e - u for e, u in zip(edge_counts, upper_bounds)]
    assert edge_counts[0] == (T*T) + (2 + 2*T) + 3*(2*T*T)
    assert upper_bounds[0] == (2 + 2*T) + 3*(2*T*T)
    assert edge_counts[1] == 676*5 and upper_bounds[1] == 676*4
    assert edge_counts[2] == 3*5 and upper_bounds[2] == 3*4
    assert sum(edge_counts) == 8422
    assert sum(upper_bounds) == 7039
    assert deficits == [676, 676, 3, 28, 0]

    result = {
        "arithmetic": "integer-only",
        "traffic_quotient_states": checked,
        "traffic_min_switch_loss": minimum,
        "traffic_minimizer_count": len(minimizers),
        "traffic_first_minimizers": minimizers[:20],
        "class_edge_counts": edge_counts,
        "class_upper_bounds": upper_bounds,
        "class_deficits": deficits,
        "edge_total": sum(edge_counts),
        "upper_bound_total": sum(upper_bounds),
        "conditional_verdict": "maxcut<=7039 if the advertised incidence partition and circuit deficit-28 certificate hold",
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
