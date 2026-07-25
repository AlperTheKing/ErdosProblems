#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using Edge = std::pair<int, int>;
using EdgeSet = std::set<Edge>;

void write_edge_graph(const std::filesystem::path& path, int n,
                      const EdgeSet& edges) {
    std::ofstream out(path, std::ios::trunc);
    if (!out) throw std::runtime_error("cannot write " + path.string());
    out << "p edge " << n << ' ' << edges.size() << '\n';
    for (const auto [u, v] : edges) out << "e " << u << ' ' << v << '\n';
}

void write_adj_graph(const std::filesystem::path& path, int n,
                     const EdgeSet& edges) {
    std::vector<std::vector<int>> adj(n);
    for (const auto [u, v] : edges) {
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    std::ofstream out(path, std::ios::trunc);
    if (!out) throw std::runtime_error("cannot write " + path.string());
    out << "p adj " << n << ' ' << edges.size() << '\n';
    for (int v = 0; v < n; ++v) {
        out << "a " << v << " :";
        for (const int u : adj[v]) out << ' ' << u;
        out << '\n';
    }
}

EdgeSet complete_bipartite(int left, int right) {
    EdgeSet edges;
    for (int u = 0; u < left; ++u) {
        for (int v = left; v < left + right; ++v) edges.emplace(u, v);
    }
    return edges;
}

EdgeSet complete_graph(int n) {
    EdgeSet edges;
    for (int u = 0; u < n; ++u) {
        for (int v = u + 1; v < n; ++v) edges.emplace(u, v);
    }
    return edges;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const std::filesystem::path output =
            argc >= 2 ? std::filesystem::path(argv[1])
                      : std::filesystem::path("fixtures");
        std::filesystem::create_directories(output);

        const EdgeSet k12_13 = complete_bipartite(12, 13);
        write_edge_graph(output / "k12_13.edge", 25, k12_13);

        const EdgeSet star = complete_bipartite(1, 4);
        write_edge_graph(output / "star_k1_4.edge", 5, star);

        EdgeSet c5{{0, 1}, {0, 4}, {1, 2}, {2, 3}, {3, 4}};
        write_edge_graph(output / "c5.edge", 5, c5);
        write_adj_graph(output / "c5.adj", 5, c5);

        EdgeSet dense = complete_graph(25);
        dense.erase({0, 1});
        write_edge_graph(output / "k25_minus_edge.edge", 25, dense);

        EdgeSet plus_edge = k12_13;
        plus_edge.emplace(0, 1);
        write_edge_graph(output / "k12_13_plus_edge.edge", 25, plus_edge);

        EdgeSet missing_edge = k12_13;
        missing_edge.erase({0, 12});
        write_edge_graph(output / "k12_13_missing_edge.edge", 25, missing_edge);

        EdgeSet disconnected{{0, 1}, {2, 3}};
        write_edge_graph(output / "disconnected.edge", 4, disconnected);

        {
            std::ofstream out(output / "bad_duplicate.edge", std::ios::trunc);
            out << "p edge 3 2\n"
                << "e 0 1\n"
                << "e 0 1\n";
        }
        {
            std::ofstream out(output / "bad_loop.edge", std::ios::trunc);
            out << "p edge 3 1\n"
                << "e 1 1\n";
        }
        {
            std::ofstream out(output / "bad_reversed.edge", std::ios::trunc);
            out << "p edge 3 1\n"
                << "e 1 0\n";
        }
        {
            std::ofstream out(output / "bad_count.edge", std::ios::trunc);
            out << "p edge 3 2\n"
                << "e 0 1\n";
        }
        {
            std::ofstream out(output / "bad_asymmetric.adj", std::ios::trunc);
            out << "p adj 3 1\n"
                << "a 0 : 1\n"
                << "a 1 :\n"
                << "a 2 :\n";
        }

        std::cout << "FIXTURES_A_OK directory=" << output.string()
                  << " count=13\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FIXTURES_A_FAILED message=" << error.what() << '\n';
        return 1;
    }
}
