#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <string>
#include <thread>
#include <utility>
#include <vector>

using ld = long double;

struct Sample {
    std::string name;
    ld alpha; // x = cos(pi alpha)
};

struct Row {
    std::string name;
    int level;
    int n;
    ld phase;
    ld deficit25;
    ld deficit50;
    ld deficit100;
    ld logL;
    ld thresholdMinusL;
    ld auditError;
};

static ld hp_deficit(std::vector<ld> logs, ld beta) {
    std::sort(logs.begin(), logs.end(), std::greater<ld>());
    const int m = std::max(1, static_cast<int>(std::floor(beta * logs.size())));
    const ld a = 2.0L / acosl(-1.0L);
    ld ans = 0;
    for (int r = 1; r <= m; ++r) {
        const ld target = a / static_cast<ld>(r);
        const ld lt = logl(target);
        if (logs[r - 1] < lt) {
            ans += target - expl(logs[r - 1]);
        }
    }
    return ans;
}

static ld log_sum_exp(const std::vector<ld>& logs) {
    const ld mx = *std::max_element(logs.begin(), logs.end());
    ld sum = 0;
    for (ld z : logs) sum += expl(z - mx);
    return mx + logl(sum);
}

static ld direct_log_weight(const std::vector<ld>& nodes, ld x, int k) {
    ld ans = 0;
    for (int i = 0; i < static_cast<int>(nodes.size()); ++i) {
        if (i == k) continue;
        ans += logl(fabsl(x - nodes[i])) - logl(fabsl(nodes[k] - nodes[i]));
    }
    return ans;
}

static std::vector<Row> evaluate(const Sample& sample, int maxLevel) {
    const ld pi = acosl(-1.0L);
    const ld x = cosl(pi * sample.alpha);
    std::vector<ld> nodes;
    std::vector<ld> logs;
    std::vector<Row> rows;

    auto append_node = [&](ld y) {
        if (nodes.empty()) {
            nodes.push_back(y);
            logs.push_back(0);
            return;
        }
        ld newLog = 0;
        for (ld z : nodes) {
            newLog += logl(fabsl(x - z)) - logl(fabsl(y - z));
        }
        const ld numUpdate = logl(fabsl(x - y));
        for (int k = 0; k < static_cast<int>(nodes.size()); ++k) {
            logs[k] += numUpdate - logl(fabsl(nodes[k] - y));
        }
        nodes.push_back(y);
        logs.push_back(newLog);
    };

    append_node(1.0L);
    append_node(-1.0L);

    for (int level = 1; level <= maxLevel; ++level) {
        const int N = 1 << level;
        for (int k = 1; k < N; k += 2) {
            append_node(cosl(pi * static_cast<ld>(k) / static_cast<ld>(N)));
        }

        ld audit = 0;
        if (level <= 7) {
            for (int k = 0; k < static_cast<int>(nodes.size()); ++k) {
                audit = std::max(audit, fabsl(logs[k] - direct_log_weight(nodes, x, k)));
            }
        }

        const ld logL = log_sum_exp(logs);
        const ld threshold = (2.0L / pi) * logl(static_cast<ld>(nodes.size()));
        ld thresholdMinusL;
        if (logL > 40) {
            thresholdMinusL = -std::numeric_limits<ld>::infinity();
        } else {
            thresholdMinusL = threshold - expl(logL);
        }
        const ld frac = fmodl(ldexpl(sample.alpha, level), 1.0L);
        rows.push_back(Row{
            sample.name,
            level,
            static_cast<int>(nodes.size()),
            fabsl(sinl(pi * frac)),
            hp_deficit(logs, 0.25L),
            hp_deficit(logs, 0.50L),
            hp_deficit(logs, 1.00L),
            logL,
            thresholdMinusL,
            audit
        });
    }
    return rows;
}

int main(int argc, char** argv) {
    int maxLevel = 12;
    int workerCount = 4;
    if (argc >= 2) maxLevel = std::atoi(argv[1]);
    if (argc >= 3) workerCount = std::atoi(argv[2]);
    if (maxLevel < 2 || maxLevel > 15 || workerCount < 1 || workerCount > 16) {
        std::cerr << "usage: hp_dyadic_scan [maxLevel 2..15] [workers 1..16]\n";
        return 2;
    }

    const ld sqrt2minus1 = sqrtl(2.0L) - 1.0L;
    const ld goldenConjugate = (sqrtl(5.0L) - 1.0L) / 2.0L;
    // A finite numerical proxy for alpha=sum_s 2^(-(m_s+1)),
    // m_s=4,12,28,50.  It has phase extremely close to 1/2 at levels 4 and 12.
    const ld forced =
        ldexpl(1.0L, -5) + ldexpl(1.0L, -13) +
        ldexpl(1.0L, -29) + ldexpl(1.0L, -51);

    const std::vector<Sample> samples{
        {"one_third", 1.0L / 3.0L},
        {"sqrt2_minus_1", sqrt2minus1},
        {"golden_conjugate", goldenConjugate},
        {"forced_binary", forced},
        {"pi_fraction", acosl(-1.0L) / 10.0L},
        {"e_fraction", expl(1.0L) / 10.0L}
    };

    std::vector<Row> all;
    std::mutex resultMutex;
    std::mutex indexMutex;
    std::size_t next = 0;
    auto worker = [&]() {
        while (true) {
            std::size_t i;
            {
                std::lock_guard<std::mutex> lock(indexMutex);
                if (next >= samples.size()) return;
                i = next++;
            }
            auto rows = evaluate(samples[i], maxLevel);
            std::lock_guard<std::mutex> lock(resultMutex);
            all.insert(all.end(), rows.begin(), rows.end());
        }
    };

    const int actualWorkers = std::min<int>(workerCount, samples.size());
    std::vector<std::thread> threads;
    for (int i = 0; i < actualWorkers; ++i) threads.emplace_back(worker);
    for (auto& t : threads) t.join();

    std::sort(all.begin(), all.end(), [](const Row& a, const Row& b) {
        if (a.name != b.name) return a.name < b.name;
        return a.level < b.level;
    });

    std::cout << std::setprecision(12);
    std::cout << "sample,level,n,abs_sin_phase,deficit25,deficit50,deficit100,"
                 "logL,threshold_minus_L,audit_max_log_error\n";
    for (const Row& r : all) {
        std::cout << r.name << ',' << r.level << ',' << r.n << ','
                  << static_cast<double>(r.phase) << ','
                  << static_cast<double>(r.deficit25) << ','
                  << static_cast<double>(r.deficit50) << ','
                  << static_cast<double>(r.deficit100) << ','
                  << static_cast<double>(r.logL) << ','
                  << static_cast<double>(r.thresholdMinusL) << ','
                  << static_cast<double>(r.auditError) << '\n';
    }
    return 0;
}
