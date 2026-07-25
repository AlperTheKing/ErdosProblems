#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using u64 = std::uint64_t;

static bool is_prime(u64 n) {
    if (n < 2) return false;
    for (u64 p : {2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL, 17ULL, 19ULL,
                  23ULL, 29ULL, 31ULL, 37ULL}) {
        if (n % p == 0) return n == p;
    }
    for (u64 d = 41; d * d <= n; d += 2) {
        if (n % d == 0) return false;
    }
    return true;
}

static std::vector<u64> divisors(u64 n) {
    std::vector<std::pair<u64, int>> fac;
    for (u64 p = 2; p * p <= n; ++p) {
        if (n % p != 0) continue;
        int e = 0;
        do {
            n /= p;
            ++e;
        } while (n % p == 0);
        fac.emplace_back(p, e);
    }
    if (n > 1) fac.emplace_back(n, 1);

    std::vector<u64> ds{1};
    for (auto [p, e] : fac) {
        const std::size_t old = ds.size();
        u64 q = 1;
        for (int j = 1; j <= e; ++j) {
            q *= p;
            for (std::size_t i = 0; i < old; ++i) ds.push_back(ds[i] * q);
        }
    }
    std::sort(ds.begin(), ds.end());
    return ds;
}

struct Candidate {
    u64 L;
    long double reciprocal_mass;
    std::vector<u64> moduli;
};

static Candidate inspect(u64 L) {
    Candidate c{L, 0.0L, {}};
    for (u64 d : divisors(L)) {
        if (d >= 4 && is_prime(d + 1)) {
            c.moduli.push_back(d);
            c.reciprocal_mass += 1.0L / static_cast<long double>(d);
        }
    }
    return c;
}

static bool verify_selfridge() {
    const std::vector<std::pair<int, int>> cover = {
        {0, 2}, {3, 4}, {3, 6}, {7, 10}, {5, 12}, {7, 18},
        {25, 30}, {13, 36}, {29, 40}, {13, 60}, {1, 72}, {1, 180}};
    for (int x = 0; x < 360; ++x) {
        bool hit = false;
        for (auto [a, m] : cover) {
            if (x % m == a) {
                hit = true;
                break;
            }
        }
        if (!hit) {
            std::cerr << "SELFDRIDGE_FAIL residue=" << x << "\n";
            return false;
        }
    }
    std::cout << "SELFRIDGE_VERIFIED period=360 congruences="
              << cover.size() << "\n";
    return true;
}

int main() {
    if (!verify_selfridge()) return 2;

    // Predeclared diagnostic box.  It chooses one finite production period;
    // it is not a cascade of cover searches.
    const std::vector<u64> primes = {2, 3, 5, 7, 11, 13, 17, 19};
    const std::vector<int> max_exp = {12, 8, 5, 3, 3, 2, 2, 2};
    constexpr u64 cap = 2'000'000'000ULL;
    std::vector<Candidate> feasible;

    auto rec = [&](auto&& self, std::size_t i, u64 L) -> void {
        if (i == primes.size()) {
            if (L % 360 != 0) return;
            Candidate c = inspect(L);
            if (c.reciprocal_mass >= 1.0L &&
                !c.moduli.empty() && c.moduli.back() + 1 > 877) {
                feasible.push_back(std::move(c));
            }
            return;
        }
        u64 value = L;
        for (int e = 0; e <= max_exp[i]; ++e) {
            self(self, i + 1, value);
            if (e == max_exp[i] || value > cap / primes[i]) break;
            value *= primes[i];
        }
    };
    rec(rec, 0, 1);

    std::sort(feasible.begin(), feasible.end(),
              [](const Candidate& a, const Candidate& b) {
                  if (a.L != b.L) return a.L < b.L;
                  return a.reciprocal_mass > b.reciprocal_mass;
              });

    std::cout << "FEASIBLE_PERIODS " << feasible.size() << "\n";
    const std::size_t show = std::min<std::size_t>(20, feasible.size());
    for (std::size_t i = 0; i < show; ++i) {
        const auto& c = feasible[i];
        std::cout << "CANDIDATE L=" << c.L
                  << " count=" << c.moduli.size()
                  << " reciprocal_mass=" << std::setprecision(15)
                  << static_cast<double>(c.reciprocal_mass)
                  << " max_p=" << c.moduli.back() + 1 << " moduli=";
        for (std::size_t j = 0; j < c.moduli.size(); ++j) {
            if (j) std::cout << ',';
            std::cout << c.moduli[j];
        }
        std::cout << "\n";
    }
    return feasible.empty() ? 3 : 0;
}
