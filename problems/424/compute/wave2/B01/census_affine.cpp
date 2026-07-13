#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>

int main(int argc, char** argv) {
    const std::uint64_t limit = argc > 1 ? std::strtoull(argv[1], nullptr, 10) : 100000000ULL;
    if (limit == std::numeric_limits<std::uint64_t>::max() ||
        limit > std::numeric_limits<std::size_t>::max() - 1) {
        throw std::invalid_argument("limit does not fit the address space");
    }

    std::vector<std::uint8_t> member(limit + 1, 0);
    if (limit >= 2) member[2] = 1;
    if (limit >= 3) member[3] = 1;
    if (limit >= 5) member[5] = 1;

    std::uint64_t count = 0;
    std::uint64_t next_checkpoint = 10;
    std::uint64_t previous = 0;
    std::uint64_t max_gap = 0;
    std::uint64_t max_gap_end = 0;
    for (std::uint64_t n = 1; n <= limit; ++n) {
        if (!member[n] && n > 5) {
            const std::uint64_t shifted = n + 1;
            if ((shifted % 2 == 0 && shifted / 2 != 2 && member[shifted / 2]) ||
                (shifted % 3 == 0 && shifted / 3 != 3 && member[shifted / 3]) ||
                (shifted % 5 == 0 && shifted / 5 != 5 && member[shifted / 5])) {
                member[n] = 1;
            }
        }
        if (member[n]) {
            ++count;
            if (previous != 0 && n - previous > max_gap) {
                max_gap = n - previous;
                max_gap_end = n;
            }
            previous = n;
        }
        if (n == next_checkpoint || n == limit) {
            std::cout << "X=" << n << " count=" << count
                      << " density=" << static_cast<long double>(count) / n
                      << " max_gap=" << max_gap
                      << " max_gap_interval=(" << max_gap_end - max_gap << ',' << max_gap_end << ")\n";
            if (next_checkpoint <= limit / 10) next_checkpoint *= 10;
        }
    }
}
