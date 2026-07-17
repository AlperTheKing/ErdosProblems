#include <algorithm>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr std::uint32_t kMaximumLimit = 4'000'000'000U;
constexpr std::uint64_t kFnvOffset = 14'695'981'039'346'656'037ULL;
constexpr std::uint64_t kFnvPrime = 1'099'511'628'211ULL;

bool allowed(std::uint32_t n) {
    return n >= 2 && n % 3 != 1;
}

void fnv_byte(std::uint64_t& digest, std::uint8_t value) {
    digest ^= value;
    digest *= kFnvPrime;
}

void fnv_u32(std::uint64_t& digest, std::uint32_t value) {
    for (unsigned shift = 0; shift < 32; shift += 8) {
        fnv_byte(digest, static_cast<std::uint8_t>(value >> shift));
    }
}

std::string hex_u64(std::uint64_t value) {
    std::ostringstream out;
    out << std::hex << std::setfill('0') << std::setw(16) << value;
    return out.str();
}

void build_odd_spf(std::uint32_t maximum, std::vector<std::uint16_t>& odd_spf) {
    for (std::uint32_t p = 3;
         static_cast<std::uint64_t>(p) * p <= maximum;
         p += 2) {
        if (odd_spf[p >> 1] != 0) continue;
        const auto step = 2ULL * p;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
             multiple <= maximum;
             multiple += step) {
            auto& entry = odd_spf[static_cast<std::size_t>(multiple >> 1)];
            if (entry == 0) entry = static_cast<std::uint16_t>(p);
        }
    }
}

std::uint32_t prime_factor(
    std::uint32_t value, const std::vector<std::uint16_t>& odd_spf
) {
    if ((value & 1U) == 0) return 2;
    const auto factor = odd_spf[value >> 1];
    return factor == 0 ? value : factor;
}

using Factorization = std::vector<std::pair<std::uint32_t, unsigned>>;

Factorization factorize(
    std::uint32_t value, const std::vector<std::uint16_t>& odd_spf
) {
    Factorization factors;
    while (value > 1) {
        const auto p = prime_factor(value, odd_spf);
        unsigned exponent = 0;
        do {
            value /= p;
            ++exponent;
        } while (value > 1 && value % p == 0);
        factors.emplace_back(p, exponent);
    }
    return factors;
}

void enumerate_divisors(
    const Factorization& factors, std::vector<std::uint32_t>& divisors
) {
    divisors.clear();
    divisors.push_back(1);
    for (const auto& [p, exponent] : factors) {
        const auto old_size = divisors.size();
        std::uint32_t power = 1;
        for (unsigned e = 0; e < exponent; ++e) {
            power *= p;
            for (std::size_t i = 0; i < old_size; ++i) {
                divisors.push_back(divisors[i] * power);
            }
        }
    }
}

struct Record {
    std::uint32_t h = 0;
    std::uint32_t d = 0;
    Factorization factors;
    std::vector<std::uint32_t> witness_endpoints;
};

struct RootRecords {
    std::uint32_t root = 0;
    std::uint32_t maximum_d = 0;
    std::vector<Record> records;
};

std::uint32_t seed_root(std::uint32_t endpoint) {
    const auto shifted = endpoint - 1;
    return 1 + (shifted >> std::countr_zero(shifted));
}

void write_factorization(std::ostream& out, const Factorization& factors) {
    out << '[';
    for (std::size_t i = 0; i < factors.size(); ++i) {
        if (i != 0) out << ',';
        out << '[' << factors[i].first << ',' << factors[i].second << ']';
    }
    out << ']';
}

