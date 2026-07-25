#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <vector>

namespace {

constexpr int q = 5;
constexpr int old_n = 25;
constexpr int n = 26;
constexpr int infinity = 25;

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

using Colouring = std::array<std::array<int, n>, n>;

Colouring make_colouring(int a, int b, int c) {
    Colouring colour{};
    for (auto& row : colour) row.fill(-1);

    for (int u = 0; u < old_n; ++u) {
        const auto [xu, yu] = point(u);
        colour[u][infinity] = colour[infinity][u] = xu;
        for (int v = u + 1; v < old_n; ++v) {
            const auto [xv, yv] = point(v);
            const int dx = mod(xv - xu);
            const int dy = mod(yv - yu);
            const int midpoint_x = mod((xu + xv) * inv(2));
            const int h =
                mod(a * dx * dx + b * dx * dy + c * dy * dy);
            colour[u][v] = colour[v][u] = mod(midpoint_x + h);
        }
    }
    return colour;
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

bool valid(const Colouring& colour,
           int& bad_colour,
           std::vector<int>& witness) {
    const std::uint32_t all = (std::uint32_t{1} << n) - 1;
    for (int target = 0; target < q; ++target) {
        witness.clear();
        if (has_independent_set(colour, target, all, 6, witness)) {
            bad_colour = target;
            return false;
        }
    }
    return true;
}

void print_ledger(const Colouring& colour) {
    for (int u = 0; u < n; ++u) {
        for (int v = u + 1; v < n; ++v) {
            std::cout << u << ' ' << v << ' ' << colour[u][v] << '\n';
        }
    }
}

}  // namespace

int main() {
    int tested = 0;
    int best_prefix = -1;
    std::array<int, 3> best_parameters{};
    std::vector<int> witness;

    for (int a = 0; a < q; ++a) {
        for (int b = 0; b < q; ++b) {
            for (int c = 0; c < q; ++c) {
                ++tested;
                const Colouring colour = make_colouring(a, b, c);
                int bad_colour = -1;
                if (valid(colour, bad_colour, witness)) {
                    std::cerr << "HIT a=" << a << " b=" << b
                              << " c=" << c << '\n';
                    print_ledger(colour);
                    return 0;
                }
                if (bad_colour > best_prefix) {
                    best_prefix = bad_colour;
                    best_parameters = {a, b, c};
                }
            }
        }
    }

    std::cout << "NO_HIT tested=" << tested
              << " best_prefix=" << best_prefix
              << " best_a=" << best_parameters[0]
              << " best_b=" << best_parameters[1]
              << " best_c=" << best_parameters[2] << '\n';
    return 1;
}
