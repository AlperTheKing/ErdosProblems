#include <algorithm>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

struct ParseError : std::runtime_error {
    int line;
    ParseError(int line_number, const std::string& message)
        : std::runtime_error(message), line(line_number) {}
};

struct Graph {
    int n = 0;
    std::int64_t declared_m = 0;
    std::string format;
    std::vector<std::pair<int, int>> edges;
    std::vector<std::vector<int>> adj;
};

struct DistanceStats {
    bool connected = true;
    int diameter = 0;
    std::vector<std::pair<std::pair<int, int>, int>> over_two;
};

std::string trim(const std::string& input) {
    const auto first = input.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) return "";
    const auto last = input.find_last_not_of(" \t\r\n");
    return input.substr(first, last - first + 1);
}

std::vector<std::string> split_ws(const std::string& line) {
    std::istringstream in(line);
    std::vector<std::string> tokens;
    std::string token;
    while (in >> token) tokens.push_back(token);
    return tokens;
}

template <typename Integer>
Integer parse_integer(const std::string& token, int line, const std::string& field) {
    Integer value{};
    const char* begin = token.data();
    const char* end = begin + token.size();
    const auto result = std::from_chars(begin, end, value);
    if (result.ec != std::errc{} || result.ptr != end) {
        throw ParseError(line, "invalid integer for " + field + ": " + token);
    }
    return value;
}

bool is_comment_or_blank(const std::string& line) {
    const std::string t = trim(line);
    return t.empty() || t.front() == '#' ||
           (t.front() == 'c' && (t.size() == 1 || t[1] == ' ' || t[1] == '\t'));
}

Graph parse_graph(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw ParseError(0, "cannot open input: " + path);

    Graph graph;
    bool have_header = false;
    std::vector<std::vector<int>> adjacency_rows;
    std::vector<bool> row_seen;
    std::pair<int, int> previous_edge{-1, -1};

    std::string raw;
    int line_number = 0;
    while (std::getline(input, raw)) {
        ++line_number;
        if (is_comment_or_blank(raw)) continue;
        const std::string line = trim(raw);
        const std::vector<std::string> tokens = split_ws(line);

        if (!have_header) {
            if (tokens.size() != 4 || tokens[0] != "p" ||
                (tokens[1] != "edge" && tokens[1] != "adj")) {
                throw ParseError(line_number, "expected header: p edge|adj N M");
            }
            graph.format = tokens[1];
            graph.n = parse_integer<int>(tokens[2], line_number, "N");
            graph.declared_m =
                parse_integer<std::int64_t>(tokens[3], line_number, "M");
            if (graph.n < 1) throw ParseError(line_number, "N must be positive");
            const std::int64_t max_edges =
                static_cast<std::int64_t>(graph.n) * (graph.n - 1) / 2;
            if (graph.declared_m < 0 || graph.declared_m > max_edges) {
                throw ParseError(line_number, "M is outside the simple-graph range");
            }
            if (graph.format == "adj") {
                adjacency_rows.assign(graph.n, {});
                row_seen.assign(graph.n, false);
            }
            have_header = true;
            continue;
        }

        if (graph.format == "edge") {
            if (tokens.size() != 3 || tokens[0] != "e") {
                throw ParseError(line_number, "expected edge row: e U V");
            }
            const int u = parse_integer<int>(tokens[1], line_number, "U");
            const int v = parse_integer<int>(tokens[2], line_number, "V");
            if (u < 0 || u >= graph.n || v < 0 || v >= graph.n) {
                throw ParseError(line_number, "edge endpoint outside [0,N)");
            }
            if (u == v) throw ParseError(line_number, "loop is not allowed");
            if (u > v) {
                throw ParseError(line_number,
                                 "noncanonical edge: endpoints must satisfy U < V");
            }
            const std::pair<int, int> edge{u, v};
            if (!graph.edges.empty() && edge <= previous_edge) {
                throw ParseError(
                    line_number,
                    edge == previous_edge ? "duplicate edge"
                                          : "edge rows are not lexicographically sorted");
            }
            graph.edges.push_back(edge);
            previous_edge = edge;
        } else {
            if (tokens.size() < 3 || tokens[0] != "a" || tokens[2] != ":") {
                throw ParseError(line_number,
                                 "expected adjacency row: a V : [sorted neighbors]");
            }
            const int v = parse_integer<int>(tokens[1], line_number, "V");
            if (v < 0 || v >= graph.n) {
                throw ParseError(line_number, "adjacency vertex outside [0,N)");
            }
            if (row_seen[v]) throw ParseError(line_number, "duplicate adjacency row");
            if (v != static_cast<int>(std::count(row_seen.begin(), row_seen.end(), true))) {
                throw ParseError(line_number,
                                 "adjacency rows must appear in vertex order 0,...,N-1");
            }
            int previous_neighbor = -1;
            for (std::size_t i = 3; i < tokens.size(); ++i) {
                const int u =
                    parse_integer<int>(tokens[i], line_number, "neighbor");
                if (u < 0 || u >= graph.n) {
                    throw ParseError(line_number, "neighbor outside [0,N)");
                }
                if (u == v) throw ParseError(line_number, "loop is not allowed");
                if (u <= previous_neighbor) {
                    throw ParseError(line_number,
                                     u == previous_neighbor
                                         ? "duplicate neighbor"
                                         : "neighbors are not strictly increasing");
                }
                adjacency_rows[v].push_back(u);
                previous_neighbor = u;
            }
            row_seen[v] = true;
        }
    }

    if (!have_header) throw ParseError(0, "missing header");

    if (graph.format == "edge") {
        if (static_cast<std::int64_t>(graph.edges.size()) != graph.declared_m) {
            throw ParseError(line_number,
                             "declared edge count does not match edge rows");
        }
        graph.adj.assign(graph.n, {});
        for (const auto [u, v] : graph.edges) {
            graph.adj[u].push_back(v);
            graph.adj[v].push_back(u);
        }
    } else {
        for (int v = 0; v < graph.n; ++v) {
            if (!row_seen[v]) throw ParseError(line_number, "missing adjacency row");
        }
        for (int v = 0; v < graph.n; ++v) {
            for (const int u : adjacency_rows[v]) {
                if (!std::binary_search(adjacency_rows[u].begin(),
                                        adjacency_rows[u].end(), v)) {
                    throw ParseError(line_number,
                                     "asymmetric adjacency relation at " +
                                         std::to_string(v) + "," +
                                         std::to_string(u));
                }
                if (v < u) graph.edges.emplace_back(v, u);
            }
        }
        std::sort(graph.edges.begin(), graph.edges.end());
        if (static_cast<std::int64_t>(graph.edges.size()) != graph.declared_m) {
            throw ParseError(line_number,
                             "declared edge count does not match adjacency rows");
        }
        graph.adj = std::move(adjacency_rows);
    }
    return graph;
}

