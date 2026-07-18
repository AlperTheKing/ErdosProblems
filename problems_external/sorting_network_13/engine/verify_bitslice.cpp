#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

int main(int argc, char** argv) {
    if (argc < 2 || argc > 3) {
        std::cerr << "usage: verify_bitslice NETWORK.net [EXPECTED_CES]\n";
        return 2;
    }
    std::ifstream in(argv[1]);
    if (!in) {
        std::cerr << "cannot open " << argv[1] << "\n";
        return 2;
    }
    std::string line;
    int n = -1;
    std::vector<std::pair<int, int>> pairs;
    while (std::getline(in, line)) {
        const auto hash = line.find('#');
        if (hash != std::string::npos) line.resize(hash);
        if (line.find_first_not_of(" \t\r\n") == std::string::npos) continue;
        if (n < 0) {
            char key = 0;
            if (std::sscanf(line.c_str(), " %c %d", &key, &n) != 2 || key != 'n') {
                throw std::runtime_error("first data line must be n <channels>");
            }
        } else {
            int lo = -1, hi = -1;
            if (std::sscanf(line.c_str(), " %d %d", &lo, &hi) != 2) continue;
            if (!(0 <= lo && lo < hi && hi < n)) throw std::runtime_error("invalid comparator");
            pairs.emplace_back(lo, hi);
        }
    }
    if (argc == 3 && pairs.size() != static_cast<std::size_t>(std::stoul(argv[2]))) {
        std::cerr << "unexpected comparator count " << pairs.size() << "\n";
        return 2;
    }
    if (n <= 0 || n >= 31) throw std::runtime_error("unsupported channel count");

    const auto started = std::chrono::steady_clock::now();
    std::uint32_t failures = 0;
    std::uint32_t first_failure = 0;
    const std::uint32_t inputs = std::uint32_t{1} << n;
    for (std::uint32_t input = 0; input < inputs; ++input) {
        std::uint32_t state = input;
        for (const auto [lo, hi] : pairs) {
            const bool low_one = ((state >> lo) & 1U) != 0;
            const bool high_zero = ((state >> hi) & 1U) == 0;
            if (low_one && high_zero) state ^= (std::uint32_t{1} << lo) | (std::uint32_t{1} << hi);
        }
        bool sorted = true;
        for (int i = 0; i + 1 < n; ++i) {
            if (((state >> i) & 3U) == 1U) {
                sorted = false;
                break;
            }
        }
        if (!sorted) {
            if (failures == 0) first_failure = input;
            ++failures;
        }
    }
    const double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count();
    std::cout << "{\"verifier\":\"cpp-bitstate\",\"channels\":" << n
              << ",\"comparators\":" << pairs.size() << ",\"inputs\":" << inputs
              << ",\"failures\":" << failures << ",\"first_failure\":";
    if (failures == 0) std::cout << "null"; else std::cout << first_failure;
    std::cout << ",\"elapsed_s\":" << elapsed << "}\n";
    return failures == 0 ? 0 : 1;
}
