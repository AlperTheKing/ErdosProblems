#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr std::uint16_t kUnset = std::numeric_limits<std::uint16_t>::max();
constexpr std::size_t kMaxRank = 63;
constexpr std::array<std::uint8_t, 4> kCaps{1, 2, 3, 8};

bool allowed(std::uint32_t n) {
    return n >= 2 && n % 3 != 1;
}

struct PrefixAudit {
    std::int64_t maximum_excess = std::numeric_limits<std::int64_t>::min();
    std::uint32_t maximum_x = 0;
    std::uint16_t maximum_rank = 0;
    std::uint64_t strict_failure_events = 0;
    std::uint64_t plus_one_failure_events = 0;
    std::uint32_t first_plus_one_x = 0;
    std::uint16_t first_plus_one_rank = 0;
    std::uint64_t first_plus_one_h = 0;
    std::uint64_t first_plus_one_q = 0;

    void observe(
        std::uint32_t x,
        std::uint16_t rank,
        std::uint64_t h,
        std::uint64_t q
    ) {
        const auto excess = static_cast<std::int64_t>(h) -
            static_cast<std::int64_t>(q);
        if (excess > maximum_excess) {
            maximum_excess = excess;
            maximum_x = x;
            maximum_rank = rank;
        }
        if (excess > 0) ++strict_failure_events;
        if (excess > 1) {
            ++plus_one_failure_events;
            if (first_plus_one_x == 0) {
                first_plus_one_x = x;
                first_plus_one_rank = rank;
                first_plus_one_h = h;
                first_plus_one_q = q;
            }
        }
    }
};