bool is_deleted_edge(int x, int y, const std::pair<int, int>& deleted) {
    return (x == deleted.first && y == deleted.second) ||
           (x == deleted.second && y == deleted.first);
}

DistanceStats all_pairs_stats(const Graph& graph,
                              const std::pair<int, int>* deleted) {
    constexpr int infinity = std::numeric_limits<int>::max();
    DistanceStats stats;
    std::vector<int> distance(graph.n);
    std::queue<int> queue;

    for (int source = 0; source < graph.n; ++source) {
        std::fill(distance.begin(), distance.end(), infinity);
        while (!queue.empty()) queue.pop();
        distance[source] = 0;
        queue.push(source);
        while (!queue.empty()) {
            const int v = queue.front();
            queue.pop();
            for (const int u : graph.adj[v]) {
                if (deleted != nullptr && is_deleted_edge(v, u, *deleted)) continue;
                if (distance[u] == infinity) {
                    distance[u] = distance[v] + 1;
                    queue.push(u);
                }
            }
        }
        for (int target = source + 1; target < graph.n; ++target) {
            const int d = distance[target];
            if (d == infinity) {
                stats.connected = false;
                if (deleted != nullptr) {
                    stats.over_two.push_back({{source, target}, infinity});
                }
            } else {
                stats.diameter = std::max(stats.diameter, d);
                if (deleted != nullptr && d > 2) {
                    stats.over_two.push_back({{source, target}, d});
                }
            }
        }
    }
    return stats;
}

std::string display_distance(int distance, bool connected) {
    if (!connected || distance == std::numeric_limits<int>::max()) return "INF";
    return std::to_string(distance);
}

struct Options {
    std::string input_path;
    std::string ledger_path = "-";
    int expected_n = 25;
    std::int64_t minimum_edges = 157;
};

Options parse_options(int argc, char** argv) {
    if (argc < 2) {
        throw std::runtime_error(
            "usage: verifier_a INPUT [--expect-n N] [--min-edges M] "
            "[--ledger PATH|-]");
    }
    Options options;
    options.input_path = argv[1];
    for (int i = 2; i < argc; ++i) {
        const std::string flag = argv[i];
        if (i + 1 >= argc) throw std::runtime_error("missing value for " + flag);
        const std::string value = argv[++i];
        if (flag == "--expect-n") {
            options.expected_n = parse_integer<int>(value, 0, "--expect-n");
            if (options.expected_n < 1)
                throw std::runtime_error("--expect-n must be positive");
        } else if (flag == "--min-edges") {
            options.minimum_edges =
                parse_integer<std::int64_t>(value, 0, "--min-edges");
            if (options.minimum_edges < 0)
                throw std::runtime_error("--min-edges must be nonnegative");
        } else if (flag == "--ledger") {
            options.ledger_path = value;
        } else {
            throw std::runtime_error("unknown option: " + flag);
        }
    }
    return options;
}

