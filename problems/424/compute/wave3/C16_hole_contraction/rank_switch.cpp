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
constexpr std::size_t kMaxDepth = 63;
constexpr std::uint16_t kGenerationOffset = 5;

bool is_allowed(std::uint32_t value) {
    return value >= 2 && value % 3 != 1;
}

struct Audit {
    std::uint64_t failure_events = 0;
    std::uint32_t first_x = 0;
    std::uint16_t first_depth = 0;
    std::int64_t maximum_excess = 0;
    std::uint32_t maximum_x = 0;
    std::uint16_t maximum_depth = 0;

    void observe(
        std::uint32_t x,
        std::uint16_t depth,
        std::uint64_t source,
        std::uint64_t target
    ) {
        const auto excess = static_cast<std::int64_t>(source) -
            static_cast<std::int64_t>(target);
        if (excess > 0) {
            ++failure_events;
            if (first_x == 0) {
                first_x = x;
                first_depth = depth;
            }
        }
        if (excess > maximum_excess) {
            maximum_excess = excess;
            maximum_x = x;
            maximum_depth = depth;
        }
    }
};

void write_audit(std::ostream& out, const Audit& audit) {
    out << "{\"failure_events\":" << audit.failure_events
        << ",\"first_X\":" << audit.first_x
        << ",\"first_depth\":" << audit.first_depth
        << ",\"maximum_excess\":" << audit.maximum_excess
        << ",\"maximum_excess_X\":" << audit.maximum_x
        << ",\"maximum_excess_depth\":" << audit.maximum_depth << "}";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: rank_switch LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 100 || parsed_limit > 1000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [100, 1000000000]");
    }
    const std::uint32_t limit = static_cast<std::uint32_t>(parsed_limit);

    std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 2);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t p = 2;
         static_cast<std::uint64_t>(p) * p <=
             static_cast<std::uint64_t>(limit) + 1;
         ++p) {
        if (spf[p] != p) continue;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(p) * p;
             multiple <= static_cast<std::uint64_t>(limit) + 1;
             multiple += p) {
            if (spf[multiple] == multiple) spf[multiple] = p;
        }
    }

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
    std::vector<std::uint16_t> generation_depth(
        static_cast<std::size_t>(limit) + 1, kUnset
    );
    std::vector<std::uint16_t> obstruction_depth(
        static_cast<std::size_t>(limit) + 1, kUnset
    );
    member[2] = member[3] = 1;
    generation_depth[2] = generation_depth[3] = 0;

    std::array<std::uint64_t, kMaxDepth + 1> hard_exact{};
    std::array<std::uint64_t, kMaxDepth + 1> healed_exact{};
    std::array<std::uint64_t, kMaxDepth + 1> hard_cumulative{};
    std::array<std::uint64_t, kMaxDepth + 1> healed_cumulative{};
    std::array<std::uint64_t, kMaxDepth + 1> grounded_cumulative{};
    Audit depth_majorization;
    Audit grounded_majorization;
    std::uint16_t maximum_generation_depth = 0;
    std::uint16_t maximum_obstruction_depth = 0;
    std::uint64_t hard_total = 0;
    std::uint64_t healed_total = 0;

    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);
    for (std::uint32_t n = 4; n <= limit; ++n) {
        bool has_admissible_split = false;
        std::uint16_t best_generation_depth = kUnset;
        std::uint16_t blocking_depth = 0;

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

        for (const std::uint32_t left : divisors) {
            if (left < 2) continue;
            const std::uint32_t right = product / left;
            if (left >= right) continue;
            if (!is_allowed(left) || !is_allowed(right)) continue;
            has_admissible_split = true;

            if (member[left] && member[right]) {
                const auto candidate = static_cast<std::uint16_t>(
                    1 + std::max(generation_depth[left], generation_depth[right])
                );
                best_generation_depth = std::min(
                    best_generation_depth, candidate
                );
                member[n] = 1;
            } else {
                std::uint16_t pair_block = kUnset;
                if (!member[left]) {
                    if (obstruction_depth[left] == kUnset) {
                        throw std::runtime_error("unset left obstruction depth");
                    }
                    pair_block = obstruction_depth[left];
                }
                if (!member[right]) {
                    if (obstruction_depth[right] == kUnset) {
                        throw std::runtime_error("unset right obstruction depth");
                    }
                    pair_block = std::min(pair_block, obstruction_depth[right]);
                }
                blocking_depth = std::max(blocking_depth, pair_block);
            }
        }

        if (member[n]) {
            if (best_generation_depth == kUnset) {
                throw std::runtime_error("generated value has no witness depth");
            }
            generation_depth[n] = best_generation_depth;
            maximum_generation_depth = std::max(
                maximum_generation_depth, best_generation_depth
            );

            if ((n & 1U) != 0) {
                const std::uint32_t parent = (n + 1) / 2;
                if (is_allowed(parent) && !member[parent]) {
                    const std::uint16_t missing_depth = obstruction_depth[parent];
                    const std::uint16_t child_depth = generation_depth[n];
                    if (missing_depth > kMaxDepth || child_depth > kMaxDepth) {
                        throw std::runtime_error("rank depth exceeds audit range");
                    }
                    ++healed_total;
                    ++healed_exact[missing_depth];
                    for (std::size_t d = missing_depth; d <= kMaxDepth; ++d) {
                        ++healed_cumulative[d];
                    }
                    const std::uint16_t grounded_threshold = std::max(
                        missing_depth,
                        static_cast<std::uint16_t>(
                            child_depth > kGenerationOffset
                                ? child_depth - kGenerationOffset
                                : 0
                        )
                    );
                    for (std::size_t d = grounded_threshold;
                         d <= kMaxDepth;
                         ++d) {
                        ++grounded_cumulative[d];
                    }
                }
            }
            continue;
        }

        if (!is_allowed(n)) continue;
        obstruction_depth[n] = has_admissible_split
            ? static_cast<std::uint16_t>(blocking_depth + 1)
            : 0;
        maximum_obstruction_depth = std::max(
            maximum_obstruction_depth, obstruction_depth[n]
        );

        if ((n & 1U) != 0 || !has_admissible_split) continue;
        const std::uint32_t seed3_parent = (n + 1) / 3;
        if ((n + 1) % 3 == 0 &&
            is_allowed(seed3_parent) &&
            seed3_parent != 3) {
            continue;
        }

        const std::uint16_t depth = obstruction_depth[n];
        if (depth > kMaxDepth) {
            throw std::runtime_error("hard depth exceeds audit range");
        }
        ++hard_total;
        ++hard_exact[depth];
        for (std::size_t d = depth; d <= kMaxDepth; ++d) {
            ++hard_cumulative[d];
        }
        for (std::uint16_t d = 0; d <= kMaxDepth; ++d) {
            depth_majorization.observe(
                n, d, hard_cumulative[d], healed_cumulative[d]
            );
            grounded_majorization.observe(
                n, d, hard_cumulative[d], grounded_cumulative[d]
            );
        }
    }

    if (hard_cumulative[kMaxDepth] != hard_total ||
        healed_cumulative[kMaxDepth] != healed_total) {
        throw std::runtime_error("cumulative rank count mismatch");
    }

    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n";
    out << "  \"schema_version\":1,\n";
    out << "  \"limit\":" << limit << ",\n";
    out << "  \"generation_offset\":" << kGenerationOffset << ",\n";
    out << "  \"maximum_generation_depth\":"
        << maximum_generation_depth << ",\n";
    out << "  \"maximum_obstruction_depth\":"
        << maximum_obstruction_depth << ",\n";
    out << "  \"hard_total\":" << hard_total << ",\n";
    out << "  \"healed_total\":" << healed_total << ",\n";
    out << "  \"depth_majorization\":";
    write_audit(out, depth_majorization);
    out << ",\n  \"grounded_majorization\":";
    write_audit(out, grounded_majorization);
    out << ",\n";
    out << "  \"depth_rows\":[\n";
    const auto last_depth = std::max(
        maximum_generation_depth, maximum_obstruction_depth
    );
    for (std::uint16_t d = 0; d <= last_depth; ++d) {
        out << "    {\"depth\":" << d
            << ",\"hard_exact\":" << hard_exact[d]
            << ",\"healed_exact\":" << healed_exact[d]
            << ",\"hard_le_depth\":" << hard_cumulative[d]
            << ",\"healed_le_depth\":" << healed_cumulative[d]
            << ",\"grounded_target\":" << grounded_cumulative[d]
            << "}" << (d == last_depth ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit
              << " max_gdepth=" << maximum_generation_depth
              << " max_mdepth=" << maximum_obstruction_depth
              << " hard=" << hard_total
              << " healed=" << healed_total
              << " depth_failures=" << depth_majorization.failure_events
              << " grounded_failures=" << grounded_majorization.failure_events
              << '\n';
    return 0;
}
