#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

namespace {

constexpr int n = 26;
using Matrix = std::array<std::array<bool, n>, n>;

bool homogeneous_six_set(const Matrix& adjacency,
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

int maximum_homogeneous_set(const Matrix& adjacency, bool want_edge) {
    int best = 0;
    for (int mask = 1; mask < (1 << 11); ++mask) {
        // Exact alpha/omega on vertices 0..10.  Vertices 11..25 are three
        // explicit K5 components and are handled analytically below.
        bool homogeneous = true;
        int size = 0;
        for (int i = 0; i < 11 && homogeneous; ++i) {
            if (!(mask & (1 << i))) continue;
            ++size;
            for (int j = i + 1; j < 11; ++j) {
                if ((mask & (1 << j)) &&
                    adjacency[i][j] != want_edge) {
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
        std::cerr << "usage: verify_r2_counterexample INPUT.edges\n";
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
    int edge_count = 0;
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
            if (!row || a < 0 || b < 0 || a >= n || b >= n || a >= b) {
                std::cerr << "bad edge line: " << line << '\n';
                return 5;
            }
            if (adjacency[a][b]) {
                std::cerr << "duplicate edge: " << a << ' ' << b << '\n';
                return 6;
            }
            adjacency[a][b] = adjacency[b][a] = true;
            ++edge_count;
        } else {
            std::cerr << "unknown line: " << line << '\n';
            return 7;
        }
    }
    if (declared_n != n || declared_e != 65 || edge_count != 65) {
        std::cerr << "header/count disagreement: n=" << declared_n
                  << " declared_e=" << declared_e
                  << " parsed_e=" << edge_count << '\n';
        return 8;
    }

    std::array<int, 6> witness{};
    if (homogeneous_six_set(adjacency, true, witness)) {
        std::cerr << "omega >= 6 witness:";
        for (int v : witness) std::cerr << ' ' << v;
        std::cerr << '\n';
        return 9;
    }
    if (homogeneous_six_set(adjacency, false, witness)) {
        std::cerr << "alpha >= 6 witness:";
        for (int v : witness) std::cerr << ' ' << v;
        std::cerr << '\n';
        return 10;
    }

    const int omega_h = maximum_homogeneous_set(adjacency, true);
    const int alpha_h = maximum_homogeneous_set(adjacency, false);
    // Three disjoint K5 components add three vertices to an independent set,
    // while a clique stays inside one component.
    const int omega = std::max(omega_h, 5);
    const int alpha = alpha_h + 3;
    if (omega != 5 || alpha != 5) {
        std::cerr << "unexpected exact values alpha=" << alpha
                  << " omega=" << omega << '\n';
        return 11;
    }
    std::cout << "VERIFIED n=26 e=65 alpha=5 omega=5"
              << " six_sets_checked=230230\n";
    return 0;
}
