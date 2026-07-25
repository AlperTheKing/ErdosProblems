#include <fstream>
#include <iostream>
#include <string>

namespace {

bool groetzsch_edge(int a, int b) {
    if (a > b) std::swap(a, b);

    // v_i = i, u_i = 5+i, w = 10.
    if (a < 5 && b < 5) {
        const int delta = (b - a) % 5;
        return delta == 1 || delta == 4;
    }
    if (a < 5 && b >= 5 && b < 10) {
        const int vi = a;
        const int ui = b - 5;
        return vi == (ui + 1) % 5 || vi == (ui + 4) % 5;
    }
    if (a >= 5 && a < 10 && b == 10) return true;
    return false;
}

bool counterexample_edge(int a, int b) {
    if (a > b) std::swap(a, b);
    if (b <= 10) return !groetzsch_edge(a, b);
    if (a >= 11 && b <= 15) return true;
    if (a >= 16 && b <= 20) return true;
    if (a >= 21 && b <= 25) return true;
    return false;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: generate_r2_counterexample OUTPUT.edges\n";
        return 2;
    }
    std::ofstream out(argv[1], std::ios::binary);
    if (!out) {
        std::cerr << "cannot open output\n";
        return 3;
    }
    out << "p edge 26 65\n";
    int count = 0;
    for (int a = 0; a < 26; ++a) {
        for (int b = a + 1; b < 26; ++b) {
            if (!counterexample_edge(a, b)) continue;
            out << "e " << a << ' ' << b << '\n';
            ++count;
        }
    }
    if (count != 65) {
        std::cerr << "internal edge-count error: " << count << '\n';
        return 4;
    }
    std::cout << "WROTE n=26 e=65\n";
    return 0;
}
