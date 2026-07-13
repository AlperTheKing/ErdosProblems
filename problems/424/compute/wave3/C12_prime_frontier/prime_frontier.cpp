#include <algorithm>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

using u8 = std::uint8_t;
using u32 = std::uint32_t;
using u64 = std::uint64_t;

struct Factor {
    u32 prime;
    u32 exponent;
};

struct FrontierRow {
    u32 x;
    u32 lower;
    u32 y;
    u64 prefix_count;
    u64 interval_count;
    u64 audited_cofactors;
};

struct PrimeRow {
    u32 x;
    u64 all_primes;
    u64 eligible_primes;
    u64 generated_primes;
    u32 largest_generated_prime;
    u32 largest_generated_prime_gap;
};

static u32 integer_sqrt(u64 n) {
    u64 r = static_cast<u64>(std::sqrt(static_cast<long double>(n)));
    while ((r + 1) * (r + 1) <= n) ++r;
    while (r * r > n) --r;
    return static_cast<u32>(r);
}

static u32 integer_cuberoot(u64 n) {
    u64 r = static_cast<u64>(std::cbrt(static_cast<long double>(n)));
    while ((r + 1) * (r + 1) * (r + 1) <= n) ++r;
    while (r * r * r > n) --r;
    return static_cast<u32>(r);
}

// A zero entry at n >= 2 means that n is prime.
static std::vector<u32> smallest_prime_factors(u32 limit) {
    std::vector<u32> spf(static_cast<std::size_t>(limit) + 1, 0);
    for (u32 p = 2; u64(p) * p <= limit; ++p) {
        if (spf[p] != 0) continue;
        for (u64 m = u64(p) * p; m <= limit; m += p) {
            if (spf[static_cast<std::size_t>(m)] == 0) {
                spf[static_cast<std::size_t>(m)] = p;
            }
        }
    }
    return spf;
}

static std::vector<Factor> factorize(u32 value, const std::vector<u32>& spf) {
    std::vector<Factor> factors;
    while (value > 1) {
        const u32 p = spf[value] == 0 ? value : spf[value];
        u32 exponent = 0;
        do {
            value /= p;
            ++exponent;
        } while (value > 1 && value % p == 0);
        factors.push_back({p, exponent});
    }
    return factors;
}

static std::vector<u32> divisors_at_most(
    const std::vector<Factor>& factors,
    u32 bound
) {
    std::vector<u32> divisors{1};
    for (const Factor factor : factors) {
        const std::size_t old_size = divisors.size();
        u64 power = 1;
        for (u32 exponent = 1; exponent <= factor.exponent; ++exponent) {
            power *= factor.prime;
            for (std::size_t i = 0; i < old_size; ++i) {
                const u64 divisor = u64(divisors[i]) * power;
                if (divisor <= bound) {
                    divisors.push_back(static_cast<u32>(divisor));
                }
            }
        }
    }
    return divisors;
}

static u32 least_valid_parent(
    u32 n,
    const std::vector<u32>& spf,
    const std::vector<u8>& in_g
) {
    const u32 product = n + 1;
    const u32 root = integer_sqrt(product);
    const auto factors = factorize(product, spf);
    const auto divisors = divisors_at_most(factors, root);
    u32 best = 0;
    for (const u32 divisor : divisors) {
        if (divisor < 2 || product % divisor != 0) continue;
        const u32 quotient = product / divisor;
        if (divisor >= quotient) continue;
        if (in_g[divisor] && in_g[quotient] && (best == 0 || divisor < best)) {
            best = divisor;
        }
    }
    return best;
}

static bool is_prime_trial(u32 n) {
    if (n < 2) return false;
    if (n % 2 == 0) return n == 2;
    for (u32 divisor = 3; u64(divisor) * divisor <= n; divisor += 2) {
        if (n % divisor == 0) return false;
    }
    return true;
}

static u32 least_generated_divisor_by_factorization(
    u32 n,
    const std::vector<u32>& spf,
    const std::vector<u8>& in_g
) {
    assert(n >= 2 && in_g[n]);
    const auto factors = factorize(n, spf);
    const auto divisors = divisors_at_most(factors, n);
    u32 best = n;
    for (const u32 divisor : divisors) {
        if (divisor >= 2 && in_g[divisor] && divisor < best) best = divisor;
    }
    return best;
}

static std::vector<u32> checkpoints_through(u32 limit) {
    std::vector<u32> checkpoints;
    for (u64 x = 1'000; x <= limit; x *= 10) {
        checkpoints.push_back(static_cast<u32>(x));
        if (x > limit / 10) break;
    }
    if (limit >= 2'000'000) checkpoints.push_back(2'000'000);
    checkpoints.push_back(limit);
    std::sort(checkpoints.begin(), checkpoints.end());
    checkpoints.erase(std::unique(checkpoints.begin(), checkpoints.end()), checkpoints.end());
    return checkpoints;
}

