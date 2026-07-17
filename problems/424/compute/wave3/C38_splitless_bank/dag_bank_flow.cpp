#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr std::uint16_t kUnsetRank =
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

struct Edge {
    std::uint32_t to;
    std::uint32_t reverse;
    std::int32_t capacity;
    std::int32_t original;
};

enum class NodeKind : std::uint8_t {
    special,
    root,
    source,
    target,
};

class ResidualNetwork {
public:
    ResidualNetwork() {
        add_node(NodeKind::special, 0);
        add_node(NodeKind::special, 0);
    }

    std::uint32_t add_node(NodeKind kind, std::uint32_t value) {
        graph_.emplace_back();
        kind_.push_back(kind);
        value_.push_back(value);
        seen_stamp_.push_back(0);
        parent_node_.push_back(kNoNode);
        parent_edge_.push_back(kNoNode);
        return static_cast<std::uint32_t>(graph_.size() - 1);
    }

    void add_edge(std::uint32_t from, std::uint32_t to, std::int32_t capacity) {
        if (capacity < 0) throw std::runtime_error("negative capacity");
        const auto forward_reverse = static_cast<std::uint32_t>(graph_[to].size());
        const auto reverse_reverse = static_cast<std::uint32_t>(graph_[from].size());
        graph_[from].push_back(Edge{to, forward_reverse, capacity, capacity});
        graph_[to].push_back(Edge{from, reverse_reverse, 0, 0});
    }

    bool augment_one(std::uint32_t source, std::uint32_t sink) {
        ++current_stamp_;
        if (current_stamp_ == 0) {
            std::fill(seen_stamp_.begin(), seen_stamp_.end(), 0);
            current_stamp_ = 1;
        }
        std::queue<std::uint32_t> queue;
        seen_stamp_[source] = current_stamp_;
        parent_node_[source] = source;
        queue.push(source);
        while (!queue.empty() && seen_stamp_[sink] != current_stamp_) {
            const std::uint32_t node = queue.front();
            queue.pop();
            for (std::uint32_t edge_id = 0; edge_id < graph_[node].size(); ++edge_id) {
                const Edge& edge = graph_[node][edge_id];
                if (edge.capacity == 0 || seen_stamp_[edge.to] == current_stamp_) {
                    continue;
                }
                seen_stamp_[edge.to] = current_stamp_;
                parent_node_[edge.to] = node;
                parent_edge_[edge.to] = edge_id;
                queue.push(edge.to);
                if (edge.to == sink) break;
            }
        }
        if (seen_stamp_[sink] != current_stamp_) return false;

        for (std::uint32_t node = sink; node != source; node = parent_node_[node]) {
            const std::uint32_t previous = parent_node_[node];
            Edge& edge = graph_[previous][parent_edge_[node]];
            --edge.capacity;
            ++graph_[node][edge.reverse].capacity;
        }
        return true;
    }

    std::uint64_t cut_capacity() const {
        if (current_stamp_ == 0) {
            throw std::runtime_error("cut requested before failed search");
        }
        std::uint64_t total = 0;
        for (std::uint32_t from = 0; from < graph_.size(); ++from) {
            if (seen_stamp_[from] != current_stamp_) continue;
            for (const Edge& edge : graph_[from]) {
                if (seen_stamp_[edge.to] != current_stamp_) total += edge.original;
            }
        }
        return total;
    }

    std::uint64_t reachable_count(NodeKind kind) const {
        std::uint64_t count = 0;
        for (std::size_t node = 0; node < graph_.size(); ++node) {
            if (seen_stamp_[node] == current_stamp_ && kind_[node] == kind) ++count;
        }
        return count;
    }

    std::vector<std::uint32_t> reachable_values(
        NodeKind kind,
        std::size_t maximum
    ) const {
        std::vector<std::uint32_t> values;
        for (std::size_t node = 0; node < graph_.size(); ++node) {
            if (seen_stamp_[node] != current_stamp_ || kind_[node] != kind) continue;
            values.push_back(value_[node]);
            if (values.size() == maximum) break;
        }
        return values;
    }

    std::size_t node_count() const { return graph_.size(); }

