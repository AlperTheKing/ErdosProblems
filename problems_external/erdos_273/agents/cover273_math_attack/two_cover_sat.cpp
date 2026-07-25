#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <tuple>
#include <vector>

struct ClauseWriter {
    std::ofstream out;
    std::uint64_t clauses = 0;
    explicit ClauseWriter(const std::string& path) : out(path) {
        out << std::string(80, ' ') << "\n";
    }
    void clause(const std::vector<int>& xs) {
        for (int x : xs) out << x << ' ';
        out << "0\n";
        ++clauses;
    }
};

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: two_cover_sat OUT.cnf\n";
        return 2;
    }
    const std::vector<int> qs = {
        2,3,5,6,8,9,11,14,15,18,20,21,30,33,35,36,44,56,63,90,99,
        105,120,140,165,168,198,210,231,308,315,330,440,495,504,660,
        1155,1260,1848,2310,4620,9240,27720
    };
    constexpr int Q = 27720;
    int next_var = 1;
    std::vector<std::vector<std::vector<int>>> x(2);
    for (int c = 0; c < 2; ++c) {
        x[c].resize(qs.size());
        for (std::size_t i = 0; i < qs.size(); ++i) {
            x[c][i].resize(qs[i]);
            for (int a = 0; a < qs[i]; ++a) x[c][i][a] = next_var++;
        }
    }

    ClauseWriter w(argv[1]);
    // Each q supplies at most one residue to at most one of the two covers.
    for (std::size_t i = 0; i < qs.size(); ++i) {
        std::vector<int> lits;
        for (int c = 0; c < 2; ++c)
            for (int a = 0; a < qs[i]; ++a) lits.push_back(x[c][i][a]);
        std::vector<int> s(lits.size() - 1);
        for (int& v : s) v = next_var++;
        w.clause({-lits[0], s[0]});
        for (std::size_t j = 1; j + 1 < lits.size(); ++j) {
            w.clause({-lits[j], s[j]});
            w.clause({-s[j - 1], s[j]});
            w.clause({-lits[j], -s[j - 1]});
        }
        w.clause({-lits.back(), -s.back()});
    }
    // Every residue modulo Q is covered in both colors.
    for (int c = 0; c < 2; ++c) {
        for (int y = 0; y < Q; ++y) {
            std::vector<int> clause;
            clause.reserve(qs.size());
            for (std::size_t i = 0; i < qs.size(); ++i)
                clause.push_back(x[c][i][y % qs[i]]);
            w.clause(clause);
        }
    }
    // Since the reciprocal mass without q=2 is <2, q=2 is mandatory.
    // Swap colors and translate y to normalize it to 0 (mod 2) in cover 0.
    w.clause({x[0][0][0]});

    const int variables = next_var - 1;
    w.out.flush();
    w.out.seekp(0);
    std::string header = "p cnf " + std::to_string(variables) + " " +
                         std::to_string(w.clauses);
    if (header.size() > 79) return 3;
    w.out << header << std::string(79 - header.size(), ' ') << "\n";

    std::ofstream map(std::string(argv[1]) + ".map");
    for (int c = 0; c < 2; ++c)
        for (std::size_t i = 0; i < qs.size(); ++i)
            for (int a = 0; a < qs[i]; ++a)
                map << x[c][i][a] << ' ' << c << ' ' << qs[i] << ' ' << a
                    << '\n';
    std::cout << "Q=" << Q << " q_count=" << qs.size()
              << " variables=" << variables << " clauses=" << w.clauses
              << "\n";
    return 0;
}
