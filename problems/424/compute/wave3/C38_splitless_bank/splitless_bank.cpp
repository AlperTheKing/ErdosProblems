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

constexpr std::uint16_t kUnsetRank =
    std::numeric_limits<std::uint16_t>::max();
constexpr std::uint32_t kUnsetRoot =
    std::numeric_limits<std::uint32_t>::max();
constexpr std::size_t kRankCount = 32;
constexpr std::uint16_t kNoRank =
    std::numeric_limits<std::uint16_t>::max();

bool allowed(std::uint32_t n) {
    return n >= 2 && n % 3 != 1;
}

bool hard_shape(std::uint32_t n, bool has_pair) {
    if ((n & 1U) != 0 || !has_pair) return false;
    if ((n + 1) % 3 != 0) return true;
    const std::uint32_t q = (n + 1) / 3;
    return !(allowed(q) && q != 3);
}

struct Witness {
    bool set = false;
    std::uint32_t x = 0;
    std::uint16_t rank = kNoRank;
    std::uint32_t root = 0;
    std::uint64_t hard = 0;
    std::uint64_t healed = 0;
    std::int64_t deficit = 0;
};

struct Audit {
    std::int64_t maximum_deficit = 0;
    Witness maximum;
    Witness first_positive;
    Witness first_over_one;

    void observe(
        std::uint32_t x,
        std::uint16_t rank,
        std::uint32_t root,
        std::uint64_t hard,
        std::uint64_t healed,
        std::int64_t deficit
    ) {
        const Witness row{true, x, rank, root, hard, healed, deficit};
        if (deficit > maximum_deficit) {
            maximum_deficit = deficit;
            maximum = row;
        }
        if (deficit > 0 && !first_positive.set) first_positive = row;
        if (deficit > 1 && !first_over_one.set) first_over_one = row;
    }
};

void write_witness(std::ostream& out, const Witness& row) {
    if (!row.set) {
        out << "null";
        return;
    }
    out << "{\"X\":" << row.x << ",\"rank\":";
    if (row.rank == kNoRank) out << "null";
    else out << row.rank;
    out << ",\"root\":";
    if (row.root == 0) out << "null";
    else out << row.root;
    out << ",\"H\":" << row.hard
        << ",\"Q\":" << row.healed
        << ",\"deficit\":" << row.deficit << "}";
}

void write_audit(std::ostream& out, const Audit& audit) {
    out << "{\"maximum_deficit\":" << audit.maximum_deficit
        << ",\"maximum_witness\":";
    write_witness(out, audit.maximum);
    out << ",\"first_positive\":";
    write_witness(out, audit.first_positive);
    out << ",\"first_over_one\":";
    write_witness(out, audit.first_over_one);
    out << "}";
}

struct Component {
    std::array<std::int32_t, kRankCount> net_exact{};
    std::array<std::uint32_t, kRankCount> healed_exact{};
    std::int64_t balance = 0;
};

enum class RootRule {
    min_endpoint,
    min_root,
    minimum_balance,
};

struct Policy {
    Policy(
        std::string policy_name,
        RootRule policy_rule,
        std::size_t node_count,
        std::size_t expected_roots
    ) : name(std::move(policy_name)),
        rule(policy_rule),
        root_of(node_count, kUnsetRoot) {
        components.reserve(expected_roots);
    }

    std::string name;
    RootRule rule;
    std::vector<std::uint32_t> root_of;
    std::vector<Component> components;
    Audit unranked;
    std::array<Audit, 3> rank_offset;

    void add_root(std::uint32_t node, std::uint32_t root_id) {
        if (root_id != components.size()) {
            throw std::runtime_error("splitless root ids lost synchronization");
        }
        root_of[node] = root_id;
        components.emplace_back();
    }

