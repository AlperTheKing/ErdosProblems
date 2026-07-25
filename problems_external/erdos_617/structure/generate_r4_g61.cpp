#include <array>
#include <fstream>
#include <iostream>

namespace {

constexpr std::array<int, 11> part = {
    0, 0, 0,  // part 0, size 3
    1, 1,     // part 1, size 2
    2, 2,     // part 2, size 2
    3, 3,     // part 3, size 2
    4, 4      // part 4, size 2
};

bool adjacent_cycle_parts(int a, int b) {
    const int delta = (a - b + 5) % 5;
    return delta == 1 || delta == 4;
}

bool g61_edge(int a, int b) {
    if (a > b) std::swap(a, b);
    if (b <= 10) {
        // Complement of the independent-part C5 blow-up.
        return part[a] == part[b] ||
               !adjacent_cycle_parts(part[a], part[b]);
    }
    if (a >= 11 && b <= 15) return true;
    if (a >= 16 && b <= 20) return true;
    if (a >= 21 && b <= 25) return true;
    return false;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: generate_r4_g61 OUTPUT.edges\n";
        return 2;
    }
    std::ofstream out(argv[1], std::ios::binary);
    if (!out) {
        std::cerr << "cannot open output\n";
        return 3;
    }
    out << "p edge 26 61\n";
    int edges = 0;
    for (int a = 0; a < 26; ++a) {
        for (int b = a + 1; b < 26; ++b) {
            if (!g61_edge(a, b)) continue;
            out << "e " << a << ' ' << b << '\n';
            ++edges;
        }
    }
    if (edges != 61) {
        std::cerr << "internal edge-count error: " << edges << '\n';
        return 4;
    }
    std::cout << "WROTE n=26 e=61\n";
    return 0;
}