void write_audit(std::ostream& out, const PrefixAudit& audit) {
    out << "{\"maximum_excess\":" << audit.maximum_excess
        << ",\"maximum_X\":" << audit.maximum_x
        << ",\"maximum_rank\":" << audit.maximum_rank
        << ",\"strict_failure_events\":" << audit.strict_failure_events
        << ",\"plus_one_failure_events\":"
        << audit.plus_one_failure_events
        << ",\"first_plus_one_X\":" << audit.first_plus_one_x
        << ",\"first_plus_one_rank\":" << audit.first_plus_one_rank
        << ",\"first_plus_one_H\":" << audit.first_plus_one_h
        << ",\"first_plus_one_Q\":" << audit.first_plus_one_q << "}";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: forest_exit_cap LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 100 || parsed_limit > 2000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [100, 2000000000]");
    }
    const auto limit = static_cast<std::uint32_t>(parsed_limit);

    std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 2);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t p = 2;
         static_cast<std::uint64_t>(p) * p <=
             static_cast<std::uint64_t>(limit) + 1;
         ++p) {
        if (spf[p] != p) continue;
        for (std::uint64_t m = static_cast<std::uint64_t>(p) * p;
             m <= static_cast<std::uint64_t>(limit) + 1;
             m += p) {
            if (spf[m] == m) spf[m] = p;
        }
    }

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
    std::vector<std::uint16_t> rank(
        static_cast<std::size_t>(limit) + 1, kUnset
    );
    std::vector<std::uint32_t> component_root(
        static_cast<std::size_t>(limit) + 1, 0
    );
    std::vector<std::uint8_t> component_exit_count(
        static_cast<std::size_t>(limit) + 1, 0
    );
    member[2] = member[3] = 1;

    std::array<std::uint64_t, kMaxRank + 1> hard_cumulative{};
    std::array<std::array<std::uint64_t, kMaxRank + 1>, kCaps.size()>
        exit_cumulative{};
    std::array<std::uint64_t, kCaps.size()> selected_exit_totals{};
    std::array<PrefixAudit, kCaps.size()> audits{};
    std::uint64_t hard_total = 0;
    std::uint64_t exit_total = 0;
    std::uint64_t splitless_roots = 0;
    std::uint64_t hard_roots = 0;
    std::uint64_t exits_from_splitless_components = 0;
    std::uint64_t exits_from_hard_components = 0;
    std::uint64_t decomposition_failures = 0;
    std::uint16_t maximum_rank = 0;

    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);
    for (std::uint32_t n = 4; n <= limit; ++n) {
        if (!allowed(n)) continue;

        bool has_split = false;
        bool generated = false;
        std::uint16_t blocking_rank = 0;
        const std::uint32_t product = n + 1;
        std::uint32_t remaining = product;
        divisors.clear();
        divisors.push_back(1);
        while (remaining > 1) {
            const std::uint32_t p = spf[remaining];
            const std::size_t old_size = divisors.size();
            std::uint32_t power = 1;
            do {
                remaining /= p;
                power *= p;
                for (std::size_t i = 0; i < old_size; ++i) {
                    divisors.push_back(divisors[i] * power);
                }
            } while (remaining > 1 && spf[remaining] == p);
        }

        for (const std::uint32_t a : divisors) {
            if (a < 2) continue;
            const std::uint32_t b = product / a;
            if (a >= b || !allowed(a) || !allowed(b)) continue;
            has_split = true;
            if (member[a] && member[b]) {
                generated = true;
                continue;
            }
            std::uint16_t pair_block = kUnset;
            if (!member[a]) {
                if (rank[a] == kUnset) {
                    throw std::runtime_error("unset left obstruction rank");
                }
                pair_block = rank[a];
            }
            if (!member[b]) {
                if (rank[b] == kUnset) {
                    throw std::runtime_error("unset right obstruction rank");
                }
                pair_block = std::min(pair_block, rank[b]);
            }
            blocking_rank = std::max(blocking_rank, pair_block);
        }

        if (generated) {
            member[n] = 1;
            if ((n & 1U) != 0) {
                const std::uint32_t parent = (n + 1) / 2;
                if (allowed(parent) && !member[parent]) {
                    if (rank[parent] == kUnset || component_root[parent] == 0) {
                        throw std::runtime_error("target parent lacks forest data");
                    }
                    const std::uint32_t root = component_root[parent];
                    auto& ordinal = component_exit_count[root];
                    if (ordinal != std::numeric_limits<std::uint8_t>::max()) {
                        ++ordinal;
                    }
                    ++exit_total;
                    if (rank[root] == 0) {
                        ++exits_from_splitless_components;
                    } else {
                        ++exits_from_hard_components;
                    }
                    for (std::size_t i = 0; i < kCaps.size(); ++i) {
                        if (ordinal > kCaps[i]) continue;
                        ++selected_exit_totals[i];
                        for (std::size_t d = rank[parent]; d <= kMaxRank; ++d) {
                            ++exit_cumulative[i][d];
                        }
                    }
                }
            }
            continue;
        }

        rank[n] = has_split
            ? static_cast<std::uint16_t>(blocking_rank + 1)
            : 0;
        maximum_rank = std::max(maximum_rank, rank[n]);

        bool hard = false;
        if ((n & 1U) != 0) {
            const std::uint32_t parent = (n + 1) / 2;
            if (!allowed(parent) || member[parent] ||
                component_root[parent] == 0 || rank[parent] >= rank[n]) {
                ++decomposition_failures;
                component_root[n] = n;
            } else {
                component_root[n] = component_root[parent];
            }
        } else {
            const bool easy3 = product % 3 == 0 &&
                allowed(product / 3) && product / 3 != 3;
            if (easy3) {
                const std::uint32_t parent = product / 3;
                if (member[parent] || component_root[parent] == 0 ||
                    rank[parent] >= rank[n]) {
                    ++decomposition_failures;
                    component_root[n] = n;
                } else {
                    component_root[n] = component_root[parent];
                }
            } else {
                component_root[n] = n;
                if (has_split) {
                    hard = true;
                    ++hard_roots;
                } else {
                    ++splitless_roots;
                }
            }
        }

        if (!hard) continue;
        ++hard_total;
        for (std::size_t d = rank[n]; d <= kMaxRank; ++d) {
            ++hard_cumulative[d];
        }
        for (std::size_t i = 0; i < kCaps.size(); ++i) {
            for (std::uint16_t d = 0; d <= kMaxRank; ++d) {
                audits[i].observe(
                    n, d, hard_cumulative[d], exit_cumulative[i][d]
                );
            }
        }
    }

    if (hard_total != hard_roots) {
        throw std::runtime_error("hard roots and hard events disagree");
    }

    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n"
        << "  \"schema_version\":1,\n"
        << "  \"limit\":" << limit << ",\n"
        << "  \"forest\":\"odd holes use T2 parent; 3-easy even holes use T3 parent; splitless and hard holes are roots\",\n"
        << "  \"maximum_obstruction_rank\":" << maximum_rank << ",\n"
        << "  \"hard_total\":" << hard_total << ",\n"
        << "  \"healed_seed2_exits_total\":" << exit_total << ",\n"
        << "  \"splitless_roots\":" << splitless_roots << ",\n"
        << "  \"hard_roots\":" << hard_roots << ",\n"
        << "  \"exits_from_splitless_components\":"
        << exits_from_splitless_components << ",\n"
        << "  \"exits_from_hard_components\":"
        << exits_from_hard_components << ",\n"
        << "  \"decomposition_failures\":" << decomposition_failures << ",\n"
        << "  \"cap_audits\":[\n";
    for (std::size_t i = 0; i < kCaps.size(); ++i) {
        out << "    {\"cap\":" << static_cast<unsigned>(kCaps[i])
            << ",\"selected_exits\":" << selected_exit_totals[i]
            << ",\"rank_prefix\":";
        write_audit(out, audits[i]);
        out << "}" << (i + 1 == kCaps.size() ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit
              << " hard=" << hard_total
              << " exits=" << exit_total
              << " roots=" << splitless_roots + hard_roots
              << " decomposition_failures=" << decomposition_failures;
    for (std::size_t i = 0; i < kCaps.size(); ++i) {
        std::cout << " cap" << static_cast<unsigned>(kCaps[i])
                  << "_max=" << audits[i].maximum_excess
                  << " cap" << static_cast<unsigned>(kCaps[i])
                  << "_first_plus_one=" << audits[i].first_plus_one_x;
    }
    std::cout << '\n';
    return 0;
}