static std::vector<PrimeRow> prime_rows(
    const std::vector<u32>& checkpoints,
    const std::vector<u32>& spf,
    const std::vector<u8>& in_g
) {
    std::vector<PrimeRow> rows;
    u64 all_primes = 0;
    u64 eligible_primes = 0;
    u64 generated_primes = 0;
    u32 previous_generated_prime = 0;
    u32 largest_generated_prime = 0;
    u32 largest_gap = 0;
    std::size_t checkpoint_index = 0;
    const u32 limit = checkpoints.back();
    for (u32 n = 2; n <= limit; ++n) {
        const bool prime = spf[n] == 0;
        if (prime) {
            ++all_primes;
            const bool eligible = n == 2 || n == 3 || n % 3 == 2;
            if (eligible) ++eligible_primes;
            if (in_g[n]) {
                assert(eligible);
                ++generated_primes;
                if (previous_generated_prime != 0) {
                    largest_gap = std::max(largest_gap, n - previous_generated_prime);
                }
                previous_generated_prime = n;
                largest_generated_prime = n;
            }
        }
        while (checkpoint_index < checkpoints.size() && n == checkpoints[checkpoint_index]) {
            rows.push_back({
                n,
                all_primes,
                eligible_primes,
                generated_primes,
                largest_generated_prime,
                largest_gap,
            });
            ++checkpoint_index;
        }
    }
    return rows;
}

struct FrontierCount {
    u64 prefix = 0;
    u64 interval = 0;
    u64 audited_cofactors = 0;
};

static FrontierCount count_frontier(
    u32 x,
    u32 lower,
    u32 y,
    const std::vector<u32>& generated_primes,
    const std::vector<u32>& spf,
    const std::vector<u8>& in_g,
    const std::vector<u32>& ell,
    std::vector<u8>& audited_q,
    bool audit_injectivity
) {
    FrontierCount result;
    std::vector<u8> seen;
    if (audit_injectivity) seen.assign(static_cast<std::size_t>(x) + 1, 0);

    for (const u32 p : generated_primes) {
        if (p <= y) continue;
        if (u64(p) * p > u64(x) + 1) break;
        assert(spf[p] == 0);
        assert(is_prime_trial(p));
        assert(in_g[p]);

        const u32 q_max = static_cast<u32>((u64(x) + 1) / p);
        assert(q_max < ell.size());
        for (u32 q = p + 1; q <= q_max; ++q) {
            if (!in_g[q] || ell[q] < p) continue;
            const u64 product = u64(p) * q;
            assert(product <= u64(x) + 1);
            assert(ell[q] >= p);
            assert(ell[q] >= 2 && in_g[ell[q]] && q % ell[q] == 0);

            if (!audited_q[q]) {
                const u32 independent = least_generated_divisor_by_factorization(q, spf, in_g);
                assert(independent == ell[q]);
                audited_q[q] = 1;
                ++result.audited_cofactors;
            }

            ++result.prefix;
            const u32 output = static_cast<u32>(product - 1);
            assert(in_g[output]);
            if (output > lower) ++result.interval;
            if (audit_injectivity) {
                assert(!seen[output]);
                seen[output] = 1;
            }
        }
    }
    return result;
}