    std::uint32_t choose(
        const std::vector<std::uint32_t>& candidates,
        const std::vector<std::uint32_t>& root_values
    ) const {
        if (candidates.empty()) {
            throw std::runtime_error("reducible hole has no critical blocker");
        }
        std::uint32_t best = candidates.front();
        for (const std::uint32_t q : candidates) {
            const std::uint32_t q_root = root_of[q];
            const std::uint32_t best_root = root_of[best];
            if (q_root == kUnsetRoot || best_root == kUnsetRoot) {
                throw std::runtime_error("critical blocker has no splitless root");
            }
            bool take = false;
            if (rule == RootRule::min_endpoint) {
                take = q < best;
            } else if (rule == RootRule::min_root) {
                take = std::pair(root_values[q_root], q) <
                    std::pair(root_values[best_root], best);
            } else {
                take = std::tuple(
                    components[q_root].balance, root_values[q_root], q
                ) < std::tuple(
                    components[best_root].balance, root_values[best_root], best
                );
            }
            if (take) best = q;
        }
        return best;
    }

    void assign_hole(
        std::uint32_t node,
        const std::vector<std::uint32_t>& candidates,
        const std::vector<std::uint32_t>& root_values
    ) {
        root_of[node] = root_of[choose(candidates, root_values)];
    }

    void add_healed(std::uint32_t parent, std::uint16_t rank) {
        if (rank >= kRankCount) throw std::runtime_error("rank overflow");
        const std::uint32_t root_id = root_of[parent];
        if (root_id == kUnsetRoot) {
            throw std::runtime_error("healed parent has no splitless root");
        }
        Component& component = components[root_id];
        --component.net_exact[rank];
        ++component.healed_exact[rank];
        --component.balance;
    }

    void add_hard(
        std::uint32_t source,
        std::uint16_t rank,
        const std::vector<std::uint32_t>& root_values
    ) {
        if (rank >= kRankCount) throw std::runtime_error("rank overflow");
        const std::uint32_t root_id = root_of[source];
        if (root_id == kUnsetRoot) {
            throw std::runtime_error("hard source has no splitless root");
        }
        Component& component = components[root_id];
        ++component.net_exact[rank];
        ++component.balance;
        const std::uint32_t root_value = root_values[root_id];
        unranked.observe(
            source, kNoRank, root_value, 0, 0, component.balance
        );

        std::array<std::uint64_t, kRankCount> healed_prefix{};
        std::uint64_t healed_running = 0;
        for (std::size_t d = 0; d < kRankCount; ++d) {
            healed_running += component.healed_exact[d];
            healed_prefix[d] = healed_running;
        }

        std::int64_t net_running = 0;
        healed_running = 0;
        for (std::size_t d = 0; d < kRankCount; ++d) {
            net_running += component.net_exact[d];
            healed_running += component.healed_exact[d];
            const std::uint64_t hard_running = static_cast<std::uint64_t>(
                static_cast<std::int64_t>(healed_running) + net_running
            );
            for (std::size_t offset = 0; offset <= 2; ++offset) {
                const std::size_t target_rank = std::min(
                    d + offset, kRankCount - 1
                );
                const std::uint64_t healed = healed_prefix[target_rank];
                const std::int64_t deficit =
                    static_cast<std::int64_t>(hard_running) -
                    static_cast<std::int64_t>(healed);
                rank_offset[offset].observe(
                    source,
                    static_cast<std::uint16_t>(d),
                    root_value,
                    hard_running,
                    healed,
                    deficit
                );
            }
        }
    }
};

struct Snapshot {
    std::uint32_t x = 0;
    std::uint64_t hard = 0;
    std::uint64_t healed = 0;
    std::uint64_t splitless = 0;
    std::int64_t hard_minus_healed_splitless = 0;
    std::int64_t hard_minus_splitless = 0;
    std::int64_t leaf_6_required_capacity = 0;
    std::vector<std::array<std::int64_t, 4>> policy_maxima;
};

