"""Independent exact-rational audit of P13's variational countermodel."""

from fractions import Fraction as F


def integral_poly(coeffs: list[F], lo: F, hi: F) -> F:
    total = F(0)
    for degree, coefficient in enumerate(coeffs):
        total += coefficient * (hi ** (degree + 1) - lo ** (degree + 1)) / (degree + 1)
    return total


def main() -> None:
    half = F(1, 2)
    one = F(1)
    three_halves = F(3, 2)
    five_halves = F(5, 2)

    # Difference density a(t)=1-t on [0,1].
    mass_a = integral_poly([one, -one], F(0), one)

    # Shifted-sum density b(t), two affine pieces.
    mass_b = integral_poly([-F(1, 4), half], half, three_halves)
    mass_b += integral_poly([F(5, 4), -half], three_halves, five_halves)
    assert mass_a == mass_b == half

    # Exact overlap integral on [1/2,1].
    # (1-t)(t-1/2)/2 = -t^2/2 + 3t/4 - 1/4.
    overlap = integral_poly([-F(1, 4), F(3, 4), -half], half, one)
    assert overlap == F(1, 96)

    # Each affine piece of a+b attains its maximum at an endpoint.
    pieces = [
        ([one, -one], F(0), half),
        ([F(3, 4), -half], half, one),
        ([-F(1, 4), half], one, three_halves),
        ([F(5, 4), -half], three_halves, five_halves),
    ]
    maxima = []
    for coeffs, lo, hi in pieces:
        values = [sum(c * x**i for i, c in enumerate(coeffs)) for x in (lo, hi)]
        maxima.append(max(values))
    assert max(maxima) <= one

    # Boundary g=0 moment identity: density 1-t/2 on [0,2].
    for r in range(11):
        moment = integral_poly([F(0)] * r + [one, -half], F(0), F(2))
        expected = F(2 ** (r + 1), (r + 1) * (r + 2))
        assert moment == expected

    # Continuum lag-window formulas at exact rational alpha values.
    for denominator in range(1, 21):
        for numerator in range(denominator + 1):
            alpha = F(numerator, denominator)
            mass = alpha - alpha**2 / 2
            first_moment = alpha**2 / 2 - alpha**3 / 3
            assert mass >= 0
            assert first_moment <= alpha**2 / 2

    print(
        {
            "mass_difference": str(mass_a),
            "mass_shifted_sum": str(mass_b),
            "overlap": str(overlap),
            "max_combined_density": str(max(maxima)),
            "moments_checked": 11,
            "lag_values_checked": sum(d + 1 for d in range(1, 21)),
        }
    )


if __name__ == "__main__":
    main()