static void write_json(
    const std::string& output_path,
    u32 limit,
    u32 member_count,
    double sieve_seconds,
    double membership_seconds,
    double ell_seconds,
    double frontier_seconds,
    const std::vector<PrimeRow>& prime_stats,
    const std::vector<FrontierRow>& cube_rows,
    const std::vector<FrontierRow>& log_rows,
    const std::vector<std::pair<u32, u64>>& witness_counts,
    const std::vector<u32>& first_missing_eligible,
    u64 independently_audited_frontier_primes,
    u64 independently_audited_cofactors,
    u64 injectivity_audited_outputs,
    bool factor_641_in_g,
    bool factor_6700417_in_g
) {
    std::ofstream out(output_path);
    if (!out) throw std::runtime_error("cannot open output file");
    out << "{\n";
    out << "  \"schema_version\": 1,\n";
    out << "  \"limit\": " << limit << ",\n";
    out << "  \"member_count\": " << member_count << ",\n";
    out << "  \"definitions\": \"ordinary prime means prime in Z; ell(q)=min{d in G:d|q}; F uses Y<p<q, p ordinary prime in G, p<=ell(q), pq<=X+1\",\n";
    out << "  \"seconds\": {\"sieve\": " << sieve_seconds
        << ", \"membership\": " << membership_seconds
        << ", \"least_generated_divisors\": " << ell_seconds
        << ", \"frontiers\": " << frontier_seconds << "},\n";
    out << "  \"audits\": {\"trial_divided_frontier_primes\": "
        << independently_audited_frontier_primes
        << ", \"factorized_frontier_cofactors\": " << independently_audited_cofactors
        << ", \"injectivity_checked_outputs_at_limit_for_cuberoot_frontier\": "
        << injectivity_audited_outputs << "},\n";

    out << "  \"prime_checkpoints\": [\n";
    for (std::size_t i = 0; i < prime_stats.size(); ++i) {
        const auto& row = prime_stats[i];
        out << "    {\"X\": " << row.x
            << ", \"all_ordinary_primes\": " << row.all_primes
            << ", \"eligible_primes_2_3_or_2mod3\": " << row.eligible_primes
            << ", \"generated_ordinary_primes\": " << row.generated_primes
            << ", \"largest_generated_prime\": " << row.largest_generated_prime
            << ", \"largest_generated_prime_gap\": " << row.largest_generated_prime_gap
            << "}" << (i + 1 == prime_stats.size() ? "\n" : ",\n");
    }
    out << "  ],\n";

    auto write_frontiers = [&out](const char* name, const std::vector<FrontierRow>& rows) {
        out << "  \"" << name << "\": [\n";
        for (std::size_t i = 0; i < rows.size(); ++i) {
            const auto& row = rows[i];
            out << "    {\"X\": " << row.x
                << ", \"interval_lower_exclusive\": " << row.lower
                << ", \"Y\": " << row.y
                << ", \"F_prefix\": " << row.prefix_count
                << ", \"F_interval\": " << row.interval_count
                << ", \"new_independently_audited_cofactors\": " << row.audited_cofactors
                << "}" << (i + 1 == rows.size() ? "\n" : ",\n");
        }
        out << "  ],\n";
    };
    write_frontiers("frontier_Y_floor_cuberoot_X", cube_rows);
    write_frontiers("frontier_Y_floor_log_X", log_rows);

    out << "  \"least_parent_counts_for_generated_primes\": [\n";
    for (std::size_t i = 0; i < witness_counts.size(); ++i) {
        out << "    {\"least_parent\": " << witness_counts[i].first
            << ", \"count\": " << witness_counts[i].second << "}"
            << (i + 1 == witness_counts.size() ? "\n" : ",\n");
    }
    out << "  ],\n";

    out << "  \"first_missing_eligible_primes\": [";
    for (std::size_t i = 0; i < first_missing_eligible.size(); ++i) {
        if (i) out << ", ";
        out << first_missing_eligible[i];
    }
    out << "],\n";
    out << "  \"fermat_F5_audit\": {\"F5\": 4294967297, \"factorization\": \"641*6700417\", "
        << "\"641_in_G\": " << (factor_641_in_g ? "true" : "false")
        << ", \"6700417_in_G\": " << (factor_6700417_in_g ? "true" : "false") << "}\n";
    out << "}\n";
}

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: prime_frontier LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const u64 parsed_limit = std::stoull(argv[1]);
    if (parsed_limit < 10'000 || parsed_limit >= std::numeric_limits<u32>::max()) {
        std::cerr << "LIMIT must lie in [10000, 2^32-2]\n";
        return 2;
    }
    const u32 limit = static_cast<u32>(parsed_limit);
    const std::string output_path = argv[2];
    const auto checkpoints = checkpoints_through(limit);

    const auto t0 = std::chrono::steady_clock::now();
    auto spf = smallest_prime_factors(limit + 1);
    const auto t1 = std::chrono::steady_clock::now();

    std::vector<u8> in_g(static_cast<std::size_t>(limit) + 1, 0);
    in_g[2] = 1;
    in_g[3] = 1;
    std::vector<u32> generated_primes;
    generated_primes.push_back(2);
    generated_primes.push_back(3);
    std::vector<std::pair<u32, u64>> witness_counts;
    std::vector<u64> witness_histogram(integer_sqrt(u64(limit) + 1) + 1, 0);
    u32 member_count = 2;
    for (u32 n = 4; n <= limit; ++n) {
        const u32 witness = least_valid_parent(n, spf, in_g);
        if (witness == 0) continue;
        in_g[n] = 1;
        ++member_count;
        if (spf[n] == 0) {
            generated_primes.push_back(n);
            ++witness_histogram[witness];
        }
    }
    const auto t2 = std::chrono::steady_clock::now();

    // Trial division is an independent primality audit for every p that can
    // occur in F(X,Y), namely p <= sqrt(limit+1).
    const u32 frontier_prime_limit = integer_sqrt(u64(limit) + 1);
    u64 audited_frontier_primes = 0;
    for (const u32 p : generated_primes) {
        if (p > frontier_prime_limit) break;
        assert(is_prime_trial(p));
        assert(spf[p] == 0);
        ++audited_frontier_primes;
    }

    const std::vector<u32> accepted_counts_x{10, 100, 1'000, 10'000, 100'000, 1'000'000, 10'000'000, 100'000'000};
    const std::vector<u32> accepted_counts_g{4, 23, 250, 3'207, 39'843, 457'599, 4'952'270, 51'899'129};
    u32 exact_prefix_count = 0;
    std::size_t accepted_index = 0;
    for (u32 n = 0; n <= limit && accepted_index < accepted_counts_x.size(); ++n) {
        exact_prefix_count += in_g[n];
        if (n == accepted_counts_x[accepted_index]) {
            assert(exact_prefix_count == accepted_counts_g[accepted_index]);
            ++accepted_index;
        }
    }
    assert(!in_g[8] && !in_g[24]);

    for (u32 witness = 2; witness < witness_histogram.size(); ++witness) {
        if (witness_histogram[witness]) witness_counts.push_back({witness, witness_histogram[witness]});
    }

    const auto p_rows = prime_rows(checkpoints, spf, in_g);
    std::vector<u32> first_missing_eligible;
    for (u32 p = 2; p <= limit && first_missing_eligible.size() < 20; ++p) {
        if (spf[p] == 0 && (p == 2 || p == 3 || p % 3 == 2) && !in_g[p]) {
            first_missing_eligible.push_back(p);
        }
    }

    u32 global_min_y = std::numeric_limits<u32>::max();
    for (const u32 x : checkpoints) {
        global_min_y = std::min(global_min_y, integer_cuberoot(x));
        global_min_y = std::min(global_min_y, static_cast<u32>(std::floor(std::log(static_cast<long double>(x)))));
    }
    const u32 ell_limit = static_cast<u32>((u64(limit) + 1) / (global_min_y + 1));
    std::vector<u32> ell(static_cast<std::size_t>(ell_limit) + 1, 0);
    for (u32 divisor = 2; divisor <= ell_limit; ++divisor) {
        if (!in_g[divisor]) continue;
        for (u32 multiple = divisor; multiple <= ell_limit; multiple += divisor) {
            if (ell[multiple] == 0) ell[multiple] = divisor;
            if (multiple > ell_limit - divisor) break;
        }
    }
    for (u32 q = 2; q <= ell_limit; ++q) {
        if (in_g[q]) assert(ell[q] >= 2 && in_g[ell[q]] && q % ell[q] == 0);
    }
    const auto t3 = std::chrono::steady_clock::now();

    std::vector<u8> audited_q(static_cast<std::size_t>(ell_limit) + 1, 0);
    std::vector<FrontierRow> cube_rows;
    std::vector<FrontierRow> log_rows;
    for (const u32 x : checkpoints) {
        u32 lower = 0;
        if (x == 2'000'000) {
            lower = 1'000'000;
        } else if (x >= 10'000 && x % 10 == 0) {
            lower = x / 10;
        }
        const u32 y_cube = integer_cuberoot(x);
        const auto cube = count_frontier(
            x, lower, y_cube, generated_primes, spf, in_g, ell, audited_q, x == limit
        );
        cube_rows.push_back({x, lower, y_cube, cube.prefix, cube.interval, cube.audited_cofactors});

        const u32 y_log = static_cast<u32>(std::floor(std::log(static_cast<long double>(x))));
        const auto logarithmic = count_frontier(
            x, lower, y_log, generated_primes, spf, in_g, ell, audited_q, false
        );
        log_rows.push_back({x, lower, y_log, logarithmic.prefix, logarithmic.interval, logarithmic.audited_cofactors});
    }
    const auto t4 = std::chrono::steady_clock::now();

    const bool factor_641_in_g = limit >= 641 && in_g[641];
    const bool factor_6700417_in_g = limit >= 6'700'417 && in_g[6'700'417];
    assert(u64(641) * 6'700'417 == 4'294'967'297ULL);
    if (limit >= 6'700'417) {
        assert(is_prime_trial(641));
        assert(is_prime_trial(6'700'417));
    }

    auto seconds = [](auto begin, auto end) {
        return std::chrono::duration<double>(end - begin).count();
    };
    write_json(
        output_path,
        limit,
        member_count,
        seconds(t0, t1),
        seconds(t1, t2),
        seconds(t2, t3),
        seconds(t3, t4),
        p_rows,
        cube_rows,
        log_rows,
        witness_counts,
        first_missing_eligible,
        audited_frontier_primes,
        static_cast<u64>(std::count(audited_q.begin(), audited_q.end(), u8{1})),
        cube_rows.back().prefix_count,
        factor_641_in_g,
        factor_6700417_in_g
    );

    std::cout << "limit=" << limit
        << " members=" << member_count
        << " generated_primes=" << generated_primes.size()
        << " ell_limit=" << ell_limit
        << " audited_q=" << std::count(audited_q.begin(), audited_q.end(), u8{1})
        << " seconds=" << seconds(t0, t4) << "\n";
    return 0;
}
