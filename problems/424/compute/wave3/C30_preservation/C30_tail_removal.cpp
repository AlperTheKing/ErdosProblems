#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

bool allowed(std::uint32_t value) {
    return value >= 2 && value % 3 != 1;
}

bool hard_shape(std::uint32_t value, bool has_split) {
    if ((value & 1U) != 0 || !has_split) return false;
    if ((value + 1) % 3 != 0) return true;
    const std::uint32_t parent = (value + 1) / 3;
    return !(allowed(parent) && parent != 3);
}

struct Snapshot {
    std::uint32_t x;
    std::uint64_t hard;
    std::uint64_t q;
    std::uint64_t removable;
    std::int64_t residual;
};

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: C30_tail_removal LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const std::uint64_t parsed = std::stoull(argv[1]);
    if (parsed < 54 || parsed > 1000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [54,1000000000]");
    }
    const auto limit = static_cast<std::uint32_t>(parsed);
    const auto started = std::chrono::steady_clock::now();

    std::vector<std::uint32_t> spf(static_cast<std::size_t>(limit) + 2);
    std::iota(spf.begin(), spf.end(), 0U);
    for (std::uint32_t prime = 2;
         static_cast<std::uint64_t>(prime) * prime <=
             static_cast<std::uint64_t>(limit) + 1;
         ++prime) {
        if (spf[prime] != prime) continue;
        for (std::uint64_t multiple =
                 static_cast<std::uint64_t>(prime) * prime;
             multiple <= static_cast<std::uint64_t>(limit) + 1;
             multiple += prime) {
            if (spf[multiple] == multiple) {
                spf[multiple] = prime;
            }
        }
    }

    std::vector<std::uint8_t> member(
        static_cast<std::size_t>(limit) + 1, 0
    );
    std::vector<std::uint8_t> reducible(
        static_cast<std::size_t>(limit) + 1, 0
    );
    std::vector<std::uint8_t> hard_hole(
        static_cast<std::size_t>(limit) + 1, 0
    );
    member[2] = 1;
    member[3] = 1;
    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);

    for (std::uint32_t value = 4; value <= limit; ++value) {
        const std::uint32_t product = value + 1;
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
            if (!allowed(left) || !allowed(right)) continue;
            reducible[value] = 1;
            if (member[left] && member[right]) member[value] = 1;
        }
        if (allowed(value) && !member[value] &&
            hard_shape(value, reducible[value] != 0)) {
            hard_hole[value] = 1;
        }
    }

    std::vector<std::uint8_t> q_parent(
        static_cast<std::size_t>(limit) + 1, 0
    );
    std::vector<std::uint64_t> removable_prefix(
        static_cast<std::size_t>(limit) + 1, 0
    );
    for (std::uint32_t parent = 2; parent <= limit; ++parent) {
        const std::uint64_t child64 = 2ULL * parent - 1;
        if (child64 > limit) break;
        const auto child = static_cast<std::uint32_t>(child64);
        if (allowed(parent) && !member[parent] && member[child]) {
            q_parent[parent] = 1;
        }
    }
    for (std::uint32_t value = 1; value <= limit; ++value) {
        removable_prefix[value] = removable_prefix[value - 1];
        if (q_parent[value] && (value & 1U) == 0 && reducible[value] &&
            !hard_shape(value, true)) {
            ++removable_prefix[value];
        }
    }

    std::uint64_t hard = 0;
    std::uint64_t q = 0;
    std::int64_t minimum = std::numeric_limits<std::int64_t>::max();
    std::uint32_t minimum_x = 0;
    std::uint32_t first_failure = 0;
    std::vector<Snapshot> snapshots;
    std::uint64_t next_power = 100;
    for (std::uint32_t x = 2; x <= limit; ++x) {
        hard += hard_hole[x];
        if ((x & 1U) != 0) {
            const std::uint32_t parent = (x + 1) / 2;
            q += q_parent[parent];
        }
        const std::uint32_t half = (x + 1) / 2;
        const std::uint32_t third = (x + 1) / 3;
        const std::uint64_t removable =
            removable_prefix[half] - removable_prefix[third];
        const std::int64_t residual =
            static_cast<std::int64_t>(q) -
            static_cast<std::int64_t>(hard) -
            static_cast<std::int64_t>(removable);
        if (residual < minimum) {
            minimum = residual;
            minimum_x = x;
        }
        if (residual < 0 && first_failure == 0) first_failure = x;
        if (x == next_power || x == limit) {
            snapshots.push_back(Snapshot{x, hard, q, removable, residual});
            if (next_power <= limit / 10) next_power *= 10;
        }
    }

    std::vector<std::uint32_t> failure_parents;
    if (first_failure != 0) {
        const std::uint32_t half = (first_failure + 1) / 2;
        const std::uint32_t third = (first_failure + 1) / 3;
        for (std::uint32_t parent = third + 1; parent <= half; ++parent) {
            if (q_parent[parent] && (parent & 1U) == 0 &&
                reducible[parent] &&
                !hard_shape(parent, true)) {
                failure_parents.push_back(parent);
                if (failure_parents.size() == 64) break;
            }
        }
    }

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;
    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output");
    out << "{\n  \"schema_version\":1,\n";
    out << "  \"limit\":" << limit << ",\n";
    out << "  \"construction\":\"G plus even reducible nonhard Q-parent roots in (floor((X+1)/3),floor((X+1)/2)]\",\n";
    out << "  \"first_failure\":" << first_failure << ",\n";
    out << "  \"minimum_residual\":" << minimum << ",\n";
    out << "  \"minimum_X\":" << minimum_x << ",\n";
    out << "  \"elapsed_seconds\":" << elapsed.count() << ",\n";
    out << "  \"failure_parent_sample\":[";
    for (std::size_t i = 0; i < failure_parents.size(); ++i) {
        if (i) out << ',';
        out << failure_parents[i];
    }
    out << "],\n  \"snapshots\":[\n";
    for (std::size_t i = 0; i < snapshots.size(); ++i) {
        const auto& row = snapshots[i];
        out << "    {\"X\":" << row.x << ",\"H\":" << row.hard
            << ",\"Q\":" << row.q << ",\"R\":" << row.removable
            << ",\"Q_minus_H_minus_R\":" << row.residual << "}"
            << (i + 1 == snapshots.size() ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    std::cout << "limit=" << limit << " first_failure=" << first_failure
              << " minimum=" << minimum << " at=" << minimum_x
              << " elapsed=" << elapsed.count() << "s\n";
    return 0;
}
