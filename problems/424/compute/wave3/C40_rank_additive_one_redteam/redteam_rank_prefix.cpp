#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace {

constexpr std::uint16_t kUnset = std::numeric_limits<std::uint16_t>::max();
constexpr std::size_t kRanks = 96;

bool allowed(std::uint32_t n) {
    return n >= 2 && n % 3 != 1;
}

std::uint32_t integer_sqrt(std::uint32_t n) {
    std::uint32_t low = 0;
    std::uint32_t high = std::min<std::uint32_t>(n, 65536U) + 1;
    while (low + 1 < high) {
        const std::uint32_t mid = low + (high - low) / 2;
        if (static_cast<std::uint64_t>(mid) * mid <= n) {
            low = mid;
        } else {
            high = mid;
        }
    }
    return low;
}

struct PairNode {
    std::uint32_t left;
    std::int32_t next;
};

struct Event {
    std::uint32_t x;
    std::uint16_t rank;
};

struct Model {
    std::vector<std::uint8_t> member;
    std::vector<std::uint16_t> rank;
    std::vector<Event> hard;
    std::vector<Event> targets;
    std::array<std::uint64_t, kRanks> hard_hist{};
    std::array<std::uint64_t, kRanks> target_hist{};
    std::uint16_t max_rank = 0;
    std::uint32_t first_direct_zero = 0;
    std::uint64_t direct_zero_count = 0;
    std::uint32_t first_two_step_zero = 0;
    std::uint64_t two_step_zero_count = 0;
    std::uint32_t first_arrived_chain_zero = 0;
    std::uint64_t arrived_chain_zero_count = 0;
    std::uint32_t largest_fiber_parent = 0;
    std::uint64_t largest_fiber_size = 0;
};

struct Sweep {
    std::int64_t maximum_excess = std::numeric_limits<std::int64_t>::min();
    std::uint32_t maximum_x = 0;
    std::uint16_t maximum_rank = 0;
    std::uint64_t positive_tests = 0;
    std::uint64_t plus_one_failures = 0;
    std::uint32_t first_positive_x = 0;
    std::uint16_t first_positive_rank = 0;
    std::uint32_t last_positive_x = 0;
    std::uint16_t last_positive_rank = 0;
};

class RedTeam {
  public:
    explicit RedTeam(std::uint32_t limit)
        : limit_(limit), head_(static_cast<std::size_t>(limit) + 1, -1) {}

    void build_pairs() {
        const std::uint32_t product_limit = limit_ + 1;
        const std::uint32_t root = integer_sqrt(product_limit);
        nodes_.reserve(static_cast<std::size_t>(limit_) * 3);
        for (std::uint32_t a = 2; a <= root; ++a) {
            if (!allowed(a)) continue;
            const std::uint32_t last_b = product_limit / a;
            for (std::uint32_t b = a + 1; b <= last_b; ++b) {
                if (!allowed(b)) continue;
                const std::uint32_t n = a * b - 1;
                nodes_.push_back({a, head_[n]});
                head_[n] = static_cast<std::int32_t>(nodes_.size() - 1);
            }
        }
    }

