#include <eclib/points.h>

#include <cstdlib>
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    const long precision = argc == 2 ? std::strtol(argv[1], nullptr, 10) : 400;
    if (precision < 100) {
        std::cerr << "precision must be at least 100 bits\n";
        return 2;
    }

    set_precision(precision);
    initprimes("PRIMES", 0);
    Curvedata curve(
        ZZ(0), ZZ(2568913), ZZ(0), ZZ(1535181310080LL),
        ZZ(59427518261760000LL), 0
    );

    Point q0(curve, ZZ(3160080), ZZ(-7881690960LL), ZZ(1));
    Point q1(curve, ZZ(827640), ZZ(1912224600LL), ZZ(1));
    Point q2(curve, ZZ(-28512), ZZ(-133122528), ZZ(1));
    // eclib uses ordinary P^2 coordinates [X:Y:Z], so rational affine
    // coordinates use one common denominator rather than weighted scaling.
    Point tb(curve, ZZ(453076470), ZZ(1708010515035LL), ZZ(2744));
    Point td(curve, ZZ(3432198000LL), ZZ(12245462235600LL), ZZ(343));
    Point tg(curve, ZZ(3160080), ZZ(7881690960LL), ZZ(1));

    std::vector<Point> candidates{q0, q1, q2};
    std::cout << std::boolalpha;
    std::cout << "precision_bits " << precision << "\n";
    std::cout << "candidate_points_valid "
              << (q0.isvalid() && q1.isvalid() && q2.isvalid()) << "\n";
    std::cout << "relation_points_valid "
              << (tb.isvalid() && td.isvalid() && tg.isvalid()) << "\n";
    for (int row = 0; row < 3; ++row) {
        std::cout << "candidate_height_row_" << (row + 1);
        for (int column = 0; column < 3; ++column) {
            std::cout << " "
                      << height_pairing(candidates[row], candidates[column]);
        }
        std::cout << "\n";
    }
    std::cout << "candidate_regulator " << regulator(candidates) << "\n";
    std::cout << "half_relation_Q1 " << (2 * q1 == tb + tg) << "\n";
    std::cout << "half_relation_Q2 " << (2 * q2 == tg - td) << "\n";
    std::cout << "base_relation_Q0 " << (q0 == -tg) << "\n";

    std::vector<Point> torsion = torsion_points(curve);
    std::cout << "torsion_size " << torsion.size() << "\n";
    for (std::size_t index = 0; index < torsion.size(); ++index) {
        Point point = torsion[index];
        std::cout << "torsion_" << index << " " << point
                  << " order " << order(point) << "\n";
    }
    return 0;
}
