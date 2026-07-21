#include <eclib/points.h>

#include <array>
#include <climits>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr long long SCALE = 1'000'000'000'000LL;
constexpr long long HEIGHT_BOUND = 1'000LL;
constexpr int COORDINATE_BOUND = 55;
constexpr long long HEIGHT_MATRIX[4][4] = {
    {3066644681814LL, -1604217266982LL, 2304106286354LL, -2647588945619LL},
    {-1604217266982LL, 4852120801592LL, 2186366222773LL, -805702796450LL},
    {2304106286354LL, 2186366222773LL, 8991728418553LL, -4979765774895LL},
    {-2647588945619LL, -805702796450LL, -4979765774895LL, 4515819823940LL},
};

struct Rational {
    bigint numerator;
    bigint denominator;

    Rational(bigint num, bigint den) : numerator(num), denominator(den) {
        if (denominator == 0) {
            throw std::runtime_error("zero rational denominator");
        }
        if (denominator < 0) {
            numerator = -numerator;
            denominator = -denominator;
        }
        bigint divisor = gcd(numerator, denominator);
        if (divisor < 0) {
            divisor = -divisor;
        }
        numerator /= divisor;
        denominator /= divisor;
    }
};

bool rational_square(const Rational& value, Rational* root = nullptr) {
    if (value.numerator < 0) {
        return false;
    }
    bigint numerator_root;
    bigint denominator_root;
    SqrRoot(numerator_root, value.numerator);
    SqrRoot(denominator_root, value.denominator);
    if (
        numerator_root * numerator_root != value.numerator
        || denominator_root * denominator_root != value.denominator
    ) {
        return false;
    }
    if (root != nullptr) {
        *root = Rational(numerator_root, denominator_root);
    }
    return true;
}

bool equal_rational(const Rational& value, long numerator, long denominator) {
    return value.numerator * denominator == bigint(numerator) * value.denominator;
}

Rational compatibility_value(
    const bigint& projective_x,
    const bigint& projective_z,
    long constant_numerator,
    long constant_denominator
) {
    // h = 7*X/(5078700*Z), so c*h+1 is the rational below.
    const bigint numerator =
        bigint(7 * constant_numerator) * projective_x
        + bigint(5'078'700LL * constant_denominator) * projective_z;
    const bigint denominator =
        bigint(5'078'700LL * constant_denominator) * projective_z;
    return Rational(numerator, denominator);
}

long long proxy_height(const std::array<int, 4>& vector) {
    __int128 result = 0;
    for (int row = 0; row < 4; ++row) {
        for (int column = 0; column < 4; ++column) {
            result += static_cast<__int128>(vector[row])
                * HEIGHT_MATRIX[row][column] * vector[column];
        }
    }
    if (result < 0 || result > INT64_MAX) {
        throw std::runtime_error("proxy height overflow or loss of positivity");
    }
    return static_cast<long long>(result);
}

std::string rational_text(const Rational& value) {
    std::ostringstream stream;
    stream << value.numerator;
    if (value.denominator != 1) {
        stream << "/" << value.denominator;
    }
    return stream.str();
}

bool is_fixed_value(const Rational& value) {
    constexpr long fixed[6][2] = {
        {243, 560},
        {1147, 5040},
        {1100, 63},
        {7820, 567},
        {95, 112},
        {196, 45},
    };
    for (const auto& item : fixed) {
        if (equal_rational(value, item[0], item[1])) {
            return true;
        }
    }
    return false;
}

}  // namespace