    Model compute(bool include_equal) const {
        Model out;
        out.member.assign(static_cast<std::size_t>(limit_) + 1, 0);
        out.rank.assign(static_cast<std::size_t>(limit_) + 1, kUnset);
        out.member[2] = out.member[3] = 1;
        std::unordered_map<std::uint32_t, std::uint64_t> forced_fibers;

        for (std::uint32_t n = 4; n <= limit_; ++n) {
            if (!allowed(n)) continue;
            const std::uint32_t product = n + 1;
            bool has_pair = false;
            bool generated = false;
            std::uint16_t blocking = 0;
            std::uint32_t pair_count = 0;
            std::uint32_t sole_missing = 0;
            std::uint32_t sole_missing_count = 0;

            auto inspect = [&](std::uint32_t a, std::uint32_t b) {
                has_pair = true;
                ++pair_count;
                if (out.member[a] && out.member[b]) {
                    generated = true;
                    return;
                }
                std::uint16_t pair_block = kUnset;
                if (!out.member[a]) {
                    if (out.rank[a] == kUnset) throw std::runtime_error("unset left rank");
                    pair_block = out.rank[a];
                    sole_missing = a;
                    ++sole_missing_count;
                }
                if (!out.member[b]) {
                    if (out.rank[b] == kUnset) throw std::runtime_error("unset right rank");
                    pair_block = std::min(pair_block, out.rank[b]);
                    sole_missing = b;
                    ++sole_missing_count;
                }
                blocking = std::max(blocking, pair_block);
            };

            for (std::int32_t i = head_[n]; i >= 0; i = nodes_[i].next) {
                const std::uint32_t a = nodes_[i].left;
                inspect(a, product / a);
            }
            if (include_equal) {
                const std::uint32_t a = integer_sqrt(product);
                if (a >= 2 && a * a == product && allowed(a)) inspect(a, a);
            }

            if (generated) {
                out.member[n] = 1;
                if ((n & 1U) != 0U) {
                    const std::uint32_t parent = (n + 1) / 2;
                    if (allowed(parent) && !out.member[parent]) {
                        if (out.rank[parent] >= kRanks) throw std::runtime_error("target rank overflow");
                        out.targets.push_back({n, out.rank[parent]});
                        ++out.target_hist[out.rank[parent]];
                    }
                }
                continue;
            }

            out.rank[n] = has_pair ? static_cast<std::uint16_t>(blocking + 1) : 0;
            out.max_rank = std::max(out.max_rank, out.rank[n]);
            if ((n & 1U) != 0U || !has_pair) continue;
            const std::uint32_t q3 = product / 3;
            if (product % 3 == 0 && allowed(q3) && (include_equal || q3 != 3)) continue;
            if (out.rank[n] >= kRanks) throw std::runtime_error("hard rank overflow");
            out.hard.push_back({n, out.rank[n]});
            ++out.hard_hist[out.rank[n]];

            if (!include_equal) {
                bool has_direct = false;
                bool has_two_step = false;
                bool has_arrived_chain = false;
                for (std::int32_t i = head_[n]; i >= 0; i = nodes_[i].next) {
                    const std::uint32_t a = nodes_[i].left;
                    const std::uint32_t b = product / a;
                    for (const std::uint32_t q : {a, b}) {
                        if (out.member[q]) continue;
                        std::uint32_t current = q;
                        for (std::uint32_t step = 1;; ++step) {
                            const std::uint64_t child = 2ULL * current - 1;
                            if (child > n) break;
                            if (out.member[child]) {
                                if (out.rank[current] <= out.rank[n]) {
                                    has_arrived_chain = true;
                                    if (step <= 2) has_two_step = true;
                                    if (step == 1) has_direct = true;
                                }
                                break;
                            }
                            current = static_cast<std::uint32_t>(child);
                        }
                    }
                }
                if (!has_direct) {
                    ++out.direct_zero_count;
                    if (out.first_direct_zero == 0) out.first_direct_zero = n;
                }
                if (!has_two_step) {
                    ++out.two_step_zero_count;
                    if (out.first_two_step_zero == 0) out.first_two_step_zero = n;
                }
                if (!has_arrived_chain) {
                    ++out.arrived_chain_zero_count;
                    if (out.first_arrived_chain_zero == 0) out.first_arrived_chain_zero = n;
                }
                if (pair_count == 1 && sole_missing_count == 1) {
                    const auto count = ++forced_fibers[sole_missing];
                    if (count > out.largest_fiber_size) {
                        out.largest_fiber_size = count;
                        out.largest_fiber_parent = sole_missing;
                    }
                }
            }
        }
        return out;
    }

    const std::vector<std::int32_t>& heads() const { return head_; }
    const std::vector<PairNode>& nodes() const { return nodes_; }

  private:
    std::uint32_t limit_;
    std::vector<std::int32_t> head_;
    std::vector<PairNode> nodes_;
};

Sweep sweep(
    const std::vector<Event>& hard,
    const std::vector<Event>& targets,
    bool parent_coordinate,
    bool exact_layers,
    std::uint16_t target_rank_offset = 0
) {
    std::vector<Event> credits = targets;
    if (parent_coordinate) {
        for (auto& event : credits) event.x = (event.x + 1) / 2;
    }
    std::sort(credits.begin(), credits.end(), [](const Event& a, const Event& b) {
        return std::pair{a.x, a.rank} < std::pair{b.x, b.rank};
    });

    std::array<std::uint64_t, kRanks> hc{};
    std::array<std::uint64_t, kRanks> qc{};
    Sweep out;
    std::size_t ti = 0;
    for (const auto& source : hard) {
        while (ti < credits.size() && credits[ti].x <= source.x) {
            ++qc[credits[ti].rank];
            ++ti;
        }
        ++hc[source.rank];
        std::uint64_t hs = 0;
        std::uint64_t qs_prefix = 0;
        for (std::uint16_t d = 0; d < kRanks; ++d) {
            std::uint64_t qs = 0;
            if (exact_layers) {
                hs = hc[d];
                const std::size_t tr = std::min<std::size_t>(d + target_rank_offset, kRanks - 1);
                qs = qc[tr];
            } else {
                hs += hc[d];
                qs_prefix += qc[d];
                qs = qs_prefix;
                if (target_rank_offset > 0 && static_cast<std::size_t>(d) + 1 < kRanks) {
                    qs += qc[d + 1];
                }
            }
            const auto excess = static_cast<std::int64_t>(hs) - static_cast<std::int64_t>(qs);
            if (excess > out.maximum_excess) {
                out.maximum_excess = excess;
                out.maximum_x = source.x;
                out.maximum_rank = d;
            }
            if (excess > 0) {
                ++out.positive_tests;
                if (out.first_positive_x == 0) {
                    out.first_positive_x = source.x;
                    out.first_positive_rank = d;
                }
                out.last_positive_x = source.x;
                out.last_positive_rank = d;
            }
            if (excess > 1) ++out.plus_one_failures;
        }
    }
    return out;
}