    std::uint64_t directed_edge_count() const {
        std::uint64_t count = 0;
        for (const auto& row : graph_) count += row.size();
        return count;
    }

private:
    static constexpr std::uint32_t kNoNode =
        std::numeric_limits<std::uint32_t>::max();

    std::vector<std::vector<Edge>> graph_;
    std::vector<NodeKind> kind_;
    std::vector<std::uint32_t> value_;
    std::vector<std::uint32_t> seen_stamp_;
    std::vector<std::uint32_t> parent_node_;
    std::vector<std::uint32_t> parent_edge_;
    std::uint32_t current_stamp_ = 0;
};

void write_values(std::ostream& out, const std::vector<std::uint32_t>& values) {
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        out << values[i] << (i + 1 == values.size() ? "" : ",");
    }
    out << ']';
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "usage: dag_bank_flow LIMIT BANK_CAPACITY OUTPUT_JSON\n";
        return 2;
    }
    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    const std::uint64_t parsed_capacity = std::stoull(argv[2]);
    if (parsed_limit < 100 || parsed_limit > 100000000ULL) {
        throw std::runtime_error("LIMIT must lie in [100,100000000]");
    }
    if (parsed_capacity < 1 || parsed_capacity > 1000000ULL) {
        throw std::runtime_error("BANK_CAPACITY must lie in [1,1000000]");
    }
    const auto limit = static_cast<std::uint32_t>(parsed_limit);
    const auto bank_capacity = static_cast<std::int32_t>(parsed_capacity);

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
    std::vector<std::uint16_t> rank(
        static_cast<std::size_t>(limit) + 1, kUnsetRank
    );
    std::vector<std::vector<std::uint32_t>> shadow(
        static_cast<std::size_t>(limit) + 1
    );
    member[2] = member[3] = 1;

    ResidualNetwork flow;
    constexpr std::uint32_t super_source = 0;
    constexpr std::uint32_t sink = 1;
    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);
    std::vector<std::uint32_t> missing_endpoints;
    missing_endpoints.reserve(128);
    std::vector<std::uint32_t> merged_shadow;
    merged_shadow.reserve(256);

    std::uint64_t generated = 2;
    std::uint64_t holes = 0;
    std::uint64_t splitless = 0;
    std::uint64_t hard = 0;
    std::uint64_t healed = 0;
    std::uint64_t matched = 0;
    std::uint16_t maximum_rank = 0;
    std::size_t maximum_shadow_size = 0;
    std::uint32_t failure_x = 0;
    std::uint16_t failure_rank = 0;

    for (std::uint32_t n = 4; n <= limit; ++n) {
        if (!allowed(n)) continue;
        bool has_pair = false;
        bool is_generated = false;
        std::uint16_t blocking_rank = 0;
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
                is_generated = true;
                continue;
            }
            std::uint16_t pair_block = kUnsetRank;
            if (!member[a]) {
                pair_block = rank[a];
                missing_endpoints.push_back(a);
            }
            if (!member[b]) {
                pair_block = std::min(pair_block, rank[b]);
                missing_endpoints.push_back(b);
            }
            if (pair_block == kUnsetRank) {
                throw std::runtime_error("blocked pair has no missing endpoint");
            }
            blocking_rank = std::max(blocking_rank, pair_block);
        }

        if (is_generated) {
            member[n] = 1;
            ++generated;
            if ((n & 1U) != 0) {
                const std::uint32_t parent = (n + 1) / 2;
                if (!member[parent]) {
                    const std::uint32_t target = flow.add_node(NodeKind::target, n);
                    for (const std::uint32_t root : shadow[parent]) {
                        flow.add_edge(root, target, 1);
                    }
                    flow.add_edge(target, sink, 1);
                    ++healed;
                }
            }
            continue;
        }

        ++holes;
        if (!has_pair) {
            rank[n] = 0;
            const std::uint32_t root = flow.add_node(NodeKind::root, n);
            shadow[n].push_back(root);
            flow.add_edge(root, sink, bank_capacity);
            ++splitless;
        } else {
            rank[n] = static_cast<std::uint16_t>(blocking_rank + 1);
            merged_shadow.clear();
            for (const std::uint32_t q : missing_endpoints) {
                if (rank[q] >= rank[n]) continue;
                merged_shadow.insert(
                    merged_shadow.end(), shadow[q].begin(), shadow[q].end()
                );
            }
            if (merged_shadow.empty()) {
                throw std::runtime_error("hole has no lower-rank shadow");
            }
            std::sort(merged_shadow.begin(), merged_shadow.end());
            merged_shadow.erase(
                std::unique(merged_shadow.begin(), merged_shadow.end()),
                merged_shadow.end()
            );
            shadow[n] = merged_shadow;
        }
        maximum_rank = std::max(maximum_rank, rank[n]);
        maximum_shadow_size = std::max(maximum_shadow_size, shadow[n].size());

        if (!hard_shape(n, has_pair)) continue;
        ++hard;
        const std::uint32_t source = flow.add_node(NodeKind::source, n);
        flow.add_edge(super_source, source, 1);
        for (const std::uint32_t root : shadow[n]) {
            flow.add_edge(source, root, 1);
        }
        if (!flow.augment_one(super_source, sink)) {
            failure_x = n;
            failure_rank = rank[n];
            break;
        }
        ++matched;
    }

    const bool passed = failure_x == 0;
    std::uint64_t cut_capacity = 0;
    std::uint64_t reachable_sources = 0;
    std::uint64_t reachable_roots = 0;
    std::uint64_t reachable_targets = 0;
    std::vector<std::uint32_t> source_prefix;
    std::vector<std::uint32_t> root_prefix;
    std::vector<std::uint32_t> target_prefix;
    if (!passed) {
        cut_capacity = flow.cut_capacity();
        if (cut_capacity != matched) {
            throw std::runtime_error("max-flow/min-cut mismatch");
        }
        reachable_sources = flow.reachable_count(NodeKind::source);
        reachable_roots = flow.reachable_count(NodeKind::root);
        reachable_targets = flow.reachable_count(NodeKind::target);
        source_prefix = flow.reachable_values(NodeKind::source, 100);
        root_prefix = flow.reachable_values(NodeKind::root, 100);
        target_prefix = flow.reachable_values(NodeKind::target, 100);
    }

    std::ofstream out(argv[3]);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n"
        << "  \"schema_version\":1,\n"
        << "  \"limit\":" << limit << ",\n"
        << "  \"bank_capacity\":" << bank_capacity << ",\n"
        << "  \"relation\":\"source/target shadows intersect in a splitless leaf; shadows follow every lower-rank missing endpoint\",\n"
        << "  \"passed\":" << (passed ? "true" : "false") << ",\n"
        << "  \"processed_X\":" << (passed ? limit : failure_x) << ",\n"
        << "  \"generated\":" << generated << ",\n"
        << "  \"holes\":" << holes << ",\n"
        << "  \"splitless\":" << splitless << ",\n"
        << "  \"hard\":" << hard << ",\n"
        << "  \"healed\":" << healed << ",\n"
        << "  \"matched\":" << matched << ",\n"
        << "  \"maximum_rank\":" << maximum_rank << ",\n"
        << "  \"maximum_shadow_size\":" << maximum_shadow_size << ",\n"
        << "  \"network_nodes\":" << flow.node_count() << ",\n"
        << "  \"network_directed_edges\":" << flow.directed_edge_count() << ",\n"
        << "  \"failure\":";
    if (passed) {
        out << "null\n";
    } else {
        out << "{\"X\":" << failure_x
            << ",\"rank\":" << failure_rank
            << ",\"flow_value\":" << matched
            << ",\"min_cut_capacity\":" << cut_capacity
            << ",\"flow_deficit\":" << (hard - matched)
            << ",\"reachable_sources\":" << reachable_sources
            << ",\"reachable_roots\":" << reachable_roots
            << ",\"reachable_targets\":" << reachable_targets
            << ",\"source_prefix\":";
        write_values(out, source_prefix);
        out << ",\"root_prefix\":";
        write_values(out, root_prefix);
        out << ",\"target_prefix\":";
        write_values(out, target_prefix);
        out << "}\n";
    }
    out << "}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit
              << " C=" << bank_capacity
              << " passed=" << passed
              << " processed_X=" << (passed ? limit : failure_x)
              << " H=" << hard
              << " Q=" << healed
              << " E=" << splitless
              << " matched=" << matched
              << " max_shadow=" << maximum_shadow_size << '\n';
    return 0;
}
