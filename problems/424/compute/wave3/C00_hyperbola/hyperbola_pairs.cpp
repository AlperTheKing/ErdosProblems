#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

using u32 = std::uint32_t;
using u64 = std::uint64_t;
using u128 = unsigned __int128;

static std::string show_u128(u128 x) {
    if (x == 0) return "0";
    std::string s;
    while (x > 0) { s.push_back(char('0' + x % 10)); x /= 10; }
    std::reverse(s.begin(), s.end());
    return s;
}

static std::vector<u32> smallest_prime_factors(u32 limit) {
    std::vector<u32> spf(static_cast<std::size_t>(limit) + 1, 0);
    for (u32 p = 2; u64(p) * p <= limit; ++p) {
        if (spf[p] != 0) continue;
        for (u64 m = u64(p) * p; m <= limit; m += p) {
            if (spf[static_cast<std::size_t>(m)] == 0) spf[static_cast<std::size_t>(m)] = p;
        }
    }
    return spf;
}

static bool generated(u32 n, const std::vector<u32>& spf, const std::vector<std::uint8_t>& inG) {
    u32 value = n + 1;
    u32 remaining = value;
    std::vector<std::pair<u32,u32>> fac;
    while (remaining > 1) {
        u32 p = spf[remaining] == 0 ? remaining : spf[remaining];
        u32 e = 0;
        do { remaining /= p; ++e; } while (remaining > 1 && remaining % p == 0);
        fac.emplace_back(p,e);
    }
    const u32 root = static_cast<u32>(std::sqrt(static_cast<long double>(value)));
    std::vector<u32> divs{1};
    for (auto [p,e] : fac) {
        const std::size_t old = divs.size();
        u64 pk = 1;
        for (u32 j=1; j<=e; ++j) {
            pk *= p;
            for (std::size_t i=0; i<old; ++i) {
                u64 d = u64(divs[i]) * pk;
                if (d <= root) divs.push_back(static_cast<u32>(d));
            }
        }
    }
    for (u32 d : divs) {
        if (d < 2 || value % d != 0) continue;
        u32 q = value / d;
        if (d >= q) continue;
        if (inG[d] && inG[q]) return true;
    }
    return false;
}

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: hyperbola_pairs LIMIT OUTPUT_JSON\n";
        return 2;
    }
    const u32 B = static_cast<u32>(std::stoul(argv[1]));
    const std::string out_path = argv[2];
    const auto t0 = std::chrono::steady_clock::now();
    auto spf = smallest_prime_factors(B + 1);
    const auto t1 = std::chrono::steady_clock::now();
    std::vector<std::uint8_t> inG(static_cast<std::size_t>(B) + 1, 0);
    if (B >= 2) inG[2]=1;
    if (B >= 3) inG[3]=1;
    for (u32 n=4; n<=B; ++n) if (generated(n,spf,inG)) inG[n]=1;
    const auto t2 = std::chrono::steady_clock::now();
    std::vector<u32>().swap(spf);

    std::vector<u32> g0, g2;
    for (u32 n=1; n<=B; ++n) {
        if (!inG[n]) continue;
        if (n % 3 == 0) g0.push_back(n);
        else if (n % 3 == 2) g2.push_back(n);
    }
    std::vector<std::uint8_t>().swap(inG);

    std::vector<std::uint16_t> multiplicity(static_cast<std::size_t>(B)+1,0);
    u64 total_pairs = 0;
    for (u32 a : g0) {
        if (u64(a) * 2 > B) break;
        const u32 lim = B / a;
        auto end = std::upper_bound(g2.begin(), g2.end(), lim);
        total_pairs += static_cast<u64>(end - g2.begin());
        for (auto it=g2.begin(); it!=end; ++it) {
            const u64 p = u64(a) * (*it);
            auto &cell = multiplicity[static_cast<std::size_t>(p)];
            if (cell == std::numeric_limits<std::uint16_t>::max()) {
                std::cerr << "multiplicity overflow at " << p << "\n";
                return 3;
            }
            ++cell;
        }
    }
    const auto t3 = std::chrono::steady_clock::now();

    std::vector<u32> checkpoints;
    for (u64 x=1000; x<=B; x*=10) {
        checkpoints.push_back(static_cast<u32>(x));
        if (x > B/10) break;
    }
    if (checkpoints.empty() || checkpoints.back()!=B) checkpoints.push_back(B);

    u64 prefix_pairs=0, prefix_distinct=0;
    u128 prefix_energy=0;
    std::size_t ci=0;
    struct Row {u32 X;u64 pairs;u64 distinct;u128 energy;};
    std::vector<Row> rows;
    for (u32 n=1;n<=B;++n) {
        const u64 r=multiplicity[n];
        prefix_pairs += r;
        prefix_energy += u128(r)*r;
        if (r) ++prefix_distinct;
        while (ci<checkpoints.size() && n==checkpoints[ci]) {
            rows.push_back({n,prefix_pairs,prefix_distinct,prefix_energy});
            ++ci;
        }
    }
    const auto t4 = std::chrono::steady_clock::now();

    auto secs=[](auto a,auto b){return std::chrono::duration<double>(b-a).count();};
    std::ofstream out(out_path);
    out << "{\n  \"schema_version\": 1,\n  \"limit\": "<<B<<",\n";
    out << "  \"definitions\": \"G0=G cap 3N; G2=G cap 2(mod3); pairs=(a,b) with a in G0,b in G2,ab<=X; energy=sum_p r(p)^2\",\n";
    out << "  \"g0_count_to_limit\": "<<g0.size()<<",\n  \"g2_count_to_limit\": "<<g2.size()<<",\n";
    out << "  \"seconds\": {\"spf\": "<<secs(t0,t1)<<", \"membership\": "<<secs(t1,t2)<<", \"products\": "<<secs(t2,t3)<<", \"scan\": "<<secs(t3,t4)<<"},\n";
    out << "  \"checkpoints\": [\n";
    for (std::size_t i=0;i<rows.size();++i) {
        const auto &r=rows[i];
        long double kappa=(long double)r.energy*r.X/((long double)r.pairs*r.pairs);
        long double diag=(long double)r.energy/r.pairs;
        out << "    {\"X\": "<<r.X<<", \"pairs\": "<<r.pairs<<", \"distinct_products\": "<<r.distinct
            <<", \"energy\": \""<<show_u128(r.energy)<<"\", \"pair_density\": "<<std::setprecision(15)<<(long double)r.pairs/r.X
            <<", \"product_density\": "<<(long double)r.distinct/r.X<<", \"energy_per_pair\": "<<diag<<", \"kappa\": "<<kappa<<"}";
        out << (i+1==rows.size()?"\n":",\n");
    }
    out << "  ]\n}\n";
    std::cout << "B="<<B<<" |G0|="<<g0.size()<<" |G2|="<<g2.size()<<" pairs="<<total_pairs
              <<" distinct="<<rows.back().distinct<<" E="<<show_u128(rows.back().energy)
              <<" seconds="<<secs(t0,t4)<<"\n";
}