void write_sweep(std::ostream& out, const Sweep& s) {
    out << "{\"maximum_excess\":" << s.maximum_excess
        << ",\"maximum_X\":" << s.maximum_x
        << ",\"maximum_rank\":" << s.maximum_rank
        << ",\"positive_tests\":" << s.positive_tests
        << ",\"plus_one_failures\":" << s.plus_one_failures
        << ",\"first_positive_X\":" << s.first_positive_x
        << ",\"first_positive_rank\":" << s.first_positive_rank
        << ",\"last_positive_X\":" << s.last_positive_x
        << ",\"last_positive_rank\":" << s.last_positive_rank << "}";
}

void write_hist(
    std::ostream& out,
    const std::array<std::uint64_t, kRanks>& hist,
    std::uint16_t max_rank
) {
    out << "{";
    bool first = true;
    for (std::uint16_t r = 0; r <= max_rank; ++r) {
        if (hist[r] == 0) continue;
        if (!first) out << ",";
        first = false;
        out << "\"" << r << "\":" << hist[r];
    }
    out << "}";
}

std::uint32_t first_membership_difference(const Model& a, const Model& b) {
    for (std::uint32_t n = 2; n < a.member.size(); ++n) {
        if (a.member[n] != b.member[n]) return n;
    }
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: redteam_rank_prefix LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const std::uint64_t parsed = std::stoull(argv[1]);
    if (parsed < 100 || parsed > 100000000ULL) {
        throw std::runtime_error("LIMIT must lie in [100,100000000]");
    }
    const auto limit = static_cast<std::uint32_t>(parsed);
    RedTeam redteam(limit);
    redteam.build_pairs();
    const Model actual = redteam.compute(false);
    const Model square_leak = redteam.compute(true);

    const Sweep true_prefix = sweep(actual.hard, actual.targets, false, false);
    const Sweep parent_prefix = sweep(actual.hard, actual.targets, true, false);
    const Sweep exact_layer = sweep(actual.hard, actual.targets, false, true);
    const Sweep offset_one = sweep(actual.hard, actual.targets, false, false, 1);
    const Sweep square_prefix = sweep(square_leak.hard, square_leak.targets, false, false);

    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("cannot open output");
    out << "{\n  \"schema_version\":1,\n"
        << "  \"limit\":" << limit << ",\n"
        << "  \"pair_enumerator\":\"explicit allowed products a<b\",\n"
        << "  \"admissible_pair_count\":" << redteam.nodes().size() << ",\n"
        << "  \"hard_total\":" << actual.hard.size() << ",\n"
        << "  \"target_total\":" << actual.targets.size() << ",\n"
        << "  \"maximum_obstruction_rank\":" << actual.max_rank << ",\n"
        << "  \"true_child_coordinate_prefix\":";
    write_sweep(out, true_prefix);
    out << ",\n  \"parent_coordinate_prefix\":";
    write_sweep(out, parent_prefix);
    out << ",\n  \"exact_rank_layers\":";
    write_sweep(out, exact_layer);
    out << ",\n  \"target_rank_offset_one\":";
    write_sweep(out, offset_one);
    out << ",\n  \"missing_endpoint_chain_local\":{"
        << "\"direct_first_zero\":" << actual.first_direct_zero
        << ",\"direct_zero_count\":" << actual.direct_zero_count
        << ",\"two_step_first_zero\":" << actual.first_two_step_zero
        << ",\"two_step_zero_count\":" << actual.two_step_zero_count
        << ",\"any_arrived_boundary_first_zero\":" << actual.first_arrived_chain_zero
        << ",\"any_arrived_boundary_zero_count\":" << actual.arrived_chain_zero_count
        << "},\n"
        << "  \"unique_split_fiber\":{\"largest_parent\":"
        << actual.largest_fiber_parent << ",\"size\":"
        << actual.largest_fiber_size << "},\n"
        << "  \"parity_audit\":{\"hard_event_parity\":0,"
        << "\"target_child_parity\":1,\"same_coordinate_ties\":0,"
        << "\"target_parent_can_equal_seed_2\":false},\n"
        << "  \"distinctness_audit\":{\"first_square_leak_membership_difference\":"
        << first_membership_difference(actual, square_leak)
        << ",\"square_leak_hard_total\":" << square_leak.hard.size()
        << ",\"square_leak_target_total\":" << square_leak.targets.size()
        << ",\"square_leak_prefix\":";
    write_sweep(out, square_prefix);
    out << "},\n  \"hard_rank_histogram\":";
    write_hist(out, actual.hard_hist, actual.max_rank);
    out << ",\n  \"target_rank_histogram\":";
    write_hist(out, actual.target_hist, actual.max_rank);
    out << "\n}\n";
    if (!out) throw std::runtime_error("write failed");

    std::cout << "limit=" << limit
              << " pairs=" << redteam.nodes().size()
              << " hard=" << actual.hard.size()
              << " targets=" << actual.targets.size()
              << " max_excess=" << true_prefix.maximum_excess
              << " plus_one_failures=" << true_prefix.plus_one_failures
              << " first_square_leak=" << first_membership_difference(actual, square_leak)
              << "\n";
    return 0;
}
