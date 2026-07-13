#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

bool is_allowed(std::uint32_t value) {
    return value >= 2 && value % 3 != 1;
}

class HopcroftKarp {
public:
    HopcroftKarp(
        const std::vector<std::uint64_t>& offsets,
        const std::vector<std::uint32_t>& neighbors,
        std::uint32_t right_limit
    )
        : offsets_(offsets),
          neighbors_(neighbors),
          pair_left_(offsets.size() - 1, 0),
          pair_right_(static_cast<std::size_t>(right_limit) + 1, 0),
          distance_(offsets.size() - 1, -1),
          next_edge_(offsets.size() - 1, 0) {}

    std::uint64_t solve() {
        std::uint64_t matching = 0;
        while (bfs()) {
            for (std::uint32_t left = 0; left < pair_left_.size(); ++left) {
                if (pair_left_[left] == 0 && dfs(left)) ++matching;
            }
        }
        return matching;
    }

    const std::vector<std::uint32_t>& pair_left() const { return pair_left_; }
    const std::vector<std::uint32_t>& pair_right() const { return pair_right_; }

private:
    bool bfs() {
        std::queue<std::uint32_t> queue;
        bool found = false;
        for (std::uint32_t left = 0; left < pair_left_.size(); ++left) {
            if (pair_left_[left] == 0) {
                distance_[left] = 0;
                queue.push(left);
            } else {
                distance_[left] = -1;
            }
            next_edge_[left] = offsets_[left];
        }

        while (!queue.empty()) {
            const std::uint32_t left = queue.front();
            queue.pop();
            for (std::uint64_t edge = offsets_[left]; edge < offsets_[left + 1]; ++edge) {
                const std::uint32_t right = neighbors_[edge];
                const std::uint32_t mate_code = pair_right_[right];
                if (mate_code == 0) {
                    found = true;
                } else {
                    const std::uint32_t mate = mate_code - 1;
                    if (distance_[mate] < 0) {
                        distance_[mate] = distance_[left] + 1;
                        queue.push(mate);
                    }
                }
            }
        }
        return found;
    }

    bool dfs(std::uint32_t left) {
        for (std::uint64_t& edge = next_edge_[left]; edge < offsets_[left + 1]; ++edge) {
            const std::uint32_t right = neighbors_[edge];
            const std::uint32_t mate_code = pair_right_[right];
            if (mate_code == 0) {
                pair_left_[left] = right;
                pair_right_[right] = left + 1;
                ++edge;
                return true;
            }
            const std::uint32_t mate = mate_code - 1;
            if (distance_[mate] == distance_[left] + 1 && dfs(mate)) {
                pair_left_[left] = right;
                pair_right_[right] = left + 1;
                ++edge;
                return true;
            }
        }
        distance_[left] = -1;
        return false;
    }

    const std::vector<std::uint64_t>& offsets_;
    const std::vector<std::uint32_t>& neighbors_;
    std::vector<std::uint32_t> pair_left_;
    std::vector<std::uint32_t> pair_right_;
    std::vector<std::int32_t> distance_;
    std::vector<std::uint64_t> next_edge_;
};

bool has_neighbor(
    std::uint32_t left,
    std::uint32_t right,
    const std::vector<std::uint64_t>& offsets,
    const std::vector<std::uint32_t>& neighbors
) {
    for (std::uint64_t edge = offsets[left]; edge < offsets[left + 1]; ++edge) {
        if (neighbors[edge] == right) return true;
    }
    return false;
}