void write_ledger(std::ostream& out, const Graph& graph,
                  const DistanceStats& original,
                  const std::vector<DistanceStats>& deleted_stats,
                  int critical_edges) {
    out << "p d2c-ledger-a " << graph.n << ' ' << graph.edges.size() << '\n';
    out << "original connected " << (original.connected ? 1 : 0)
        << " diameter "
        << display_distance(original.diameter, original.connected) << '\n';
    for (std::size_t i = 0; i < graph.edges.size(); ++i) {
        const auto [u, v] = graph.edges[i];
        const DistanceStats& stats = deleted_stats[i];
        out << "deleted " << u << ' ' << v << " connected "
            << (stats.connected ? 1 : 0) << " diameter "
            << display_distance(stats.diameter, stats.connected)
            << " witness_count " << stats.over_two.size() << '\n';
        for (const auto& witness : stats.over_two) {
            out << "w " << witness.first.first << ' ' << witness.first.second
                << " distance "
                << display_distance(witness.second,
                                    witness.second !=
                                        std::numeric_limits<int>::max())
                << '\n';
        }
    }
    out << "end critical_edges " << critical_edges << " total_edges "
        << graph.edges.size() << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    Options options;
    try {
        options = parse_options(argc, argv);
    } catch (const std::exception& error) {
        std::cerr << "VERIFIER_A_USAGE_ERROR message=" << error.what() << '\n';
        return 2;
    }

    Graph graph;
    try {
        graph = parse_graph(options.input_path);
    } catch (const ParseError& error) {
        std::cerr << "VERIFIER_A_PARSE_ERROR line=" << error.line
                  << " message=" << error.what() << '\n';
        return 2;
    }

    const DistanceStats original = all_pairs_stats(graph, nullptr);
    std::vector<DistanceStats> deleted_stats;
    deleted_stats.reserve(graph.edges.size());
    int critical_edges = 0;
    for (const auto& edge : graph.edges) {
        deleted_stats.push_back(all_pairs_stats(graph, &edge));
        if (!deleted_stats.back().over_two.empty()) ++critical_edges;
    }

    const bool diameter_exactly_two = original.connected && original.diameter == 2;
    const bool edge_critical =
        critical_edges == static_cast<int>(graph.edges.size());
    const bool order_ok = graph.n == options.expected_n;
    const bool threshold_ok =
        static_cast<std::int64_t>(graph.edges.size()) >= options.minimum_edges;
    const bool target_accept =
        diameter_exactly_two && edge_critical && order_ok && threshold_ok;

    std::ofstream ledger_file;
    std::ostream* ledger = &std::cout;
    if (options.ledger_path != "-") {
        ledger_file.open(options.ledger_path, std::ios::trunc);
        if (!ledger_file) {
            std::cerr << "VERIFIER_A_IO_ERROR message=cannot write ledger: "
                      << options.ledger_path << '\n';
            return 2;
        }
        ledger = &ledger_file;
    }
    write_ledger(*ledger, graph, original, deleted_stats, critical_edges);
    ledger->flush();
    if (!*ledger) {
        std::cerr << "VERIFIER_A_IO_ERROR message=ledger write failed\n";
        return 2;
    }

    std::cout << "VERIFIER_A_SUMMARY\n";
    std::cout << "input=" << options.input_path << '\n';
    std::cout << "format=" << graph.format << '\n';
    std::cout << "n=" << graph.n << '\n';
    std::cout << "declared_edges=" << graph.declared_m << '\n';
    std::cout << "actual_edges=" << graph.edges.size() << '\n';
    std::cout << "expect_n=" << options.expected_n << '\n';
    std::cout << "min_edges=" << options.minimum_edges << '\n';
    std::cout << "simple=true\n";
    std::cout << "connected=" << (original.connected ? "true" : "false") << '\n';
    std::cout << "original_diameter="
              << display_distance(original.diameter, original.connected) << '\n';
    std::cout << "diameter_exactly_2="
              << (diameter_exactly_two ? "true" : "false") << '\n';
    std::cout << "critical_edges=" << critical_edges << '/' << graph.edges.size()
              << '\n';
    std::cout << "edge_critical=" << (edge_critical ? "true" : "false") << '\n';
    std::cout << "order_ok=" << (order_ok ? "true" : "false") << '\n';
    std::cout << "threshold_ok=" << (threshold_ok ? "true" : "false") << '\n';
    std::cout << "ledger=" << options.ledger_path << '\n';
    std::cout << "target_accept=" << (target_accept ? "true" : "false") << '\n';
    return target_accept ? 0 : 1;
}
