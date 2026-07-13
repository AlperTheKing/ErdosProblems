#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>

static long double as_long_double(unsigned __int128 value) {
    constexpr std::uint64_t base = 1000000000000000000ULL;
    return static_cast<long double>(static_cast<std::uint64_t>(value / base)) * base +
           static_cast<std::uint64_t>(value % base);
}

int main(int argc, char** argv) {
    const std::uint64_t limit = argc > 1 ? std::strtoull(argv[1], nullptr, 10) : 100000000ULL;
    std::vector<std::uint32_t> representations(limit + 1, 0);
    unsigned __int128 first_moment = 0;
    unsigned __int128 second_moment = 0;
    std::uint64_t support = 0;
    std::uint32_t maximum = 0;
    std::uint64_t maximum_at = 0;
    std::uint64_t next_checkpoint = 10;

    for (std::uint64_t x = 1; x <= limit; ++x) {
        std::uint64_t value = (x == 1 || x == 2 || x == 4) ? 1 : 0;
        if (x % 2 == 0 && x / 2 != 1) value += representations[x / 2];
        if (x % 3 == 1 && (x - 1) / 3 != 2) value += representations[(x - 1) / 3];
        if (x % 5 == 3 && (x - 3) / 5 != 4) value += representations[(x - 3) / 5];
        if (value > UINT32_MAX) {
            std::cerr << "representation overflow at " << x << '\n';
            return 2;
        }
        representations[x] = static_cast<std::uint32_t>(value);
        support += value != 0;
        first_moment += value;
        second_moment += static_cast<unsigned __int128>(value) * value;
        if (value > maximum) {
            maximum = static_cast<std::uint32_t>(value);
            maximum_at = x;
        }

        if (x == next_checkpoint || x == limit) {
            const long double m1 = as_long_double(first_moment);
            const long double m2 = as_long_double(second_moment);
            std::cout << std::setprecision(12)
                      << "X=" << x << " support=" << support
                      << " R1=" << m1 << " R2=" << m2
                      << " R2_exponent=" << std::log(m2) / std::log(static_cast<long double>(x))
                      << " CS_density=" << m1 * m1 / (m2 * x)
                      << " max_r=" << maximum << " max_at=" << maximum_at << '\n';
            if (next_checkpoint <= limit / 10) next_checkpoint *= 10;
        }
    }
}
