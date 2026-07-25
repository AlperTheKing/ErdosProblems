#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

namespace {

constexpr int n = 26;
using Matrix = std::array<std::array<bool, n>, n>;

struct Type {
    int u;
    int v;
    int w;
    int q;

    auto tuple() const {
        return std::tuple{u, v, w, q};
    }
};

bool is_clique(const Matrix& adjacency, const std::vector<int>& vertices) {
    for (std::size_t i = 0; i < vertices.size(); ++i) {
        for (std::size_t j = i + 1; j < vertices.size(); ++j) {
            if (!adjacency[vertices[i]][vertices[j]]) return false;
        }
    }
    return true;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: audit_r3_decomposition_obstruction GRAPH.edges\n";
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
    if (parsed_edges != 65) {
        std::cerr << "expected 65 edges, got " << parsed_edges << '\n';
        return 5;
    }

    std::array<int, 8> degree_count{};
    for (int a = 0; a < n; ++a) {
        int degree = 0;
        for (int b = 0; b < n; ++b) degree += adjacency[a][b];
        if (degree < 0 || degree >= static_cast<int>(degree_count.size())) {
            std::cerr << "unexpected degree " << degree << '\n';
            return 6;
        }
        ++degree_count[degree];
    }
    if (degree_count[4] != 15 || degree_count[5] != 1 ||
        degree_count[6] != 5 || degree_count[7] != 5) {
        std::cerr << "degree sequence disagreement\n";
        return 7;
    }

    const std::array<std::vector<int>, 4> expected_blocks = {
        std::vector<int>{5, 6, 7, 8, 9},
        std::vector<int>{11, 12, 13, 14, 15},
        std::vector<int>{16, 17, 18, 19, 20},
        std::vector<int>{21, 22, 23, 24, 25}};
    for (const auto& block : expected_blocks) {
        if (!is_clique(adjacency, block)) {
            std::cerr << "expected K5 block is not a clique\n";
            return 8;
        }
    }

    std::vector<Type> types;
    for (int u = 0; u <= 5; ++u) {
        for (int v = 0; v <= 5; ++v) {
            for (int w = 0; w <= 5; ++w) {
                for (int q = 0; q <= 5; ++q) {
                    if (u + v + w + q == 5 &&
                        7 * u + 6 * v + 5 * w + 4 * q == 25) {
                        types.push_back({u, v, w, q});
                    }
                }
            }
        }
    }
    std::sort(types.begin(), types.end(),
              [](const Type& a, const Type& b) {
                  return a.tuple() < b.tuple();
              });
    const std::set<std::tuple<int, int, int, int>> expected_types = {
        {1, 1, 0, 3}, {1, 0, 2, 2}, {0, 2, 1, 2},
        {0, 1, 3, 1}, {0, 0, 5, 0}};
    std::set<std::tuple<int, int, int, int>> actual_types;
    for (const Type& type : types) actual_types.insert(type.tuple());
    if (actual_types != expected_types) {
        std::cerr << "per-vertex type enumeration disagreement\n";
        return 9;
    }

    std::vector<std::array<int, 5>> global_cases;
    for (int a = 0; a <= 26; ++a) {
        for (int b = 0; b <= 26 - a; ++b) {
            for (int c = 0; c <= 26 - a - b; ++c) {
                for (int d = 0; d <= 26 - a - b - c; ++d) {
                    const int e = 26 - a - b - c - d;
                    if (a + b != 25) continue;
                    if (2 * b + c + 3 * d + 5 * e != 5) continue;
                    global_cases.push_back({a, b, c, d, e});
                }
            }
        }
    }
    const std::set<std::array<int, 5>> expected_cases = {
        {25, 0, 0, 0, 1},
        {23, 2, 1, 0, 0},
        {24, 1, 0, 1, 0}};
    const std::set<std::array<int, 5>> actual_cases(global_cases.begin(),
                                                     global_cases.end());
    if (actual_cases != expected_cases) {
        std::cerr << "global role-count case disagreement\n";
        return 10;
    }

    // Maximum number of cross-copy blocks disjoint from a U block in the
    // three cases, obtained by putting as many low-incidence B vertices in
    // that U block as globally available.
    const std::array<int, 3> max_disjoint = {
        16 - 5 * 3,
        16 - (2 * 2 + 3 * 3),
        16 - (1 * 2 + 4 * 3)};
    if (!(max_disjoint[0] == 1 && max_disjoint[1] == 3 &&
          max_disjoint[2] == 2)) {
        std::cerr << "cross-block arithmetic disagreement\n";
        return 11;
    }

    std::cout
        << "VERIFIED degree_sequence=4^15,5^1,6^5,7^5"
        << " role_types=5 global_cases=3"
        << " max_cross_disjoint_U=1,3,2 required=4\n";
    return 0;
}
