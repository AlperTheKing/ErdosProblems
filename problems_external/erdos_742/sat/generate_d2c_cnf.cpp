#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace {

struct Cnf {
    int variables = 0;
    std::vector<std::vector<int>> clauses;

    int fresh() { return ++variables; }

    void add(std::vector<int> clause) {
        if (clause.empty()) {
            clauses.push_back({});
            return;
        }
        std::sort(clause.begin(), clause.end());
        clause.erase(std::unique(clause.begin(), clause.end()), clause.end());
        for (int lit : clause) {
            if (std::binary_search(clause.begin(), clause.end(), -lit)) {
                return;  // tautology
            }
        }
        clauses.push_back(std::move(clause));
    }
};

struct Args {
    int n = 25;
    int min_edges = 157;
    std::string output;
    std::string map_output;
    std::string pin_file;
};

Args parse_args(int argc, char** argv) {
    Args a;
    for (int i = 1; i < argc; ++i) {
        const std::string s = argv[i];
        auto value = [&](const char* flag) -> std::string {
            if (i + 1 >= argc) {
                throw std::runtime_error(std::string("missing value after ") + flag);
            }
            return argv[++i];
        };
        if (s == "--n") a.n = std::stoi(value("--n"));
        else if (s == "--min-edges") a.min_edges = std::stoi(value("--min-edges"));
        else if (s == "--output") a.output = value("--output");
        else if (s == "--map") a.map_output = value("--map");
        else if (s == "--pin") a.pin_file = value("--pin");
        else throw std::runtime_error("unknown argument: " + s);
    }
    if (a.n < 3) throw std::runtime_error("n must be at least 3");
    const int m = a.n * (a.n - 1) / 2;
    if (a.min_edges < 0 || a.min_edges > m) {
        throw std::runtime_error("min-edges outside [0, C(n,2)]");
    }
    if (a.output.empty()) throw std::runtime_error("--output is required");
    return a;
}

using Edge = std::pair<int, int>;

Edge edge(int a, int b) {
    if (a == b) throw std::runtime_error("loop requested");
    if (a > b) std::swap(a, b);
    return {a, b};
}