std::uint64_t fnv_mix(std::uint64_t hash, std::uint64_t value) {
    for (unsigned byte = 0; byte < 8; ++byte) {
        hash ^= (value >> (8 * byte)) & 0xffU;
        hash *= 1099511628211ULL;
    }
    return hash;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: hall_audit LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const std::uint64_t parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 32 || parsed_limit > 1000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [32, 1000000000]");
    }
    const std::uint32_t limit = static_cast<std::uint32_t>(parsed_limit);
    const auto started = std::chrono::steady_clock::now();

    std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 2);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t prime = 2;
         static_cast<std::uint64_t>(prime) * prime <=
             static_cast<std::uint64_t>(limit) + 1;
         ++prime) {
        if (spf[prime] != prime) continue;
        for (std::uint64_t multiple = static_cast<std::uint64_t>(prime) * prime;
             multiple <= static_cast<std::uint64_t>(limit) + 1;
             multiple += prime) {
            if (spf[multiple] == multiple) spf[multiple] = prime;
        }
    }

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1, 0);
    member[2] = 1;
    member[3] = 1;

    std::vector<std::uint64_t> offsets{0};
    std::vector<std::uint32_t> neighbors;
    std::vector<std::uint32_t> outputs;
    std::vector<std::uint8_t> output_types;
    offsets.reserve(static_cast<std::size_t>(limit / 16) + 1);
    outputs.reserve(static_cast<std::size_t>(limit / 16));
    output_types.reserve(static_cast<std::size_t>(limit / 16));
    neighbors.reserve(static_cast<std::size_t>(limit / 8));

    std::uint64_t odd_count = 0;
    std::uint64_t hard_count = 0;
    std::uint64_t seed3_count = 0;
    std::uint64_t splitless_count = 0;
    std::uint64_t maximum_degree = 0;

    std::vector<std::uint32_t> divisors;
    std::vector<std::pair<std::uint32_t, std::uint32_t>> pairs;
    divisors.reserve(2048);
    pairs.reserve(1024);

    for (std::uint32_t n = 2; n <= limit; ++n) {
        pairs.clear();
        if (n >= 4) {
            const std::uint32_t product = n + 1;
            std::uint32_t remaining = product;
            divisors.clear();
            divisors.push_back(1);
            while (remaining > 1) {
                const std::uint32_t prime = spf[remaining];
                const std::size_t old_size = divisors.size();
                std::uint32_t power = 1;
                do {
                    remaining /= prime;
                    power *= prime;
                    for (std::size_t index = 0; index < old_size; ++index) {
                        divisors.push_back(divisors[index] * power);
                    }
                } while (remaining > 1 && spf[remaining] == prime);
            }

            for (const std::uint32_t left : divisors) {
                if (left < 2) continue;
                const std::uint32_t right = product / left;
                if (left >= right) continue;
                if (!is_allowed(left) || !is_allowed(right)) continue;
                pairs.emplace_back(left, right);
                if (!member[n] && member[left] && member[right]) member[n] = 1;
            }
        }

        if (!is_allowed(n) || member[n]) continue;
        if (pairs.empty()) {
            ++splitless_count;
            continue;
        }

        if ((n & 1U) != 0) {
            const std::uint32_t parent = (n + 1) / 2;
            if (member[parent] || !is_allowed(parent)) {
                throw std::runtime_error("forced seed-2 parent assertion failed");
            }
            neighbors.push_back(parent);
            outputs.push_back(n);
            output_types.push_back(0);
            offsets.push_back(neighbors.size());
            ++odd_count;
        } else if ((n + 1) % 3 == 0 &&
                   is_allowed((n + 1) / 3) && (n + 1) / 3 != 3) {
            const std::uint32_t parent = (n + 1) / 3;
            if (member[parent]) {
                throw std::runtime_error("forced seed-3 parent assertion failed");
            }
            ++seed3_count;
        } else {
            const std::size_t begin = neighbors.size();
            for (const auto& [left, right] : pairs) {
                if (!member[left]) neighbors.push_back(left);
                if (!member[right]) neighbors.push_back(right);
            }
            if (neighbors.size() == begin) {
                throw std::runtime_error("hard output has no missing factor");
            }
            maximum_degree = std::max<std::uint64_t>(
                maximum_degree,
                neighbors.size() - begin
            );
            outputs.push_back(n);
            output_types.push_back(1);
            offsets.push_back(neighbors.size());
            ++hard_count;
        }
    }

    const std::uint32_t right_limit = (limit + 1) / 2;
    HopcroftKarp matcher(offsets, neighbors, right_limit);
    const std::uint64_t matching = matcher.solve();
    const auto& pair_left = matcher.pair_left();
    const auto& pair_right = matcher.pair_right();

    std::vector<std::uint8_t> seen_right(pair_right.size(), 0);
    std::uint64_t matching_hash = 1469598103934665603ULL;
    for (std::uint32_t left = 0; left < pair_left.size(); ++left) {
        const std::uint32_t right = pair_left[left];
        if (right == 0) continue;
        if (right > right_limit || seen_right[right] ||
            !has_neighbor(left, right, offsets, neighbors)) {
            throw std::runtime_error("invalid matching certificate");
        }
        seen_right[right] = 1;
        matching_hash = fnv_mix(matching_hash, outputs[left]);
        matching_hash = fnv_mix(matching_hash, right);
    }

    std::vector<std::uint8_t> reachable_left(pair_left.size(), 0);
    std::vector<std::uint8_t> reachable_right(pair_right.size(), 0);
    std::queue<std::uint32_t> queue;
    for (std::uint32_t left = 0; left < pair_left.size(); ++left) {
        if (pair_left[left] == 0) {
            reachable_left[left] = 1;
            queue.push(left);
        }
    }
    while (!queue.empty()) {
        const std::uint32_t left = queue.front();
        queue.pop();
        for (std::uint64_t edge = offsets[left]; edge < offsets[left + 1]; ++edge) {
            const std::uint32_t right = neighbors[edge];
            if (pair_left[left] == right || reachable_right[right]) continue;
            reachable_right[right] = 1;
            const std::uint32_t mate_code = pair_right[right];
            if (mate_code != 0 && !reachable_left[mate_code - 1]) {
                reachable_left[mate_code - 1] = 1;
                queue.push(mate_code - 1);
            }
        }
    }

    std::uint64_t witness_left_count = 0;
    std::uint64_t witness_right_count = 0;
    std::uint64_t witness_hash = 1469598103934665603ULL;
    std::vector<std::uint32_t> witness_left_sample;
    std::vector<std::uint32_t> witness_right_sample;
    for (std::uint32_t left = 0; left < reachable_left.size(); ++left) {
        if (!reachable_left[left]) continue;
        ++witness_left_count;
        witness_hash = fnv_mix(witness_hash, outputs[left]);
        if (witness_left_sample.size() < 32) witness_left_sample.push_back(outputs[left]);
    }
    for (std::uint32_t right = 2; right < reachable_right.size(); ++right) {
        if (!reachable_right[right]) continue;
        ++witness_right_count;
        witness_hash = fnv_mix(witness_hash, right);
        if (witness_right_sample.size() < 32) witness_right_sample.push_back(right);
    }
    if (matching != outputs.size() && witness_left_count <= witness_right_count) {
        throw std::runtime_error("alternating Hall witness has no deficit");
    }

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;
    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n";
    out << "  \"schema_version\":1,\n";
    out << "  \"graph\":\"odd holes use forced seed-2 parent; hard holes use every missing endpoint\",\n";
    out << "  \"limit\":" << limit << ",\n";
    out << "  \"left_count\":" << outputs.size() << ",\n";
    out << "  \"odd_left_count\":" << odd_count << ",\n";
    out << "  \"hard_left_count\":" << hard_count << ",\n";
    out << "  \"excluded_seed3_count\":" << seed3_count << ",\n";
    out << "  \"splitless_count\":" << splitless_count << ",\n";
    out << "  \"edge_count\":" << neighbors.size() << ",\n";
    out << "  \"maximum_hard_degree\":" << maximum_degree << ",\n";
    out << "  \"matching_size\":" << matching << ",\n";
    out << "  \"perfect\":" << (matching == outputs.size() ? "true" : "false")
        << ",\n";
    out << "  \"matching_fnv1a64\":\"" << matching_hash << "\",\n";
    if (matching == outputs.size()) {
        out << "  \"hall_witness\":null,\n";
    } else {
        out << "  \"hall_witness\":{\n";
        out << "    \"left_count\":" << witness_left_count << ",\n";
        out << "    \"neighbor_count\":" << witness_right_count << ",\n";
        out << "    \"deficit\":" << witness_left_count - witness_right_count
            << ",\n";
        out << "    \"fnv1a64\":\"" << witness_hash << "\",\n";
        out << "    \"left_sample\":[";
        for (std::size_t index = 0; index < witness_left_sample.size(); ++index) {
            if (index != 0) out << ',';
            out << witness_left_sample[index];
        }
        out << "],\n    \"neighbor_sample\":[";
        for (std::size_t index = 0; index < witness_right_sample.size(); ++index) {
            if (index != 0) out << ',';
            out << witness_right_sample[index];
        }
        out << "]\n  },\n";
    }
    out << "  \"elapsed_seconds\":" << elapsed.count() << "\n";
    out << "}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit
              << " left=" << outputs.size()
              << " odd=" << odd_count
              << " hard=" << hard_count
              << " edges=" << neighbors.size()
              << " matching=" << matching
              << " deficit=" << outputs.size() - matching
              << " elapsed_seconds=" << elapsed.count() << "\n";
    return 0;
}
