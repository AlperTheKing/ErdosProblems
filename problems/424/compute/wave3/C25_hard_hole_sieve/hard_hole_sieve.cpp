#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

enum class HoleType : std::uint8_t {
    none,
    splitless,
    odd0,
    odd2,
    seed3,
    hard0,
    hard2,
};

bool allowed(std::uint32_t n) {
    return n >= 2 && n % 3 != 1;
}

struct Audit {
    std::uint64_t source_events = 0;
    std::uint64_t failure_events = 0;
    std::uint32_t first_failure = 0;
    std::uint64_t source_at_first_failure = 0;
    std::uint64_t capacity_at_first_failure = 0;
    std::int64_t maximum_excess = std::numeric_limits<std::int64_t>::min();
    std::uint32_t maximum_excess_x = 0;
    std::uint64_t source_at_max = 0;
    std::uint64_t capacity_at_max = 0;

    void observe(std::uint32_t x, std::uint64_t source, std::uint64_t capacity) {
        ++source_events;
        const auto excess = static_cast<std::int64_t>(source) -
                            static_cast<std::int64_t>(capacity);
        if (excess > 0) {
            ++failure_events;
            if (first_failure == 0) {
                first_failure = x;
                source_at_first_failure = source;
                capacity_at_first_failure = capacity;
            }
        }
        if (excess > maximum_excess) {
            maximum_excess = excess;
            maximum_excess_x = x;
            source_at_max = source;
            capacity_at_max = capacity;
        }
    }
};

struct Checkpoint {
    std::uint32_t x;
    std::uint64_t missing0;
    std::uint64_t missing2;
    std::uint64_t splitless;
    std::uint64_t odd0;
    std::uint64_t odd2;
    std::uint64_t seed3;
    std::uint64_t hard0;
    std::uint64_t hard2;
    std::uint64_t residual0;
    std::uint64_t residual2;
    std::uint64_t capacity0;
    std::uint64_t capacity2;
};

constexpr std::array<std::uint32_t, 5> d2 = {5, 17, 41, 53, 77};
constexpr std::array<std::uint32_t, 2> d0 = {33, 69};
constexpr std::array<std::uint32_t, 7> priority = {
    5, 17, 33, 41, 53, 69, 77
};

bool in_d2(std::uint32_t d) {
    return std::find(d2.begin(), d2.end(), d) != d2.end();
}

bool in_d0(std::uint32_t d) {
    return std::find(d0.begin(), d0.end(), d) != d0.end();
}

void write_list(std::ostream& out, const auto& values) {
    out << '[';
    bool first = true;
    for (const auto value : values) {
        if (!first) out << ',';
        first = false;
        out << value;
    }
    out << ']';
}

