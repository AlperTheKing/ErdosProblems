#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace {

constexpr int q = 5;
constexpr int old_n = 25;
constexpr int n = 26;
constexpr int infinity = 25;
constexpr int classes = 12;
constexpr int variables = classes * q;

int mod(int x) {
    x %= q;
    return x < 0 ? x + q : x;
}

int inv(int x) {
    x = mod(x);
    for (int y = 1; y < q; ++y) {
        if (mod(x * y) == 1) return y;
    }
    return -1;
}

std::pair<int, int> point(int v) {
    return {v / q, v % q};
}

int variable(int difference_class, int value) {
    return 1 + difference_class * q + value;
}

using Clause = std::vector<int>;

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: encode_covariant_offsets OUTPUT.cnf\n";
        return 2;
    }

    std::array<std::array<int, q>, q> difference_class{};
    for (auto& row : difference_class) row.fill(-1);
    int next_class = 0;
    for (int dx = 0; dx < q; ++dx) {
        for (int dy = 0; dy < q; ++dy) {
            if (dx == 0 && dy == 0) continue;
            if (difference_class[dx][dy] >= 0) continue;
            if (next_class >= classes) {
                std::cerr << "too many unordered difference classes\n";
                return 3;
            }
            difference_class[dx][dy] = next_class;
            difference_class[mod(-dx)][mod(-dy)] = next_class;
            ++next_class;
        }
    }
    if (next_class != classes) {
        std::cerr << "expected 12 unordered difference classes, got "
                  << next_class << '\n';
        return 4;
    }

    std::vector<Clause> clauses;
    clauses.reserve(230500);

    // Exactly one value for each h([d]).
    for (int dc = 0; dc < classes; ++dc) {
        Clause at_least_one;
        for (int value = 0; value < q; ++value) {
            at_least_one.push_back(variable(dc, value));
        }
        clauses.push_back(std::move(at_least_one));
        for (int a = 0; a < q; ++a) {
            for (int b = a + 1; b < q; ++b) {
                clauses.push_back(
                    {-variable(dc, a), -variable(dc, b)});
            }
        }
    }

    std::array<int, 6> set{};
    for (set[0] = 0; set[0] < n - 5; ++set[0]) {
        for (set[1] = set[0] + 1; set[1] < n - 4; ++set[1]) {
            for (set[2] = set[1] + 1; set[2] < n - 3; ++set[2]) {
                for (set[3] = set[2] + 1; set[3] < n - 2; ++set[3]) {
                    for (set[4] = set[3] + 1; set[4] < n - 1; ++set[4]) {
                        for (set[5] = set[4] + 1; set[5] < n; ++set[5]) {
                            bool automatically_covered = false;
                            bool contains_infinity = false;
                            for (int v : set) {
                                if (v == infinity) contains_infinity = true;
                            }
                            if (contains_infinity) {
                                for (int v : set) {
                                    if (v != infinity && point(v).first == 0) {
                                        automatically_covered = true;
                                    }
                                }
                            }
                            if (automatically_covered) continue;

                            std::array<bool, variables + 1> seen{};
                            Clause clause;
                            for (int i = 0; i < 6; ++i) {
                                if (set[i] == infinity) continue;
                                const auto [xi, yi] = point(set[i]);
                                for (int j = i + 1; j < 6; ++j) {
                                    if (set[j] == infinity) continue;
                                    const auto [xj, yj] = point(set[j]);
                                    const int dx = mod(xj - xi);
                                    const int dy = mod(yj - yi);
                                    const int dc = difference_class[dx][dy];
                                    const int midpoint_x =
                                        mod((xi + xj) * inv(2));
                                    const int value = mod(-midpoint_x);
                                    const int literal = variable(dc, value);
                                    if (!seen[literal]) {
                                        seen[literal] = true;
                                        clause.push_back(literal);
                                    }
                                }
                            }
                            std::sort(clause.begin(), clause.end());
                            clauses.push_back(std::move(clause));
                        }
                    }
                }
            }
        }
    }

    std::ofstream out(argv[1], std::ios::binary);
    if (!out) {
        std::cerr << "cannot open output file\n";
        return 5;
    }
    out << "c h([d]) variables are 1 + 5*class + value\n";
    for (int dx = 0; dx < q; ++dx) {
        for (int dy = 0; dy < q; ++dy) {
            if (dx == 0 && dy == 0) continue;
            const int ndx = mod(-dx);
            const int ndy = mod(-dy);
            if (std::pair{dx, dy} > std::pair{ndx, ndy}) continue;
            out << "c class " << difference_class[dx][dy] << " = +/-("
                << dx << ',' << dy << ")\n";
        }
    }
    out << "p cnf " << variables << ' ' << clauses.size() << '\n';
    for (const Clause& clause : clauses) {
        for (int literal : clause) out << literal << ' ';
        out << "0\n";
    }
    out.close();
    std::cout << "variables=" << variables
              << " clauses=" << clauses.size() << '\n';
    return 0;
}
