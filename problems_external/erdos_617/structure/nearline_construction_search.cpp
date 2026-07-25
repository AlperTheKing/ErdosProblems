#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <optional>
#include <set>
#include <tuple>
#include <vector>

namespace {

constexpr int q = 5;
constexpr int old_n = q * q;
constexpr int n = old_n + 1;
constexpr int inf_vertex = old_n;

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

int vertex(int x, int y) {
    return mod(x) * q + mod(y);
}

std::pair<int, int> point(int v) {
    return {v / q, v % q};
}

int affine_colour(int u, int v) {
    const auto [x1, y1] = point(u);
    const auto [x2, y2] = point(v);
    const int dx = mod(x2 - x1);
    const int dy = mod(y2 - y1);
    if (dx == 0 || dy == 0) return 0;
    return mod(dy * inv(dx));
}

int new_neighbour_colour(int v) {
    const auto [x, y] = point(v);
    if (y == 0) return 0;
    if (x == 0) return y;
    return mod(y * inv(x));
}

using Colouring = std::array<std::array<int, n>, n>;

Colouring base_colouring() {
    Colouring colour{};
    for (auto& row : colour) row.fill(-1);
    for (int u = 0; u < old_n; ++u) {
        for (int v = u + 1; v < old_n; ++v) {
            colour[u][v] = colour[v][u] = affine_colour(u, v);
        }
        colour[u][inf_vertex] = colour[inf_vertex][u] =
            new_neighbour_colour(u);
    }
    return colour;
}

bool recolour(Colouring& colour,
              std::set<std::pair<int, int>>& touched,
              int u,
              int v,
              int target) {
    if (u > v) std::swap(u, v);
    const auto edge = std::pair{u, v};
    if (const auto [it, inserted] = touched.insert(edge); !inserted) {
        return colour[u][v] == target;
    }
    colour[u][v] = colour[v][u] = target;
    return true;
}

bool has_independent_set(const Colouring& colour,
                         int target_colour,
                         std::uint32_t candidates,
                         int need,
                         std::vector<int>& witness) {
    if (need == 0) return true;
    if (std::popcount(candidates) < need) return false;

    while (candidates) {
        if (std::popcount(candidates) < need) return false;
        const int v = std::countr_zero(candidates);
        candidates &= candidates - 1;

        std::uint32_t next = candidates;
        for (int w = v + 1; w < n; ++w) {
            if ((next & (std::uint32_t{1} << w)) &&
                colour[v][w] == target_colour) {
                next &= ~(std::uint32_t{1} << w);
            }
        }
        witness.push_back(v);
        if (has_independent_set(colour, target_colour, next, need - 1,
                                witness)) {
            return true;
        }
        witness.pop_back();
    }
    return false;
}

std::optional<std::pair<int, std::vector<int>>>
first_failure(const Colouring& colour) {
    const std::uint32_t all = (std::uint32_t{1} << n) - 1;
    for (int c = 0; c < q; ++c) {
        std::vector<int> witness;
        if (has_independent_set(colour, c, all, 6, witness)) {
            return std::pair{c, witness};
        }
    }
    return std::nullopt;
}

void print_edge_list(const Colouring& colour) {
    for (int u = 0; u < n; ++u) {
        for (int v = u + 1; v < n; ++v) {
            std::cout << u << ' ' << v << ' ' << colour[u][v] << '\n';
        }
    }
}

}  // namespace

int main() {
    const int O = vertex(0, 0);
    const int P = vertex(-1, 0);
    int candidates_tested = 0;
    int structurally_consistent = 0;

    for (int qx = 0; qx < q; ++qx) {
        for (int qy = 0; qy < q; ++qy) {
            const int Q = vertex(qx, qy);
            if (Q == O || Q == P) continue;

            std::array<int, q> intercept{};
            bool admissible_q = true;
            for (int m = 1; m < q; ++m) {
                intercept[m] = mod(qy - m * qx);
                if (intercept[m] == 0 || intercept[m] == m) {
                    admissible_q = false;
                }
            }
            if (!admissible_q) continue;

            for (int omitted = 1; omitted < q; ++omitted) {
                std::array<int, 3> triangle_colours{};
                int pos = 0;
                for (int m = 1; m < q; ++m) {
                    if (m != omitted) triangle_colours[pos++] = m;
                }
                std::sort(triangle_colours.begin(), triangle_colours.end());
                do {
                    for (int final_intercept = 0;
                         final_intercept < q;
                         ++final_intercept) {
                        if (final_intercept == 0 ||
                            final_intercept == omitted ||
                            final_intercept == intercept[omitted]) {
                            continue;
                        }

                        ++candidates_tested;
                        Colouring colour = base_colouring();
                        std::set<std::pair<int, int>> touched;
                        bool consistent = true;

                        // First forced point P: each L'_m is y=m(x+1).
                        for (int m = 1; m < q; ++m) {
                            for (int x = 1; x < q; ++x) {
                                const int r = vertex(x, m * (x + 1));
                                if (r == P) continue;
                                consistent &=
                                    recolour(colour, touched, O, r, m);
                            }
                        }

                        // Second forced point Q: M_m is the line of slope m
                        // through Q.  The common edge P-Q is deliberately
                        // omitted from every target colour.
                        for (int m = 1; m < q; ++m) {
                            for (int x = 0; x < q; ++x) {
                                const int w =
                                    vertex(x, m * x + intercept[m]);
                                if (w == Q) continue;
                                consistent &=
                                    recolour(colour, touched, P, w, m);
                            }
                        }

                        // Three colours consume the three edges on O,P,Q.
                        consistent &= recolour(
                            colour, touched, O, P, triangle_colours[0]);
                        consistent &= recolour(
                            colour, touched, O, Q, triangle_colours[1]);
                        consistent &= recolour(
                            colour, touched, P, Q, triangle_colours[2]);

                        // The omitted colour is closed by a full Q-star into
                        // another one of its parallel lines.
                        for (int x = 0; x < q; ++x) {
                            const int w =
                                vertex(x, omitted * x + final_intercept);
                            consistent &=
                                recolour(colour, touched, Q, w, omitted);
                        }
                        if (!consistent) continue;
                        ++structurally_consistent;

                        if (!first_failure(colour)) {
                            std::cerr
                                << "HIT Q=(" << qx << ',' << qy
                                << ") omitted=" << omitted
                                << " final_intercept=" << final_intercept
                                << " triangle=" << triangle_colours[0] << ','
                                << triangle_colours[1] << ','
                                << triangle_colours[2] << '\n';
                            print_edge_list(colour);
                            return 0;
                        }
                    }
                } while (std::next_permutation(triangle_colours.begin(),
                                               triangle_colours.end()));
            }
        }
    }

    std::cout << "NO_HIT candidates_tested=" << candidates_tested
              << " structurally_consistent=" << structurally_consistent
              << '\n';
    return 1;
}