void write_audit(std::ostream& out, const Audit& audit) {
    out << "{\"source_events\":" << audit.source_events
        << ",\"failure_events\":" << audit.failure_events
        << ",\"first_failure\":" << audit.first_failure
        << ",\"source_at_first_failure\":"
        << audit.source_at_first_failure
        << ",\"capacity_at_first_failure\":"
        << audit.capacity_at_first_failure
        << ",\"maximum_excess\":" << audit.maximum_excess
        << ",\"maximum_excess_X\":" << audit.maximum_excess_x
        << ",\"source_at_max\":" << audit.source_at_max
        << ",\"capacity_at_max\":" << audit.capacity_at_max << '}';
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: hard_hole_sieve LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const auto parsed = std::stoull(argv[1]);
    if (parsed < 100 || parsed > 1000000000ULL) {
        throw std::runtime_error("LIMIT must lie in [100,1000000000]");
    }
    const auto limit = static_cast<std::uint32_t>(parsed);
    const auto started = std::chrono::steady_clock::now();

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

    std::vector<std::uint8_t> member(static_cast<std::size_t>(limit) + 1);
    std::vector<HoleType> type(static_cast<std::size_t>(limit) + 1);
    member[2] = 1;
    member[3] = 1;
    std::vector<std::uint32_t> divisors;
    divisors.reserve(2048);

    for (std::uint32_t n = 4; n <= limit; ++n) {
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

        bool has_split = false;
        for (const auto left : divisors) {
            if (left < 2) continue;
            const auto right = product / left;
            if (left >= right) continue;
            if (!allowed(left) || !allowed(right)) continue;
            has_split = true;
            if (member[left] && member[right]) member[n] = 1;
        }

        if (!allowed(n) || member[n]) continue;
        if (!has_split) {
            type[n] = HoleType::splitless;
        } else if ((n & 1U) != 0) {
            type[n] = n % 3 == 0 ? HoleType::odd0 : HoleType::odd2;
        } else {
            const auto parent = (n + 1) / 3;
            if ((n + 1) % 3 == 0 && allowed(parent) && parent != 3) {
                if (member[parent]) {
                    throw std::runtime_error("seed-3 parent must be missing");
                }
                type[n] = HoleType::seed3;
            } else if (n % 3 == 0) {
                type[n] = HoleType::hard0;
            } else {
                if (n % 18 != 2) {
                    throw std::runtime_error("hard2 residue assertion failed");
                }
                type[n] = HoleType::hard2;
            }
        }
    }

    for (const auto d : priority) {
        if (d > limit || !member[d] || (d & 1U) == 0) {
            throw std::runtime_error("selected multiplier is not generated odd");
        }
        if (in_d2(d) && d % 3 != 2) {
            throw std::runtime_error("bad d2 multiplier");
        }
        if (in_d0(d) && d % 9 != 6) {
            throw std::runtime_error("bad d0 multiplier");
        }
    }

    std::vector<std::uint32_t> odd0_prefix(
        static_cast<std::size_t>(limit) + 1
    );
    std::vector<std::uint32_t> odd2_prefix(
        static_cast<std::size_t>(limit) + 1
    );
    for (std::uint32_t n = 2; n <= limit; ++n) {
        odd0_prefix[n] = odd0_prefix[n - 1] +
                         (type[n] == HoleType::odd0 ? 1U : 0U);
        odd2_prefix[n] = odd2_prefix[n - 1] +
                         (type[n] == HoleType::odd2 ? 1U : 0U);
    }

    const auto cap0 = [&](std::uint32_t x) {
        std::uint64_t result = 0;
        for (const auto d : d2) result += odd2_prefix[(x + 1) / d];
        return result;
    };
    const auto cap2 = [&](std::uint32_t x) {
        std::uint64_t result = 0;
        for (const auto d : d2) result += odd0_prefix[(x + 1) / d];
        for (const auto d : d0) result += odd2_prefix[(x + 1) / d];
        return result;
    };

    std::vector<std::uint32_t> checkpoint_values;
    for (std::uint64_t x = 100; x <= limit; x *= 10) {
        checkpoint_values.push_back(static_cast<std::uint32_t>(x));
        if (x > limit / 10) break;
    }
    if (checkpoint_values.empty() || checkpoint_values.back() != limit) {
        checkpoint_values.push_back(limit);
    }
    std::size_t next_checkpoint = 0;
    std::vector<Checkpoint> checkpoints;

    std::uint64_t missing0 = 0;
    std::uint64_t missing2 = 0;
    std::uint64_t splitless = 0;
    std::uint64_t odd0 = 0;
    std::uint64_t odd2 = 0;
    std::uint64_t seed3 = 0;
    std::uint64_t hard0 = 0;
    std::uint64_t hard2 = 0;
    std::uint64_t residual0 = 0;
    std::uint64_t residual2 = 0;
    std::uint64_t forced11 = 0;
    std::uint64_t forced11_residual = 0;
    std::map<std::uint32_t, std::uint64_t> assigned0;
    std::map<std::uint32_t, std::uint64_t> assigned2;
    Audit recurrence0;
    Audit recurrence2;
    Audit combined;

    for (std::uint32_t n = 2; n <= limit; ++n) {
        if (allowed(n) && !member[n]) {
            if (n % 3 == 0) {
                ++missing0;
            } else {
                ++missing2;
            }
        }
        switch (type[n]) {
            case HoleType::splitless: ++splitless; break;
            case HoleType::odd0: ++odd0; break;
            case HoleType::odd2: ++odd2; break;
            case HoleType::seed3: ++seed3; break;
            case HoleType::hard0: {
                ++hard0;
                bool handled = false;
                for (const auto d : d2) {
                    if ((n + 1) % d != 0) continue;
                    const auto parent = (n + 1) / d;
                    if (parent == d) continue;
                    if (type[parent] != HoleType::odd2) {
                        throw std::runtime_error("hard0 channel type failed");
                    }
                    ++assigned0[d];
                    handled = true;
                    break;
                }
                if (!handled) ++residual0;
                if ((n + 1) % 11 == 0) {
                    const auto p = (n + 1) / 11;
                    if (p >= 5 && p != 11 && spf[p] == p && member[p]) {
                        ++forced11;
                        if (!handled) ++forced11_residual;
                    }
                }
                recurrence0.observe(n, hard0, cap0(n));
                combined.observe(n, hard0 + hard2, cap0(n) + cap2(n));
                break;
            }
            case HoleType::hard2: {
                ++hard2;
                bool handled = false;
                for (const auto d : priority) {
                    if ((n + 1) % d != 0) continue;
                    const auto parent = (n + 1) / d;
                    if (parent == d) continue;
                    const auto expected = in_d2(d) ? HoleType::odd0
                                                   : HoleType::odd2;
                    if (type[parent] != expected) {
                        throw std::runtime_error("hard2 channel type failed");
                    }
                    ++assigned2[d];
                    handled = true;
                    break;
                }
                if (!handled) ++residual2;
                recurrence2.observe(n, hard2, cap2(n));
                combined.observe(n, hard0 + hard2, cap0(n) + cap2(n));
                break;
            }
            case HoleType::none: break;
        }

        if (next_checkpoint < checkpoint_values.size() &&
            n == checkpoint_values[next_checkpoint]) {
            checkpoints.push_back(Checkpoint{
                n, missing0, missing2, splitless, odd0, odd2, seed3,
                hard0, hard2, residual0, residual2, cap0(n), cap2(n)
            });
            ++next_checkpoint;
        }
    }

    if (missing0 + missing2 !=
        splitless + odd0 + odd2 + seed3 + hard0 + hard2) {
        throw std::runtime_error("hole partition assertion failed");
    }

    std::vector<std::uint32_t> primitive_eligible;
    const auto multiplier_cap = std::min<std::uint32_t>(limit, 10000);
    for (std::uint32_t d = 5; d <= multiplier_cap; d += 2) {
        if (!member[d] || !(d % 3 == 2 || d % 9 == 6)) continue;
        bool dominated = false;
        for (const auto e : primitive_eligible) {
            if (d % e == 0) {
                dominated = true;
                break;
            }
        }
        if (!dominated) primitive_eligible.push_back(d);
    }

    long double a = 0;
    long double b = 0;
    for (const auto d : d2) a += 1.0L / d;
    for (const auto d : d0) b += 1.0L / d;
    const long double gate = 3 - 10 * a + 3 * a * a - 3 * b;
    const long double trace = 1.0L / 3 + a;
    const long double determinant =
        (a / 2) * (1.0L / 3 + a / 2) -
        0.5L * (5.0L / 6 + b / 2);
    const long double rho =
        (trace + std::sqrt(trace * trace - 4 * determinant)) / 2;

    const auto stopped = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = stopped - started;
    std::ofstream out(argv[2]);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << std::setprecision(18);
    out << "{\n  \"schema_version\":1,\n";
    out << "  \"limit\":" << limit << ",\n";
    out << "  \"multipliers\":{\"D2\":";
    write_list(out, d2);
    out << ",\"D0\":";
    write_list(out, d0);
    out << ",\"priority\":";
    write_list(out, priority);
    out << ",\"primitive_eligible_through_" << multiplier_cap
        << "\":{\"count\":" << primitive_eligible.size() << ",\"first\":[";
    for (std::size_t i = 0;
         i < std::min<std::size_t>(primitive_eligible.size(), 64);
         ++i) {
        if (i != 0) out << ',';
        out << primitive_eligible[i];
    }
    out << "]}";
    out << "},\n";
    out << "  \"spectral\":{\"a\":" << a << ",\"b\":" << b
        << ",\"gate\":" << gate << ",\"rho\":" << rho << "},\n";
    out << "  \"counts\":{\"M0\":" << missing0 << ",\"M2\":" << missing2
        << ",\"E\":" << splitless << ",\"O0\":" << odd0
        << ",\"O2\":" << odd2 << ",\"S\":" << seed3
        << ",\"H0\":" << hard0 << ",\"H2\":" << hard2
        << ",\"H\":" << hard0 + hard2 << "},\n";
    out << "  \"sieve\":{\"residual0\":" << residual0
        << ",\"residual2\":" << residual2
        << ",\"forced11\":" << forced11
        << ",\"forced11_residual\":" << forced11_residual
        << ",\"assigned0\":{";
    bool first = true;
    for (const auto& [d, count] : assigned0) {
        if (!first) out << ',';
        first = false;
        out << '\"' << d << "\":" << count;
    }
    out << "},\"assigned2\":{";
    first = true;
    for (const auto& [d, count] : assigned2) {
        if (!first) out << ',';
        first = false;
        out << '\"' << d << "\":" << count;
    }
    out << "}},\n";
    out << "  \"recurrences\":{\"H0_le_D2O2\":";
    write_audit(out, recurrence0);
    out << ",\"H2_le_D2O0_plus_D0O2\":";
    write_audit(out, recurrence2);
    out << ",\"combined\":";
    write_audit(out, combined);
    out << "},\n  \"checkpoints\":[\n";
    for (std::size_t i = 0; i < checkpoints.size(); ++i) {
        const auto& c = checkpoints[i];
        out << "    {\"X\":" << c.x << ",\"M0\":" << c.missing0
            << ",\"M2\":" << c.missing2 << ",\"E\":" << c.splitless
            << ",\"O0\":" << c.odd0 << ",\"O2\":" << c.odd2
            << ",\"S\":" << c.seed3 << ",\"H0\":" << c.hard0
            << ",\"H2\":" << c.hard2
            << ",\"residual0\":" << c.residual0
            << ",\"residual2\":" << c.residual2
            << ",\"capacity0\":" << c.capacity0
            << ",\"capacity2\":" << c.capacity2 << "}"
            << (i + 1 == checkpoints.size() ? "\n" : ",\n");
    }
    out << "  ],\n  \"elapsed_seconds\":" << elapsed.count() << "\n}\n";
    if (!out) throw std::runtime_error("could not write output JSON");

    std::cout << "limit=" << limit << " H=" << hard0 + hard2
              << " residual=" << residual0 + residual2
              << " first_combined_failure=" << combined.first_failure
              << " max_combined_excess=" << combined.maximum_excess
              << " rho=" << static_cast<double>(rho)
              << " elapsed_seconds=" << elapsed.count() << '\n';
    return 0;
}
