#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

static std::vector<int> smallest_prime_factors(int limit) {
    std::vector<int> spf(limit + 1);
    std::iota(spf.begin(), spf.end(), 0);
    for (int p = 2; int64_t(p) * p <= limit; ++p) {
        if (spf[p] != p) continue;
        for (int64_t multiple = int64_t(p) * p; multiple <= limit; multiple += p) {
            if (spf[multiple] == multiple) spf[multiple] = p;
        }
    }
    return spf;
}

static void enumerate_divisors(
    const std::vector<std::pair<int, int>>& factors,
    int index,
    int64_t current,
    int64_t square_bound,
    std::vector<int>& out
) {
    if (index == static_cast<int>(factors.size())) {
        if (current >= 2 && current <= square_bound) out.push_back(static_cast<int>(current));
        return;
    }
    const auto [prime, exponent] = factors[index];
    int64_t power = 1;
    for (int e = 0; e <= exponent; ++e) {
        if (current * power > square_bound) break;
        enumerate_divisors(factors, index + 1, current * power, square_bound, out);
        power *= prime;
    }
}

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: census LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const int limit = std::stoi(argv[1]);
    const std::string output_path = argv[2];
    auto spf = smallest_prime_factors(limit + 1);
    std::vector<uint8_t> reached(limit + 1, 0);
    std::vector<uint16_t> depth(limit + 1, 0);
    if (limit >= 2) reached[2] = 1;
    if (limit >= 3) reached[3] = 1;

    int64_t count = (limit >= 2) + (limit >= 3);
    int previous = limit >= 3 ? 3 : (limit >= 2 ? 2 : 0);
    int maximum_gap = previous > 0 ? previous - 1 : limit;
    int gap_left = 0;
    int gap_right = previous;
    uint16_t maximum_depth = 0;
    std::vector<std::pair<int, int64_t>> powers;
    int next_power = 10;

    for (int value = 4; value <= limit; ++value) {
        int product = value + 1;
        int current = product;
        std::vector<std::pair<int, int>> factors;
        while (current > 1) {
            const int prime = spf[current];
            int exponent = 0;
            do {
                current /= prime;
                ++exponent;
            } while (current % prime == 0);
            factors.emplace_back(prime, exponent);
        }
        std::vector<int> divisors;
        enumerate_divisors(factors, 0, 1, static_cast<int64_t>(std::sqrt(product)), divisors);
        std::sort(divisors.begin(), divisors.end());
        for (int left : divisors) {
            const int right = product / left;
            if (left >= right) continue;
            if (reached[left] && reached[right]) {
                reached[value] = 1;
                depth[value] = static_cast<uint16_t>(1 + std::max(depth[left], depth[right]));
                maximum_depth = std::max(maximum_depth, depth[value]);
                ++count;
                const int gap = value - previous;
                if (gap > maximum_gap) {
                    maximum_gap = gap;
                    gap_left = previous;
                    gap_right = value;
                }
                previous = value;
                break;
            }
        }
        while (next_power <= limit && value == next_power) {
            powers.emplace_back(next_power, count);
            if (next_power > limit / 10) next_power = limit + 1;
            else next_power *= 10;
        }
    }
    if (powers.empty() || powers.back().first != limit) powers.emplace_back(limit, count);

    std::ofstream out(output_path);
    out << "{\n";
    out << "  \"schema_version\": 1,\n";
    out << "  \"arithmetic\": \"exact integer ascending divisor recursion\",\n";
    out << "  \"limit\": " << limit << ",\n";
    out << "  \"count\": " << count << ",\n";
    out << "  \"density_numerator\": " << count << ",\n";
    out << "  \"density_denominator\": " << limit << ",\n";
    out << "  \"maximum_depth\": " << maximum_depth << ",\n";
    out << "  \"maximum_gap\": " << maximum_gap << ",\n";
    out << "  \"maximum_gap_endpoints\": [" << gap_left << ", " << gap_right << "],\n";
    out << "  \"checkpoints\": [\n";
    for (std::size_t i = 0; i < powers.size(); ++i) {
        out << "    [" << powers[i].first << ", " << powers[i].second << "]";
        out << (i + 1 == powers.size() ? "\n" : ",\n");
    }
    out << "  ]\n";
    out << "}\n";
    std::cout << "limit=" << limit << " count=" << count
              << " max_gap=" << maximum_gap << " depth=" << maximum_depth << "\n";
    return 0;
}
