#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

namespace {

constexpr int n = 26;
using Matrix = std::array<std::array<bool, n>, n>;

int induced_edges(const Matrix& adjacency,
                  const std::array<int, 5>& vertices) {
    int edges = 0;
    for (int i = 0; i < 5; ++i) {
        for (int j = i + 1; j < 5; ++j) {
            edges += adjacency[vertices[i]][vertices[j]];
        }
    }
    return edges;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: audit_r4_general_packing_obstruction G61.edges\n";
        return 2;
    }
    std::ifstream in(argv[1]);
    if (!in) {
        std::cerr << "cannot open graph\n";
        return 3;
    }

    Matrix adjacency{};
    std::string line;
    int parsed_edges = 0;
    while (std::getline(in, line)) {
        std::istringstream row(line);
        char tag = '\0';
        row >> tag;
        if (tag != 'e') continue;
        int a = -1;
        int b = -1;
        row >> a >> b;
        if (!row || a < 0 || b < 0 || a >= n || b >= n || a >= b ||
            adjacency[a][b]) {
            std::cerr << "bad edge row\n";
            return 4;
        }
        adjacency[a][b] = adjacency[b][a] = true;
        ++parsed_edges;
    }
    if (parsed_edges != 61) {
        std::cerr << "expected 61 edges\n";
        return 5;
    }

    int h_edges = 0;
    for (int a = 0; a < 11; ++a) {
        for (int b = a + 1; b < 11; ++b) {
            h_edges += adjacency[a][b];
        }
    }
    if (h_edges != 31) {
        std::cerr << "expected e(H)=31\n";
        return 6;
    }

    // Verify alpha(H)=2 directly.
    bool independent_pair = false;
    for (int a = 0; a < 11; ++a) {
        for (int b = a + 1; b < 11; ++b) {
            independent_pair |= !adjacency[a][b];
            for (int c = b + 1; c < 11; ++c) {
                if (!adjacency[a][b] && !adjacency[a][c] &&
                    !adjacency[b][c]) {
                    std::cerr << "independent triple in H\n";
                    return 7;
                }
            }
        }
    }
    if (!independent_pair) {
        std::cerr << "H has no independent pair\n";
        return 8;
    }

    // Exhaust all five-sets in G61 and verify the exact component profile of
    // every independent five-set.
    int independent_five_sets = 0;
    std::array<int, 5> set{};
    for (set[0] = 0; set[0] < n - 4; ++set[0]) {
        for (set[1] = set[0] + 1; set[1] < n - 3; ++set[1]) {
            for (set[2] = set[1] + 1; set[2] < n - 2; ++set[2]) {
                for (set[3] = set[2] + 1; set[3] < n - 1; ++set[3]) {
                    for (set[4] = set[3] + 1; set[4] < n; ++set[4]) {
                        if (induced_edges(adjacency, set) != 0) continue;
                        ++independent_five_sets;
                        int in_h = 0;
                        std::array<int, 3> in_q{};
                        for (int v : set) {
                            if (v < 11) {
                                ++in_h;
                            } else {
                                ++in_q[(v - 11) / 5];
                            }
                        }
                        if (in_h != 2 || in_q != std::array<int, 3>{1, 1, 1}) {
                            std::cerr
                                << "independent five-set profile disagreement\n";
                            return 9;
                        }
                    }
                }
            }
        }
    }
    if (independent_five_sets != 3000) {
        std::cerr << "expected 3000 independent five-sets, got "
                  << independent_five_sets << '\n';
        return 10;
    }

    // Independently find the minimum number of H-edges induced by five
    // vertices.  The proof only needs this minimum to be at least four.
    int minimum_h_edges = 100;
    std::array<int, 5> h_set{};
    for (h_set[0] = 0; h_set[0] < 7; ++h_set[0]) {
        for (h_set[1] = h_set[0] + 1; h_set[1] < 8; ++h_set[1]) {
            for (h_set[2] = h_set[1] + 1; h_set[2] < 9; ++h_set[2]) {
                for (h_set[3] = h_set[2] + 1; h_set[3] < 10; ++h_set[3]) {
                    for (h_set[4] = h_set[3] + 1; h_set[4] < 11;
                         ++h_set[4]) {
                        minimum_h_edges =
                            std::min(minimum_h_edges,
                                     induced_edges(adjacency, h_set));
                    }
                }
            }
        }
    }
    if (minimum_h_edges < 4) {
        std::cerr << "five vertices of H induce fewer than four edges\n";
        return 11;
    }

    const int forced_inside_h = h_edges + 4 * (3 + minimum_h_edges);
    if (forced_inside_h <= 55) {
        std::cerr << "capacity contradiction did not fire\n";
        return 12;
    }

    std::cout << "VERIFIED e(H)=31 alpha(H)=2"
              << " independent5_profiles=3000"
              << " min_e(H[5])=" << minimum_h_edges
              << " forced_inside_H=" << forced_inside_h
              << " capacity=55\n";
    return 0;
}