int main() {
    set_precision(200);
    initprimes("PRIMES", 0);
    Curvedata curve(
        ZZ(0), ZZ(2568913), ZZ(0), ZZ(1535181310080LL),
        ZZ(59427518261760000LL), 0
    );
    std::array<Point, 4> basis = {
        Point(curve, ZZ(-861840), ZZ(65622960), ZZ(1)),
        Point(curve, ZZ(-860928), ZZ(60830400), ZZ(1)),
        Point(curve, ZZ(-855520), ZZ(10311840), ZZ(1)),
        Point(curve, ZZ(-1506120), ZZ(-397614360), ZZ(1)),
    };
    Point torsion(curve, ZZ(-1672000), ZZ(0), ZZ(1));

    std::array<std::vector<Point>, 4> multiples;
    for (int coordinate = 0; coordinate < 4; ++coordinate) {
        multiples[coordinate].reserve(2 * COORDINATE_BOUND + 1);
        for (
            int coefficient = -COORDINATE_BOUND;
            coefficient <= COORDINATE_BOUND;
            ++coefficient
        ) {
            multiples[coordinate].push_back(coefficient * basis[coordinate]);
        }
    }

    std::uint64_t lattice_vectors = 0;
    std::uint64_t nonzero_distinct = 0;
    std::uint64_t passed_b = 0;
    std::uint64_t passed_bd = 0;
    std::uint64_t candidates = 0;

    for (int k1 = -55; k1 <= 55; k1 += 2) {
        for (int k2 = -55; k2 <= 55; k2 += 2) {
            for (int k3 = -55; k3 <= 55; k3 += 2) {
                for (int k4 = -54; k4 <= 54; k4 += 2) {
                    const std::array<int, 4> vector = {k1, k2, k3, k4};
                    const long long q12 = proxy_height(vector);
                    if (q12 > HEIGHT_BOUND * SCALE) {
                        continue;
                    }
                    ++lattice_vectors;

                    Point point = torsion;
                    point += multiples[0][k1 + COORDINATE_BOUND];
                    point += multiples[1][k2 + COORDINATE_BOUND];
                    point += multiples[2][k3 + COORDINATE_BOUND];
                    point += multiples[3][k4 + COORDINATE_BOUND];
                    if (point.is_zero() || !point.isvalid()) {
                        std::cerr << "invalid enumerated point at [" << k1 << ","
                                  << k2 << "," << k3 << "," << k4 << "]\n";
                        return 3;
                    }

                    const bigint projective_x = point.getX();
                    const bigint projective_y = point.getY();
                    const bigint projective_z = point.getZ();
                    Rational h(bigint(7) * projective_x, bigint(5'078'700) * projective_z);
                    if (h.numerator == 0 || is_fixed_value(h)) {
                        continue;
                    }
                    ++nonzero_distinct;

                    Rational root_b(bigint(0), bigint(1));
                    Rational root_d(bigint(0), bigint(1));
                    Rational root_g(bigint(0), bigint(1));
                    if (!rational_square(
                            compatibility_value(projective_x, projective_z, 1147, 5040),
                            &root_b
                        )) {
                        continue;
                    }
                    ++passed_b;
                    if (!rational_square(
                            compatibility_value(projective_x, projective_z, 7820, 567),
                            &root_d
                        )) {
                        continue;
                    }
                    ++passed_bd;
                    if (!rational_square(
                            compatibility_value(projective_x, projective_z, 196, 45),
                            &root_g
                        )) {
                        continue;
                    }
                    ++candidates;

                    std::cout << "{\"type\":\"candidate\",\"k\":["
                              << k1 << "," << k2 << "," << k3 << "," << k4
                              << "],\"q12\":" << q12 << ",\"point\":[\""
                              << projective_x << "\",\"" << projective_y << "\",\""
                              << projective_z << "\"],\"h\":\"" << rational_text(h)
                              << "\",\"roots_bdg\":[\"" << rational_text(root_b)
                              << "\",\"" << rational_text(root_d) << "\",\""
                              << rational_text(root_g) << "\"]}\n";
                }
            }
        }
    }

    std::cout << "{\"type\":\"summary\",\"status\":\""
              << (candidates == 0 ? "NO_HIT" : "HIT")
              << "\",\"lattice_vectors\":" << lattice_vectors
              << ",\"nonzero_distinct\":" << nonzero_distinct
              << ",\"passed_b\":" << passed_b
              << ",\"passed_bd\":" << passed_bd
              << ",\"candidates\":" << candidates << "}\n";
    return 0;
}
