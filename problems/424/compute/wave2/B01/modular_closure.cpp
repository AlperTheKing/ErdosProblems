#include <array>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <queue>
#include <vector>

static std::vector<std::uint8_t> closure(std::uint64_t modulus) {
    std::vector<std::uint8_t> seen(modulus, 0);
    std::queue<std::uint64_t> pending;
    for (std::uint64_t seed : {1ULL, 2ULL, 4ULL}) {
        const auto residue = seed % modulus;
        if (!seen[residue]) {
            seen[residue] = 1;
            pending.push(residue);
        }
    }
    while (!pending.empty()) {
        const auto x = pending.front();
        pending.pop();
        for (const auto y : std::array<std::uint64_t, 3>{
                 2 * x, (3 * x + 1) % modulus, (5 * x + 3) % modulus}) {
            const auto residue = y % modulus;
            if (!seen[residue]) {
                seen[residue] = 1;
                pending.push(residue);
            }
        }
    }
    return seen;
}

int main(int argc, char** argv) {
    const int maximum_power = argc > 1 ? std::atoi(argv[1]) : 5;
    std::uint64_t modulus = 1;
    std::vector<std::uint8_t> previous;
    for (int power = 1; power <= maximum_power; ++power) {
        modulus *= 30;
        auto current = closure(modulus);
        std::uint64_t count = 0;
        for (auto value : current) count += value;
        std::cout << std::setprecision(12) << "power=" << power << " modulus=" << modulus
                  << " reachable=" << count
                  << " fraction=" << static_cast<long double>(count) / modulus;
        if (!previous.empty()) {
            std::array<std::uint64_t, 31> histogram{};
            const auto old_modulus = modulus / 30;
            for (std::uint64_t residue = 0; residue < old_modulus; ++residue) {
                if (!previous[residue]) continue;
                int lifts = 0;
                for (int digit = 0; digit < 30; ++digit) {
                    lifts += current[residue + digit * old_modulus];
                }
                ++histogram[lifts];
            }
            std::cout << " lift_hist=";
            for (int lifts = 0; lifts <= 30; ++lifts) {
                if (histogram[lifts]) std::cout << lifts << ':' << histogram[lifts] << ',';
            }
        }
        std::cout << '\n';
        previous = std::move(current);
    }
}
