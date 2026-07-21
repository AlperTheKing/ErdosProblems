#include <eclib/points.h>

#include <cstdlib>
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    const long precision = argc == 2 ? std::strtol(argv[1], nullptr, 10) : 200;
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
    std::vector<Point> basis;
    basis.emplace_back(curve, ZZ(-861840), ZZ(65622960), ZZ(1));
    basis.emplace_back(curve, ZZ(-860928), ZZ(60830400), ZZ(1));
    basis.emplace_back(curve, ZZ(-855520), ZZ(10311840), ZZ(1));
    basis.emplace_back(curve, ZZ(-1506120), ZZ(-397614360), ZZ(1));

    std::cout << "precision_bits " << precision << "\n";
    for (int row = 0; row < 4; ++row) {
        std::cout << "matrix_row_" << (row + 1);
        for (int column = 0; column < 4; ++column) {
            std::cout << " " << height_pairing(basis[row], basis[column]);
        }
        std::cout << "\n";
    }
    std::cout << "regulator " << regulator(basis) << "\n";

    Point q0(curve, ZZ(3160080), ZZ(-7881690960LL), ZZ(1));
    Point relation = q0 - basis[0] - basis[1] - basis[2] - 2 * basis[3];
    std::cout << "Q0_minus_F1_F2_F3_2F4 " << relation
              << " order " << order(relation) << "\n";
    return 0;
}
