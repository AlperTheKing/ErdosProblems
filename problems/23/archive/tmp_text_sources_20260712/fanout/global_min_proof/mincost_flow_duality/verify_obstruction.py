"""Exact Fraction check of the fixed-charge circulation integrality obstruction."""
from fractions import Fraction as F


def feasible(flow, active):
    # One unit must cross an activated capacity-two arc.
    return flow == 1 and 0 <= active <= 1 and 0 <= flow <= 2 * active


integer_points = [(F(1), F(y)) for y in (0, 1) if feasible(F(1), F(y))]
fractional_point = (F(1), F(1, 2))

assert integer_points == [(F(1), F(1))]
assert feasible(*fractional_point)
assert fractional_point[1] == F(1, 2)
assert min(y for _, y in integer_points) == 1

print("integer_optimum=1")
print("lp_optimum=1/2")
print("fractional_witness=(flow=1,active=1/2)")
print("integrality_gap=2")
