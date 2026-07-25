#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr int n = 26;
constexpr int orbit_count = 65;

int pair_index(int a, int b) {
    // Lexicographic index of {a,b} among the ten pairs of 0,...,4.
    int index = 0;
    for (int i = 0; i < 5; ++i) {
        for (int j = i + 1; j < 5; ++j, ++index) {
            if (i == a && j == b) return index;
        }
    }
    return -1;
}

int edge_orbit_key(const std::array<int, n>& position, int u, int v) {
    int pu = position[u];
    int pv = position[v];
    if (pu == 0 || pv == 0) {
        const int other = pu == 0 ? pv : pu;
        return (other - 1) / 5;
    }

    int cu = (pu - 1) / 5;
    int cv = (pv - 1) / 5;
    int tu = (pu - 1) % 5;
    int tv = (pv - 1) % 5;
    if (cu == cv) {
        int delta = (tv - tu + 5) % 5;
        delta = std::min(delta, 5 - delta);
        return 5 + 2 * cu + (delta - 1);
    }
    if (cu > cv) {
        std::swap(cu, cv);
        std::swap(tu, tv);
    }
    const int delta = (tv - tu + 5) % 5;
    return 15 + 5 * pair_index(cu, cv) + delta;
}

int duplicate_count(const std::array<int, n>& position,
                    const std::vector<std::pair<int, int>>& edges) {
    std::array<int, orbit_count> count{};
    for (const auto [u, v] : edges) {
        ++count[edge_orbit_key(position, u, v)];
    }
    int duplicates = 0;
    for (int value : count) {
        if (value > 1) duplicates += value - 1;
    }
    return duplicates;
}

void print_sigma(const std::array<int, n>& vertex_at_position) {
    std::array<int, n> sigma{};
    sigma[vertex_at_position[0]] = vertex_at_position[0];
    for (int cycle = 0; cycle < 5; ++cycle) {
        for (int phase = 0; phase < 5; ++phase) {
            const int here = 1 + 5 * cycle + phase;
            const int next = 1 + 5 * cycle + (phase + 1) % 5;
            sigma[vertex_at_position[here]] = vertex_at_position[next];
        }
    }
    std::cout << "sigma";
    for (int v = 0; v < n; ++v) std::cout << ' ' << sigma[v];
    std::cout << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "usage: r4_cyclic_pack_search GRAPH.edges SEED ITERATIONS\n";
        return 2;
    }
    std::ifstream in(argv[1]);
    if (!in) {
        std::cerr << "cannot open graph\n";
        return 3;
    }
    const std::uint64_t seed = std::stoull(argv[2]);
    const long long iterations = std::stoll(argv[3]);

    std::vector<std::pair<int, int>> edges;
    std::string line;
    while (std::getline(in, line)) {
        std::istringstream row(line);
        char tag = '\0';
        row >> tag;
        if (tag != 'e') continue;
        int u = -1;
        int v = -1;
        row >> u >> v;
        edges.emplace_back(u, v);
    }
    if (edges.size() != 61) {
        std::cerr << "expected 61 edges\n";
        return 4;
    }

    std::array<int, n> degree{};
    for (const auto [u, v] : edges) {
        ++degree[u];
        ++degree[v];
    }

    std::mt19937_64 rng(seed);
    std::uniform_real_distribution<double> uniform(0.0, 1.0);
    std::array<int, n> best_vertex_at{};
    int global_best = 61;

    const long long restart_length = 20000;
    for (long long start = 0; start < iterations; start += restart_length) {
        std::array<int, n> vertex_at{};
        std::iota(vertex_at.begin(), vertex_at.end(), 0);
        std::shuffle(vertex_at.begin(), vertex_at.end(), rng);
        while (degree[vertex_at[0]] > 5) {
            std::shuffle(vertex_at.begin(), vertex_at.end(), rng);
        }
        std::array<int, n> position{};
        for (int p = 0; p < n; ++p) position[vertex_at[p]] = p;

        int score = duplicate_count(position, edges);
        const long long stop =
            std::min(iterations, start + restart_length);
        for (long long step = start; step < stop; ++step) {
            std::uniform_int_distribution<int> slot(1, n - 1);
            int a = slot(rng);
            int b = slot(rng);
            if (a == b) continue;

            const int va = vertex_at[a];
            const int vb = vertex_at[b];
            std::swap(vertex_at[a], vertex_at[b]);
            position[va] = b;
            position[vb] = a;
            const int next_score = duplicate_count(position, edges);

            const double phase =
                static_cast<double>((step - start) % restart_length) /
                static_cast<double>(restart_length);
            const double temperature = 1.5 * (1.0 - phase) + 0.05;
            const bool accept =
                next_score <= score ||
                uniform(rng) <
                    std::exp(static_cast<double>(score - next_score) /
                             temperature);
            if (accept) {
                score = next_score;
            } else {
                std::swap(vertex_at[a], vertex_at[b]);
                position[va] = a;
                position[vb] = b;
            }

            if (score < global_best) {
                global_best = score;
                best_vertex_at = vertex_at;
                std::cerr << "best_duplicates=" << global_best
                          << " step=" << step << '\n';
                if (global_best == 0) {
                    print_sigma(best_vertex_at);
                    return 0;
                }
            }
        }
    }

    std::cout << "NO_HIT best_duplicates=" << global_best << '\n';
    print_sigma(best_vertex_at);
    return 1;
}
