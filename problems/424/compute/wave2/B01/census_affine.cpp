#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    const std::uint64_t limit = argc > 1 ? std::strtoull(argv[1], nullptr, 10) : 100000000ULL;
    std::vector<std::uint8_t> member(limit + 1, 0);
    for (std::uint64_t seed : {2ULL, 3ULL, 5ULL}) {
        if (seed <= limit) member[seed] = 1;
    }

    std::uint64_t count = 0;
    std::uint64_t next_checkpoint = 10;
    std::uint64_t previous = 0;
    std::uint64_t max_gap = 0;
    std::uint64_t max_gap_end = 0;
    for (std::uint64_t n = 1; n <= limit; ++n) {
        if (!member[n] && n > 5) {
            const std::uint64_t m = n + 1;
            if ((m % 2 == 0 && m / 2 != 2 && member[m / 2]) ||
                (m % 3 == 0 && m / 3 != 3 && member[m / 3]) ||
                (m % 5 == 0 && m / 5 != 5 && member[m / 5])) {
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