std::set<Edge> read_pin(const std::string& path, int expected_n) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open pin file: " + path);
    std::string tag;
    int n = -1;
    if (!(in >> tag >> n) || tag != "n" || n != expected_n) {
        throw std::runtime_error("pin file must start with: n <matching-order>");
    }
    std::set<Edge> edges;
    int a, b;
    while (in >> a >> b) {
        if (a < 0 || b < 0 || a >= n || b >= n || a == b) {
            throw std::runtime_error("invalid pinned edge");
        }
        if (!edges.insert(edge(a, b)).second) {
            throw std::runtime_error("duplicate pinned edge");
        }
    }
    if (!in.eof()) throw std::runtime_error("malformed pin file");
    return edges;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Args args = parse_args(argc, argv);
        const int n = args.n;
        Cnf cnf;

        std::vector<Edge> pairs;
        std::map<Edge, int> pair_index;
        std::map<Edge, int> x;
        for (int a = 0; a < n; ++a) {
            for (int b = a + 1; b < n; ++b) {
                const Edge e{a, b};
                pair_index[e] = static_cast<int>(pairs.size());
                pairs.push_back(e);
                x[e] = cnf.fresh();
            }
        }

        // c[{s,t},k] is bidirectionally reified as
        // x[{s,k}] AND x[{k,t}].
        std::map<std::tuple<int, int, int>, int> common;
        for (const auto& [s, t] : pairs) {
            for (int k = 0; k < n; ++k) {
                if (k == s || k == t) continue;
                const int c = cnf.fresh();
                common[{s, t, k}] = c;
                const int x1 = x.at(edge(s, k));
                const int x2 = x.at(edge(k, t));
                cnf.add({-c, x1});
                cnf.add({-c, x2});
                cnf.add({-x1, -x2, c});
            }
        }

        // Diameter at most two.
        for (const auto& [s, t] : pairs) {
            std::vector<int> clause{x.at({s, t})};
            for (int k = 0; k < n; ++k) {
                if (k != s && k != t) clause.push_back(common.at({s, t, k}));
            }
            cnf.add(std::move(clause));
        }

        // Exclude the complete graph, so diameter at most two becomes exactly two.
        std::vector<int> noncomplete;
        for (const auto& p : pairs) noncomplete.push_back(-x.at(p));
        cnf.add(std::move(noncomplete));

        // b[e,p] iff e is present and p has no path of length <= 2 after
        // deletion of e.  Only pairs p incident with an endpoint of e are
        // needed; the proof is in ENCODING.md.
        std::map<std::pair<int, int>, int> bad;
        for (int ei = 0; ei < static_cast<int>(pairs.size()); ++ei) {
            const Edge e = pairs[ei];
            std::vector<int> critical_clause{-x.at(e)};
            for (int pi = 0; pi < static_cast<int>(pairs.size()); ++pi) {
                const Edge p = pairs[pi];
                const int s = p.first;
                const int t = p.second;
                if (s != e.first && s != e.second &&
                    t != e.first && t != e.second) {
                    continue;
                }

                const int bvar = cnf.fresh();
                bad[{ei, pi}] = bvar;
                critical_clause.push_back(bvar);
                cnf.add({-bvar, x.at(e)});

                std::vector<int> reverse{-x.at(e), bvar};
                if (p != e) {
                    cnf.add({-bvar, -x.at(p)});
                    reverse.push_back(x.at(p));
                }

                for (int k = 0; k < n; ++k) {
                    if (k == s || k == t) continue;
                    const Edge first = edge(s, k);
                    const Edge second = edge(k, t);
                    if (first == e || second == e) continue;
                    const int c = common.at({s, t, k});
                    cnf.add({-bvar, -c});
                    reverse.push_back(c);
                }
                cnf.add(std::move(reverse));
            }
            cnf.add(std::move(critical_clause));
        }

        // Fully reified dynamic-programming cardinality counter.
        // q[i,j] iff at least j of the first i edge variables are true.
        const int true_var = cnf.fresh();
        const int false_var = cnf.fresh();
        cnf.add({true_var});
        cnf.add({-false_var});
        const int m = static_cast<int>(pairs.size());
        const int K = args.min_edges;
        std::vector<std::vector<int>> q(m + 1, std::vector<int>(K + 1, false_var));
        for (int i = 0; i <= m; ++i) q[i][0] = true_var;
        for (int i = 1; i <= m; ++i) {
            const int xi = x.at(pairs[i - 1]);
            const int upto = std::min(i, K);
            for (int j = 1; j <= upto; ++j) {
                const int Q = cnf.fresh();
                q[i][j] = Q;
                const int A = q[i - 1][j];
                const int B = q[i - 1][j - 1];
                // Q <-> A OR (B AND xi).
                cnf.add({-A, Q});
                cnf.add({-B, -xi, Q});
                cnf.add({-Q, A, B});
                cnf.add({-Q, A, xi});
            }
        }
        if (K > 0) cnf.add({q[m][K]});

        if (!args.pin_file.empty()) {
            const auto pinned = read_pin(args.pin_file, n);
            for (const auto& p : pairs) {
                cnf.add({pinned.count(p) ? x.at(p) : -x.at(p)});
            }
        }

        std::ofstream out(args.output, std::ios::binary);
        if (!out) throw std::runtime_error("cannot create output CNF");
        out << "c D2C exact encoding; edge variables are the first C(n,2) variables\n";
        out << "c n " << n << " min_edges " << K << "\n";
        out << "p cnf " << cnf.variables << ' ' << cnf.clauses.size() << "\n";
        for (const auto& clause : cnf.clauses) {
            for (int lit : clause) out << lit << ' ';
            out << "0\n";
        }
        out.close();

        if (!args.map_output.empty()) {
            std::ofstream map_out(args.map_output);
            if (!map_out) throw std::runtime_error("cannot create map output");
            map_out << "n " << n << "\n";
            for (const auto& p : pairs) {
                map_out << "x " << x.at(p) << ' ' << p.first << ' ' << p.second << "\n";
            }
        }

        std::cerr << "n=" << n << " min_edges=" << K
                  << " vars=" << cnf.variables
                  << " clauses=" << cnf.clauses.size() << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << "\n";
        return 2;
    }
}
