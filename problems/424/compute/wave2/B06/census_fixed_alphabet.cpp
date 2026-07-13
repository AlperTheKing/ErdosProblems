#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>

int main(int argc, char** argv) {
    const std::uint64_t limit =
        argc > 1 ? std::strtoull(argv[1], nullptr, 10) : 100000000ULL;
    const std::uint64_t cutoff =
        argc > 2 ? std::strtoull(argv[2], nullptr, 10) : 100ULL;
    if (limit == std::numeric_limits<std::uint64_t>::max() ||
        limit > std::numeric_limits<std::size_t>::max() - 1) {
        throw std::invalid_argument("limit does not fit the address space");
    }

    constexpr std::array<std::uint32_t, 23> verified{
        2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50,
        51, 53, 65, 69, 77, 80, 81, 84, 87, 98, 99,
    };
    std::vector<std::uint32_t> multipliers;
    for (const auto value : verified) {
        if (value <= cutoff) multipliers.push_back(value);
    }
    if (multipliers.empty()) {
        throw std::invalid_argument("cutoff selects no verified multiplier");
    }

    std::vector<std::uint8_t> member(limit + 1, 0);
    for (const auto value : multipliers) {
        if (value <= limit) member[value] = 1;
    }

    std::uint64_t count = 0;
    std::uint64_t previous = 0;
    std::uint64_t max_gap = 0;
    std::uint64_t max_gap_end = 0;
    std::uint64_t next_checkpoint = 10;
    for (std::uint64_t n = 1; n <= limit; ++n) {
        if (!member[n]) {
            const auto shifted = n + 1;
            for (const auto multiplier : multipliers) {
                if (multiplier > shifted) break;
                if (shifted % multiplier != 0) continue;
                const auto parent = shifted / multiplier;
                if (parent != multiplier && member[parent]) {
                    member[n] = 1;
                    break;
                }
            }
        }
        if (member[n]) {
            ++count;
            if (previous && n - previous > max_gap) {
                max_gap = n - previous;
                max_gap_end = n;
            }
            previous = n;
        }
        if (n == next_checkpoint || n == limit) {
            std::cout << "K=" << cutoff << " D=" << multipliers.size()
                      << " X=" << n << " count=" << count
                      << " density="
                      << static_cast<long double>(count) / n
                      << " max_gap=" << max_gap
                      << " max_gap_interval=(" << max_gap_end - max_gap
                      << ',' << max_gap_end << ")\n";
            if (next_checkpoint <= limit / 10) next_checkpoint *= 10;
        }
    }
}
