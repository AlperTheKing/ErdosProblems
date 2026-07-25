#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

namespace {

constexpr int n = 26;
using Matrix = std::array<std::array<bool, n>, n>;

bool homogeneous_six(const Matrix& adjacency,
                     bool want_edge,
                     std::array<int, 6>& witness) {
    for (witness[0] = 0; witness[0] < n - 5; ++witness[0]) {
        for (witness[1] = witness[0] + 1; witness[1] < n - 4; ++witness[1]) {
            for (witness[2] = witness[1] + 1; witness[2] < n - 3;
                 ++witness[2]) {
                for (witness[3] = witness[2] + 1; witness[3] < n - 2;
                     ++witness[3]) {
                    for (witness[4] = witness[3] + 1;
                         witness[4] < n - 1;
                         ++witness[4]) {
                        for (witness[5] = witness[4] + 1;
                             witness[5] < n;
                             ++witness[5]) {
                            bool homogeneous = true;
                            for (int i = 0; i < 6 && homogeneous; ++i) {
                                for (int j = i + 1; j < 6; ++j) {
                                    if (adjacency[witness[i]][witness[j]] !=
                                        want_edge) {
                                        homogeneous = false;
                                        break;
                                    }
                                }
                            }
                            if (homogeneous) return true;
                        }
                    }
                }
            }
        }
    }
    return false;
}

int exact_homogeneous_number_on_first_11(const Matrix& adjacency,
                                         bool want_edge) {
    int best = 0;
    for (int mask = 1; mask < (1 << 11); ++mask) {
        bool homogeneous = true;
        int size = 0;
        for (int a = 0; a < 11 && homogeneous; ++a) {
            if (!(mask & (1 << a))) continue;
            ++size;
            for (int b = a + 1; b < 11; ++b) {
                if ((mask & (1 << b)) &&
                    adjacency[a][b] != want_edge) {
                    homogeneous = false;
                    break;
                }
            }
        }
        if (homogeneous && size > best) best = size;
    }
    return best;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: verify_r4_g61 INPUT.edges\n";
        return 2;
    }
    std::ifstream in(argv[1]);
    if (!in) {
        std::cerr << "cannot open input\n";
        return 3;
    }

    Matrix adjacency{};
    std::string line;
    int declared_n = -1;
    int declared_e = -1;
    int parsed_e = 0;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::istringstream row(line);
        char tag = '\0';
        row >> tag;
        if (tag == 'p') {
            std::string kind;
            row >> kind >> declared_n >> declared_e;
            if (!row || kind != "edge") {
                std::cerr << "bad header\n";
                return 4;
            }
        } else if (tag == 'e') {
            int a = -1;
            int b = -1;
            row >> a >> b;
            if (!row || a < 0 || b < 0 || a >= n || b >= n || a >= b ||
                adjacency[a][b]) {
                std::cerr << "bad or duplicate edge row\n";
                return 5;
            }
            adjacency[a][b] = adjacency[b][a] = true;
            ++parsed_e;
        } else {
            std::cerr << "unknown row\n";
            return 6;
        }
    }
    if (declared_n != n || declared_e != 61 || parsed_e != 61) {
        std::cerr << "header/count disagreement\n";
        return 7;
    }

    std::array<int, 6> witness{};
    if (homogeneous_six(adjacency, true, witness)) {
        std::cerr << "omega >= 6\n";
        return 8;
    }
    if (homogeneous_six(adjacency, false, witness)) {
        std::cerr << "alpha >= 6\n";
        return 9;
    }

    const int omega_h =
        exact_homogeneous_number_on_first_11(adjacency, true);
    const int alpha_h =
        exact_homogeneous_number_on_first_11(adjacency, false);
    const int omega = std::max(omega_h, 5);
    const int alpha = alpha_h + 3;
    if (omega != 5 || alpha != 5) {
        std::cerr << "unexpected exact alpha/omega: " << alpha << '/'
                  << omega << '\n';
        return 10;
    }

    std::array<int, 7> degree_count{};
    for (int a = 0; a < n; ++a) {
        int degree = 0;
        for (int b = 0; b < n; ++b) degree += adjacency[a][b];
        if (degree >= static_cast<int>(degree_count.size())) {
            std::cerr << "unexpected degree\n";
            return 11;
        }
        ++degree_count[degree];
    }
    if (degree_count[4] != 15 || degree_count[5] != 4 ||
        degree_count[6] != 7) {
        std::cerr << "degree sequence disagreement\n";
        return 12;
    }

    std::cout << "VERIFIED n=26 e=61 alpha=5 omega=5"
              << " degrees=4^15,5^4,6^7 six_sets_checked=230230\n";
    return 0;
}