void write_policy(
    std::ostream& out,
    const Policy& policy,
    std::uint64_t root_count
) {
    out << "{\"name\":\"" << policy.name << "\""
        << ",\"component_count\":" << root_count
        << ",\"unranked_bank_capacity\":";
    write_audit(out, policy.unranked);
    out << ",\"rank_filtered_bank_capacity\":{\"offset_0\":";
    write_audit(out, policy.rank_offset[0]);
    out << ",\"offset_1\":";
    write_audit(out, policy.rank_offset[1]);
    out << ",\"offset_2\":";
    write_audit(out, policy.rank_offset[2]);
    out << "}}";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: splitless_bank LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 100 || parsed_limit > 2000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [100, 2000000000]");
    }
    const std::uint32_t limit = static_cast<std::uint32_t>(parsed_limit);

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
        static_cast<std::size_t>(limit) + 1, kUnsetRank
    );
    std::vector<std::uint8_t> shadow_contains_6(
        static_cast<std::size_t>(limit) + 1, 0
    );
    std::vector<std::uint8_t> shadow_only_6(
        static_cast<std::size_t>(limit) + 1, 0
    );
    member[2] = member[3] = 1;

    const std::size_t expected_roots = static_cast<std::size_t>(limit / 8) + 16;
    std::vector<Policy> policies;
    policies.reserve(3);
    policies.emplace_back(
        "minimum_critical_endpoint", RootRule::min_endpoint,
        static_cast<std::size_t>(limit) + 1, expected_roots
    );
    policies.emplace_back(
        "minimum_critical_root", RootRule::min_root,
        static_cast<std::size_t>(limit) + 1, expected_roots
    );
    policies.emplace_back(
        "minimum_current_component_balance", RootRule::minimum_balance,
        static_cast<std::size_t>(limit) + 1, expected_roots
    );

    std::vector<std::uint32_t> root_values;
    root_values.reserve(expected_roots);
    std::array<std::uint64_t, kRankCount> hard_exact{};
    std::array<std::uint64_t, kRankCount> healed_exact{};
    std::uint64_t hard_total = 0;
    std::uint64_t healed_total = 0;
    std::uint64_t splitless_total = 0;
    std::uint64_t generated_total = 2;
    std::uint64_t hole_total = 0;
    std::uint16_t maximum_rank = 0;

    Audit scalar_h_minus_q;
    Audit scalar_h_minus_e;
    Audit scalar_h_minus_q_minus_e;
    Audit rank_h_minus_q;
    Audit rank_h_minus_q_minus_e;
    std::array<Audit, 3> global_rank_offset;
    Audit exact_layer_h_minus_q_minus_e;
    Audit singleton_leaf_6;
    std::uint64_t hard_only_leaf_6 = 0;
    std::uint64_t healed_containing_leaf_6 = 0;

    std::vector<Snapshot> snapshots;
    std::uint64_t next_checkpoint = 100;
    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);
    std::vector<std::uint32_t> candidates;
    candidates.reserve(64);
    std::vector<std::uint32_t> missing_endpoints;
    missing_endpoints.reserve(128);

    for (std::uint32_t n = 4; n <= limit; ++n) {
        if (!allowed(n)) {
            if (n == next_checkpoint) {
                Snapshot row;
                row.x = n;
                row.hard = hard_total;
                row.healed = healed_total;
                row.splitless = splitless_total;
                row.hard_minus_healed_splitless =
                    static_cast<std::int64_t>(hard_total) -
                    static_cast<std::int64_t>(healed_total + splitless_total);
                row.hard_minus_splitless =
                    static_cast<std::int64_t>(hard_total) -
                    static_cast<std::int64_t>(splitless_total);
                row.leaf_6_required_capacity =
                    singleton_leaf_6.maximum_deficit;
                for (const Policy& policy : policies) {
                    row.policy_maxima.push_back({
                        policy.unranked.maximum_deficit,
                        policy.rank_offset[0].maximum_deficit,
                        policy.rank_offset[1].maximum_deficit,
                        policy.rank_offset[2].maximum_deficit,
                    });
                }
                snapshots.push_back(std::move(row));
                next_checkpoint *= 10;
            }
            continue;
        }

        bool has_pair = false;
        bool generated = false;
        std::uint16_t blocking_rank = 0;
        candidates.clear();
        missing_endpoints.clear();

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
            has_pair = true;
            if (member[a] && member[b]) {
                generated = true;
                continue;
            }
            std::uint16_t pair_block = kUnsetRank;
            if (!member[a]) pair_block = rank[a];
            if (!member[b]) pair_block = std::min(pair_block, rank[b]);
            if (!member[a]) missing_endpoints.push_back(a);
            if (!member[b]) missing_endpoints.push_back(b);
            if (pair_block == kUnsetRank) {
                throw std::runtime_error("blocked pair has no missing endpoint");
            }
            if (pair_block > blocking_rank) {
                blocking_rank = pair_block;
                candidates.clear();
            }
            if (pair_block == blocking_rank) {
                if (!member[a] && rank[a] == pair_block) candidates.push_back(a);
                if (!member[b] && rank[b] == pair_block) candidates.push_back(b);
            }
        }

        if (generated) {
            member[n] = 1;
            ++generated_total;
            if ((n & 1U) != 0) {
                const std::uint32_t parent = (n + 1) / 2;
                if (!member[parent]) {
                    const std::uint16_t parent_rank = rank[parent];
                    if (parent_rank >= kRankCount) {
                        throw std::runtime_error("healed rank overflow");
                    }
                    ++healed_total;
                    ++healed_exact[parent_rank];
                    if (shadow_contains_6[parent]) {
                        ++healed_containing_leaf_6;
                    }
                    for (Policy& policy : policies) {
                        policy.add_healed(parent, parent_rank);
                    }
                }
            }
        } else {
            ++hole_total;
            if (!has_pair) {
                rank[n] = 0;
                const std::uint32_t root_id =
                    static_cast<std::uint32_t>(root_values.size());
                root_values.push_back(n);
                for (Policy& policy : policies) policy.add_root(n, root_id);
                if (n == 6) {
                    shadow_contains_6[n] = 1;
                    shadow_only_6[n] = 1;
                }
                ++splitless_total;
            } else {
                rank[n] = static_cast<std::uint16_t>(blocking_rank + 1);
                if (rank[n] >= kRankCount) {
                    throw std::runtime_error("obstruction rank overflow");
                }
                for (Policy& policy : policies) {
                    policy.assign_hole(n, candidates, root_values);
                }
                bool found_lower = false;
                bool contains_6 = false;
                bool only_6 = true;
                for (const std::uint32_t q : missing_endpoints) {
                    if (rank[q] >= rank[n]) continue;
                    found_lower = true;
                    contains_6 = contains_6 || shadow_contains_6[q];
                    only_6 = only_6 && shadow_only_6[q];
                }
                if (!found_lower) {
                    throw std::runtime_error("hole has no lower-rank endpoint");
                }
                shadow_contains_6[n] = static_cast<std::uint8_t>(contains_6);
                shadow_only_6[n] = static_cast<std::uint8_t>(only_6);
            }
            maximum_rank = std::max(maximum_rank, rank[n]);

            if (hard_shape(n, has_pair)) {
                const std::uint16_t source_rank = rank[n];
                ++hard_total;
                ++hard_exact[source_rank];
                if (shadow_only_6[n]) {
                    ++hard_only_leaf_6;
                    singleton_leaf_6.observe(
                        n, kNoRank, 6,
                        hard_only_leaf_6, healed_containing_leaf_6,
                        static_cast<std::int64_t>(hard_only_leaf_6) -
                            static_cast<std::int64_t>(healed_containing_leaf_6)
                    );
                }
                for (Policy& policy : policies) {
                    policy.add_hard(n, source_rank, root_values);
                }

                scalar_h_minus_q.observe(
                    n, kNoRank, 0, hard_total, healed_total,
                    static_cast<std::int64_t>(hard_total) -
                        static_cast<std::int64_t>(healed_total)
                );
                scalar_h_minus_e.observe(
                    n, kNoRank, 0, hard_total, splitless_total,
                    static_cast<std::int64_t>(hard_total) -
                        static_cast<std::int64_t>(splitless_total)
                );
                scalar_h_minus_q_minus_e.observe(
                    n, kNoRank, 0, hard_total, healed_total + splitless_total,
                    static_cast<std::int64_t>(hard_total) -
                        static_cast<std::int64_t>(healed_total + splitless_total)
                );

                std::array<std::uint64_t, kRankCount> healed_prefix{};
                std::uint64_t q_running = 0;
                for (std::size_t d = 0; d < kRankCount; ++d) {
                    q_running += healed_exact[d];
                    healed_prefix[d] = q_running;
                }
                std::uint64_t h_running = 0;
                q_running = 0;
                for (std::size_t d = 0; d < kRankCount; ++d) {
                    h_running += hard_exact[d];
                    q_running += healed_exact[d];
                    const std::int64_t strict_deficit =
                        static_cast<std::int64_t>(h_running) -
                        static_cast<std::int64_t>(q_running);
                    rank_h_minus_q.observe(
                        n, static_cast<std::uint16_t>(d), 0,
                        h_running, q_running, strict_deficit
                    );
                    rank_h_minus_q_minus_e.observe(
                        n, static_cast<std::uint16_t>(d), 0,
                        h_running, q_running + splitless_total,
                        strict_deficit - static_cast<std::int64_t>(splitless_total)
                    );
                    for (std::size_t offset = 0; offset <= 2; ++offset) {
                        const std::size_t target_rank = std::min(
                            d + offset, kRankCount - 1
                        );
                        const std::uint64_t q_allowed = healed_prefix[target_rank];
                        global_rank_offset[offset].observe(
                            n, static_cast<std::uint16_t>(d), 0,
                            h_running, q_allowed,
                            static_cast<std::int64_t>(h_running) -
                                static_cast<std::int64_t>(q_allowed)
                        );
                    }
                }
                exact_layer_h_minus_q_minus_e.observe(
                    n, source_rank, 0,
                    hard_exact[source_rank],
                    healed_exact[source_rank] + splitless_total,
                    static_cast<std::int64_t>(hard_exact[source_rank]) -
                        static_cast<std::int64_t>(
                            healed_exact[source_rank] + splitless_total
                        )
                );
            }
        }

        if (n == next_checkpoint) {
            Snapshot row;
            row.x = n;
            row.hard = hard_total;
            row.healed = healed_total;
            row.splitless = splitless_total;
            row.hard_minus_healed_splitless =
                static_cast<std::int64_t>(hard_total) -
                static_cast<std::int64_t>(healed_total + splitless_total);
            row.hard_minus_splitless =
                static_cast<std::int64_t>(hard_total) -
                static_cast<std::int64_t>(splitless_total);
            row.leaf_6_required_capacity =
                singleton_leaf_6.maximum_deficit;
            for (const Policy& policy : policies) {
                row.policy_maxima.push_back({
                    policy.unranked.maximum_deficit,
                    policy.rank_offset[0].maximum_deficit,
                    policy.rank_offset[1].maximum_deficit,
                    policy.rank_offset[2].maximum_deficit,
                });
            }
            snapshots.push_back(std::move(row));
            next_checkpoint *= 10;
        }
    }

    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n  \"schema_version\":1,\n"
        << "  \"limit\":" << limit << ",\n"
        << "  \"rank_definition\":\"splitless=0; reducible=1+max_pairs min_missing_rank\",\n"
        << "  \"forest_definition\":\"each reducible hole chooses a missing endpoint of rank exactly one lower\",\n"
        << "  \"allowed\":" << (2ULL * limit / 3) << ",\n"
        << "  \"generated\":" << generated_total << ",\n"
        << "  \"holes\":" << hole_total << ",\n"
        << "  \"splitless\":" << splitless_total << ",\n"
        << "  \"hard\":" << hard_total << ",\n"
        << "  \"healed\":" << healed_total << ",\n"
        << "  \"maximum_obstruction_rank\":" << maximum_rank << ",\n"
        << "  \"scalar\":{\n"
        << "    \"H_minus_Q\":";
    write_audit(out, scalar_h_minus_q);
    out << ",\n    \"H_minus_E\":";
    write_audit(out, scalar_h_minus_e);
    out << ",\n    \"H_minus_Q_minus_E\":";
    write_audit(out, scalar_h_minus_q_minus_e);
    out << "\n  },\n  \"global_rank_filtered\":{\n"
        << "    \"same_rank_H_minus_Q\":";
    write_audit(out, rank_h_minus_q);
    out << ",\n    \"same_rank_H_minus_Q_minus_E\":";
    write_audit(out, rank_h_minus_q_minus_e);
    out << ",\n    \"offset_0\":";
    write_audit(out, global_rank_offset[0]);
    out << ",\n    \"offset_1\":";
    write_audit(out, global_rank_offset[1]);
    out << ",\n    \"offset_2\":";
    write_audit(out, global_rank_offset[2]);
    out << ",\n    \"exact_layer_H_minus_Q_minus_E\":";
    write_audit(out, exact_layer_h_minus_q_minus_e);
    out << "\n  },\n  \"singleton_leaf_6_gate\":{\n"
        << "    \"source_rule\":\"all lower-rank obstruction leaves equal 6\",\n"
        << "    \"target_rule\":\"healed parent shadow contains 6, plus C copies of E=6\",\n"
        << "    \"hard_sources\":" << hard_only_leaf_6 << ",\n"
        << "    \"healed_targets\":" << healed_containing_leaf_6 << ",\n"
        << "    \"required_bank_capacity\":";
    write_audit(out, singleton_leaf_6);
    out << "\n  },\n  \"component_policies\":[\n";
    for (std::size_t i = 0; i < policies.size(); ++i) {
        out << "    ";
        write_policy(out, policies[i], root_values.size());
        out << (i + 1 == policies.size() ? "\n" : ",\n");
    }
    out << "  ],\n  \"snapshots\":[\n";
    for (std::size_t i = 0; i < snapshots.size(); ++i) {
        const Snapshot& row = snapshots[i];
        out << "    {\"X\":" << row.x
            << ",\"H\":" << row.hard
            << ",\"Q\":" << row.healed
            << ",\"E\":" << row.splitless
            << ",\"H-Q-E\":" << row.hard_minus_healed_splitless
            << ",\"H-E\":" << row.hard_minus_splitless
            << ",\"leaf_6_required_capacity\":"
            << row.leaf_6_required_capacity
            << ",\"policy_maxima\":[";
        for (std::size_t p = 0; p < row.policy_maxima.size(); ++p) {
            const auto& values = row.policy_maxima[p];
            out << "{\"name\":\"" << policies[p].name << "\""
                << ",\"unranked\":" << values[0]
                << ",\"rank_offset_0\":" << values[1]
                << ",\"rank_offset_1\":" << values[2]
                << ",\"rank_offset_2\":" << values[3] << "}"
                << (p + 1 == row.policy_maxima.size() ? "" : ",");
        }
        out << "]}" << (i + 1 == snapshots.size() ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit
              << " G=" << generated_total
              << " holes=" << hole_total
              << " E=" << splitless_total
              << " H=" << hard_total
              << " Q=" << healed_total
              << " max_rank=" << maximum_rank;
    for (const Policy& policy : policies) {
        std::cout << " " << policy.name
                  << "=(" << policy.unranked.maximum_deficit
                  << "," << policy.rank_offset[0].maximum_deficit
                  << "," << policy.rank_offset[1].maximum_deficit
                  << "," << policy.rank_offset[2].maximum_deficit << ")";
    }
    std::cout << '\n';
    return 0;
}
