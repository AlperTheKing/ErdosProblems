#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <tuple>
#include <vector>

namespace {

struct Args {
    std::string input;
    int expect_n = -1;
    int min_edges = 0;
    bool quiet = false;
};

Args parse_args(int argc, char** argv) {
    Args a;
    for (int i = 1; i < argc; ++i) {
        const std::string s = argv[i];
        auto value = [&](const char* flag) -> std::string {
            if (i + 1 >= argc) throw std::runtime_error(std::string("missing value after ") + flag);
            return argv[++i];
        };
        if (s == "--input") a.input = value("--input");
        else if (s == "--expect-n") a.expect_n = std::stoi(value("--expect-n"));
        else if (s == "--min-edges") a.min_edges = std::stoi(value("--min-edges"));
        else if (s == "--quiet") a.quiet = true;
        else throw std::runtime_error("unknown argument: " + s);
    }
    if (a.input.empty()) throw std::runtime_error("--input is required");
    return a;
}

std::vector<std::vector<unsigned char>> read_matrix(const std::string& path, int& n) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open matrix file");
    std::string tag;
    if (!(in >> tag >> n) || tag != "N" || n < 1) {
        throw std::runtime_error("first line must be: N <positive-order>");
    }
    std::vector<std::vector<unsigned char>> a(n, std::vector<unsigned char>(n));
    for (int i = 0; i < n; ++i) {
        std::string row;
        if (!(in >> row) || static_cast<int>(row.size()) != n) {
            throw std::runtime_error("matrix row has wrong length");
        }
        for (int j = 0; j < n; ++j) {
            if (row[j] != '0' && row[j] != '1') {
                throw std::runtime_error("matrix contains a non-binary character");
            }
            a[i][j] = static_cast<unsigned char>(row[j] - '0');
        }
    }
    std::string extra;
    if (in >> extra) throw std::runtime_error("trailing token after matrix");
    return a;
}

bool same_edge(int a, int b, int c, int d) {
    if (a > b) std::swap(a, b);
    if (c > d) std::swap(c, d);
    return a == c && b == d;
}

bool edge_after(const std::vector<std::vector<unsigned char>>& a,
                int s, int t, int u, int v) {
    return a[s][t] && !same_edge(s, t, u, v);
}

std::pair<int, int> witness_after_deletion(
    const std::vector<std::vector<unsigned char>>& a, int u, int v) {
    const int n = static_cast<int>(a.size());
    for (int s = 0; s < n; ++s) {
        for (int t = s + 1; t < n; ++t) {
            if (edge_after(a, s, t, u, v)) continue;
            bool path2 = false;
            for (int k = 0; k < n && !path2; ++k) {
                if (k == s || k == t) continue;
                path2 = edge_after(a, s, k, u, v) &&
                        edge_after(a, k, t, u, v);
            }
            if (!path2) return {s, t};
        }
    }
    return {-1, -1};
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Args args = parse_args(argc, argv);
        int n = 0;
        const auto a = read_matrix(args.input, n);
        if (args.expect_n >= 0 && n != args.expect_n) {
            throw std::runtime_error("unexpected order");
        }
        for (int i = 0; i < n; ++i) {
            if (a[i][i]) throw std::runtime_error("loop on the diagonal");
            for (int j = i + 1; j < n; ++j) {
                if (a[i][j] != a[j][i]) throw std::runtime_error("matrix is not symmetric");
            }
        }

        int m = 0;
        for (int i = 0; i < n; ++i) {
            for (int j = i + 1; j < n; ++j) m += a[i][j];
        }
        if (m < args.min_edges) throw std::runtime_error("edge threshold not met");
        if (m == n * (n - 1) / 2) throw std::runtime_error("diameter is one, not two");

        for (int s = 0; s < n; ++s) {
            for (int t = s + 1; t < n; ++t) {
                if (a[s][t]) continue;
                bool common = false;
                for (int k = 0; k < n && !common; ++k) {
                    common = a[s][k] && a[k][t];
                }
                if (!common) throw std::runtime_error("diameter exceeds two");
            }
        }

        std::vector<std::tuple<int, int, int, int>> ledger;
        for (int u = 0; u < n; ++u) {
            for (int v = u + 1; v < n; ++v) {
                if (!a[u][v]) continue;
                const auto w = witness_after_deletion(a, u, v);
                if (w.first < 0) {
                    throw std::runtime_error("noncritical edge " +
                                             std::to_string(u) + "-" +
                                             std::to_string(v));
                }
                ledger.emplace_back(u, v, w.first, w.second);
            }
        }

        if (!args.quiet) {
            std::cout << "VERIFIED_B N=" << n << " M=" << m
                      << " diameter=2 critical_edges=" << ledger.size() << "\n";
            for (const auto& [u, v, s, t] : ledger) {
                std::cout << "edge " << u << ' ' << v
                          << " witness " << s << ' ' << t << "\n";
            }
        }
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "REJECTED_B: " << e.what() << "\n";
        return 1;
    }
}
