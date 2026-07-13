#!/usr/bin/env python3
"""Exact checker for the ActiveScoped hub-shore Boolean quotient."""
from itertools import product

def available(r, shore):
    x, _y, half, free, companion, edge, active_x = r
    return free and (x in shore or companion) and not (half == 0 and edge and active_x)

def reach(records, shore):
    return frozenset(r[:3] for r in records if available(r, shore))

def self_test():
    W = {0, 1, 2}
    for x_in, half, free, companion, edge, active in product((0, 1), repeat=6):
        x = 0 if x_in else 9
        r = (x, 10, half, free, companion, edge, active)
        expected = bool(free and (x_in or companion) and not (half == 0 and edge and active))
        assert available(r, W) == expected
    assert len(reach([(9,10,1,0,1,0,0)], W)) == 0
    assert len(reach([(9,10,1,1,1,0,0)], W)) == 1
    assert len(reach([(9,10,1,1,0,0,0)], W)) == 0
    assert len(reach([(0,10,0,1,0,1,1)], W)) == 0
    assert len(reach([(0,10,0,1,0,1,0)], W)) == 1
    print("PASS boolean quotient: 64/64")
    print("PASS minimal witnesses: free, eligibility, reservation")

if __name__ == "__main__": self_test()