void write_records(std::ostream& out, const RootRecords& root) {
    out << "{\"root\":" << root.root
        << ",\"dyadic_bin\":" << std::bit_width(root.root - 1) - 1
        << ",\"maximum_d\":" << root.maximum_d << ",\"records\":[";
    for (std::size_t i = 0; i < root.records.size(); ++i) {
        if (i != 0) out << ',';
        const auto& record = root.records[i];
        out << "{\"h\":" << record.h << ",\"d\":" << record.d
            << ",\"h_plus_1_factorization\":";
        write_factorization(out, record.factors);
        out << ",\"witness_endpoints\":[";
        for (std::size_t j = 0; j < record.witness_endpoints.size(); ++j) {
            if (j != 0) out << ',';
            out << record.witness_endpoints[j];
        }
        out << "]}";
    }
    out << "]}";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: C109_fixed_root_records LIMIT OUTPUT_JSON\n";
            return 2;
        }
        const auto parsed_limit = std::stoull(argv[1]);
        if (parsed_limit < 1'000 || parsed_limit > kMaximumLimit) {
            throw std::runtime_error("LIMIT must lie in [1000,4000000000]");
        }
        const auto limit = static_cast<std::uint32_t>(parsed_limit);
        const auto started = std::chrono::steady_clock::now();

        std::vector<std::uint16_t> odd_spf(
            static_cast<std::size_t>((static_cast<std::uint64_t>(limit) + 1) / 2) + 1
        );
        build_odd_spf(limit + 1, odd_spf);
        const auto spf_finished = std::chrono::steady_clock::now();

        std::vector<std::uint8_t> generated(static_cast<std::size_t>(limit) + 1);
        std::vector<std::uint32_t> divisors;
        divisors.reserve(4096);
        std::vector<std::pair<std::uint32_t, std::uint32_t>> pairs;
        pairs.reserve(2048);
        RootRecords roots[] = {{54, 0, {}}, {62, 0, {}}};
        std::uint64_t generated_digest = kFnvOffset;
        std::uint64_t record_digest = kFnvOffset;
        std::uint64_t hard_count = 0;

        for (std::uint32_t n = 2; n <= limit; ++n) {
            bool is_generated = n == 2 || n == 3;
            bool is_hard = false;
            Factorization factors;
            pairs.clear();
            if (!is_generated && allowed(n)) {
                factors = factorize(n + 1, odd_spf);
                enumerate_divisors(factors, divisors);
                for (const auto left : divisors) {
                    if (left < 2) continue;
                    const auto right = (n + 1) / left;
                    if (left >= right) continue;
                    if (!allowed(left) || !allowed(right)) continue;
                    pairs.emplace_back(left, right);
                    if (generated[left] && generated[right]) is_generated = true;
                }
                if (!is_generated && !pairs.empty() && (n & 1U) == 0) {
                    const auto product = n + 1;
                    const bool easy_seed_three =
                        product % 3 == 0 && product / 3 != 3 && allowed(product / 3);
                    is_hard = !easy_seed_three;
                }
            }
            generated[n] = static_cast<std::uint8_t>(is_generated);
            fnv_byte(generated_digest, generated[n]);
            if (is_hard) {
                ++hard_count;
                for (auto& root : roots) {
                    std::vector<std::uint32_t> endpoints;
                    for (const auto [left, right] : pairs) {
                        for (const auto endpoint : {left, right}) {
                            if (!generated[endpoint] && seed_root(endpoint) == root.root) {
                                endpoints.push_back(endpoint);
                            }
                        }
                    }
                    std::sort(endpoints.begin(), endpoints.end());
                    endpoints.erase(std::unique(endpoints.begin(), endpoints.end()), endpoints.end());
                    const auto d = static_cast<std::uint32_t>(pairs.size());
                    if (!endpoints.empty() && d > root.maximum_d) {
                        root.maximum_d = d;
                        root.records.push_back({n, d, factors, endpoints});
                        fnv_u32(record_digest, root.root);
                        fnv_u32(record_digest, n);
                        fnv_u32(record_digest, d);
                    }
                }
            }
            if (n == limit) break;
        }
        const auto finished = std::chrono::steady_clock::now();

        std::ofstream out(argv[2], std::ios::binary);
        if (!out) throw std::runtime_error("could not open output JSON");
        out << "{\n  \"schema\":\"C109-fixed-root-records-v1\",\n"
            << "  \"limit\":" << limit << ",\n"
            << "  \"threads_used\":1,\n"
            << "  \"exact_integer_acceptance\":true,\n"
            << "  \"hard_count\":" << hard_count << ",\n"
            << "  \"roots\":[\n    ";
        write_records(out, roots[0]);
        out << ",\n    ";
        write_records(out, roots[1]);
        out << "\n  ],\n  \"digests\":{\"generated_2_through_limit\":\""
            << hex_u64(generated_digest) << "\",\"fixed_root_record_events\":\""
            << hex_u64(record_digest) << "\"},\n"
            << "  \"timing_seconds\":{\"spf\":"
            << std::chrono::duration<double>(spf_finished - started).count()
            << ",\"scan\":"
            << std::chrono::duration<double>(finished - spf_finished).count()
            << "}\n}\n";
        std::cout << "limit=" << limit << " hard=" << hard_count
                  << " root54_d=" << roots[0].maximum_d
                  << " root62_d=" << roots[1].maximum_d << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
